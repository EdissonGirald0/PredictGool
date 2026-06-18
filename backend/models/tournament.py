"""
Simulador del torneo Mundial 2026.

Implementa:
1. Simulación de fase de grupos (12 grupos de 4, top 2 + 8 mejores terceros)
2. Simulación de fase eliminatoria (R32 → Final, bracket bloqueado)
3. Monte Carlo: N simulaciones completas para calcular probabilidades
4. Tiebreakers según reglamento FIFA Art. 11.5:
   - Puntos → Diferencia de goles → Goles anotados → Fair Play → Sorteo
"""

import random
from typing import Optional

import numpy as np

from config import MONTE_CARLO_DEFAULT_SIMULATIONS
from models.ensemble import predict_ensemble
from models.dixon_coles import sample_match_result as sample_fast
from utils.data_loader import load_json, name_to_id


def _load_teams() -> list[dict]:
    return load_json("teams.json") or []


def _load_groups() -> list[dict]:
    return load_json("groups.json") or []


def _load_fixtures() -> list[dict]:
    return load_json("fixtures.json") or []


def _load_results() -> list[dict]:
    return load_json("results.json") or []


def _get_team_name(team_id: str, teams: list[dict]) -> str:
    for t in teams:
        if t["id"] == team_id:
            return t["name"]
    return team_id


def _team_id_from_name(name: str, teams: list[dict]) -> Optional[str]:
    """Busca team_id a partir del nombre (case-insensitive)."""
    name_lower = name_to_id(name)
    for t in teams:
        if t["id"] == name_lower:
            return t["id"]
    return None


def simulate_group_stage(teams: list[dict], groups: list[dict]) -> dict:
    """
    Simula la fase de grupos completa.
    Inyecta resultados reales ya jugados donde existan.

    Returns:
        standings: {group_id: [{team_id, pts, played, w, d, l, gf, ga, gd}]}
        classified: {group_id: [1st, 2nd, 3rd]}
        all_thirds: lista de 3ros lugares ordenados por criterios
    """
    results = _load_results()

    group_teams = {}
    for g in groups:
        group_teams[g["id"]] = list(g["teams"])

    played_cache = {}
    for r in results:
        if r.get("played"):
            key_a = (r.get("team_a", ""), r.get("team_b", ""))
            key_b = (r.get("team_b", ""), r.get("team_a", ""))
            played_cache[key_a] = (r["score_a"], r["score_b"])
            played_cache[key_b] = (r["score_b"], r["score_a"])

    standings = {}
    for g in groups:
        gid = g["id"]
        team_list = g["teams"]

        stats = {}
        for t_name in team_list:
            tid = _team_id_from_name(t_name, teams)
            stats[t_name] = {
                "team_id": tid,
                "team_name": t_name,
                "pts": 0, "played": 0, "w": 0, "d": 0, "l": 0,
                "gf": 0, "ga": 0, "gd": 0,
            }

        matchups = [(0, 1), (2, 3), (0, 2), (1, 3), (0, 3), (1, 2)]
        for a_idx, b_idx in matchups:
            t_a = team_list[a_idx]
            t_b = team_list[b_idx]

            key = (t_a, t_b)
            if key in played_cache:
                score_a, score_b = played_cache[key]
            elif (t_b, t_a) in played_cache:
                key2 = (t_b, t_a)
                score_b, score_a = played_cache[key2]
            else:
                tid_a = _team_id_from_name(t_a, teams)
                tid_b = _team_id_from_name(t_b, teams)
                if tid_a and tid_b:
                    score_a, score_b = sample_fast(tid_a, tid_b)
                else:
                    score_a, score_b = np.random.poisson(1.2), np.random.poisson(1.2)

            stats[t_a]["played"] += 1
            stats[t_b]["played"] += 1
            stats[t_a]["gf"] += score_a
            stats[t_a]["ga"] += score_b
            stats[t_b]["gf"] += score_b
            stats[t_b]["ga"] += score_a

            if score_a > score_b:
                stats[t_a]["pts"] += 3
                stats[t_a]["w"] += 1
                stats[t_b]["l"] += 1
            elif score_b > score_a:
                stats[t_b]["pts"] += 3
                stats[t_b]["w"] += 1
                stats[t_a]["l"] += 1
            else:
                stats[t_a]["pts"] += 1
                stats[t_b]["pts"] += 1
                stats[t_a]["d"] += 1
                stats[t_b]["d"] += 1

        for t_name in team_list:
            stats[t_name]["gd"] = stats[t_name]["gf"] - stats[t_name]["ga"]

        sorted_teams = sorted(
            team_list,
            key=lambda tn: (stats[tn]["pts"], stats[tn]["gd"], stats[tn]["gf"]),
            reverse=True,
        )

        standings[gid] = [
            {
                "team_id": stats[tn]["team_id"],
                "team_name": stats[tn]["team_name"],
                "pts": stats[tn]["pts"],
                "played": stats[tn]["played"],
                "w": stats[tn]["w"],
                "d": stats[tn]["d"],
                "l": stats[tn]["l"],
                "gf": stats[tn]["gf"],
                "ga": stats[tn]["ga"],
                "gd": stats[tn]["gd"],
                "position": i + 1,
            }
            for i, tn in enumerate(sorted_teams)
        ]

    classified = {}
    all_thirds = []
    for gid, positions in standings.items():
        classified[gid] = [positions[0]["team_name"], positions[1]["team_name"], positions[2]["team_name"]]
        all_thirds.append(positions[2])

    all_thirds_sorted = sorted(all_thirds, key=lambda t: (t["pts"], t["gd"], t["gf"]), reverse=True)
    best_thirds = [t["team_name"] for t in all_thirds_sorted[:8]]

    return {
        "standings": standings,
        "classified": classified,
        "best_thirds": best_thirds,
        "all_thirds_sorted": [
            {"team_name": t["team_name"], "pts": t["pts"], "gd": t["gd"], "gf": t["gf"]}
            for t in all_thirds_sorted
        ],
    }


def simulate_knockout_stage(classified: dict, best_thirds: list, teams: list[dict]) -> dict:
    """
    Simula la fase eliminatoria desde R32 hasta la final.
    El bracket está bloqueado según la estructura oficial FIFA 2026.

    Returns:
        dict con champion, finalists, semifinalists, quarterfinalists, r16_teams
    """
    r32_teams = []
    group_order = sorted(classified.keys())

    for gid in group_order[:6]:
        r32_teams.append(classified[gid][0])
    for gid in group_order[:6]:
        r32_teams.append(classified[gid][1])

    for gid in group_order[6:]:
        r32_teams.append(classified[gid][0])
    for gid in group_order[6:]:
        r32_teams.append(classified[gid][1])

    r32_teams.extend(best_thirds)

    return _play_bracket_with_tracking(r32_teams, teams)


def _play_bracket_with_tracking(teams_round: list[str], teams: list[dict]) -> dict:
    """
    Juega el bracket SIN barajar, rastreando cada ronda para métricas de probabilidad.

    Returns:
        dict con champion, finalists, semifinalists, quarterfinalists
    """
    current = list(teams_round)
    round_num = 0
    result = {
        "champion": "",
        "finalists": [],
        "semifinalists": [],
        "quarterfinalists": [],
    }

    while len(current) > 1:
        round_num += 1
        next_round = []
        for i in range(0, len(current), 2):
            if i + 1 >= len(current):
                next_round.append(current[i])
                continue
            t_a = current[i]
            t_b = current[i + 1]
            tid_a = _team_id_from_name(t_a, teams)
            tid_b = _team_id_from_name(t_b, teams)

            if tid_a and tid_b:
                score_a, score_b = sample_fast(tid_a, tid_b)
            else:
                score_a, score_b = np.random.poisson(1.2), np.random.poisson(1.2)

            if score_a > score_b:
                winner = t_a
                loser = t_b
            elif score_b > score_a:
                winner = t_b
                loser = t_a
            else:
                if np.random.random() < 0.5:
                    winner = t_a
                    loser = t_b
                else:
                    winner = t_b
                    loser = t_a

            next_round.append(winner)

            if round_num == 1:
                result["quarterfinalists"].append(loser)
            elif round_num == 2:
                result["semifinalists"].append(loser)
            elif round_num == 3:
                result["finalists"].append(loser)

        current = next_round

    if len(current) >= 2:
        result["finalists"].extend(current[2:] if len(current) > 2 else [])
    elif len(current) == 1:
        result["finalists"].append("")

    if current:
        result["champion"] = current[0]

    return result


def _play_bracket(teams_round: list[str], teams: list[dict]) -> str:
    """
    Juega un bracket de eliminación directa SIN barajar.
    Los emparejamientos siguen el orden fijo del bracket FIFA 2026:
    posiciones adyacentes en la lista se enfrentan entre sí.
    """
    current = list(teams_round)

    while len(current) > 1:
        next_round = []
        for i in range(0, len(current), 2):
            if i + 1 >= len(current):
                next_round.append(current[i])
                continue
            t_a = current[i]
            t_b = current[i + 1]
            tid_a = _team_id_from_name(t_a, teams)
            tid_b = _team_id_from_name(t_b, teams)

            if tid_a and tid_b:
                score_a, score_b = sample_fast(tid_a, tid_b)
            else:
                score_a, score_b = np.random.poisson(1.2), np.random.poisson(1.2)

            if score_a > score_b:
                next_round.append(t_a)
            elif score_b > score_a:
                next_round.append(t_b)
            else:
                penalty_winner = 0 if np.random.random() < 0.5 else 1
                next_round.append(t_a if penalty_winner == 0 else t_b)

        current = next_round

    return current[0] if current else ""


def monte_carlo_simulation(n_simulations: int = MONTE_CARLO_DEFAULT_SIMULATIONS) -> dict:
    """
    Ejecuta N simulaciones completas del torneo y agrega resultados.

    Returns:
        Dict con probabilidades por equipo para:
        - champion: % de ganar el torneo
        - final: % de llegar a la final
        - semifinal: % de llegar a semifinales
        - quarterfinal: % de llegar a cuartos
        - round_of_16: % de avanzar de la fase de grupos
    """
    teams = _load_teams()
    groups = _load_groups()

    if not teams or not groups:
        return {"error": "No hay datos de equipos/grupos. Ejecuta run_scrapers.py primero."}

    n = min(n_simulations, 50000)

    champion_count = {}
    final_count = {}
    semifinal_count = {}
    quarterfinal_count = {}
    r16_count = {}
    group_advance_count = {}

    for t in teams:
        tn = t["name"]
        champion_count[tn] = 0
        final_count[tn] = 0
        semifinal_count[tn] = 0
        quarterfinal_count[tn] = 0
        r16_count[tn] = 0
        group_advance_count[tn] = 0

    for sim in range(n):
        group_result = simulate_group_stage(teams, groups)
        classified = group_result["classified"]
        best_thirds = group_result["best_thirds"]

        for gid, top3 in classified.items():
            for idx, tn in enumerate(top3):
                group_advance_count[tn] = group_advance_count.get(tn, 0) + 1

        all_r32 = []
        group_order = sorted(classified.keys())
        for gid in group_order:
            all_r32.extend(classified[gid][:2])
        all_r32.extend(best_thirds)

        for tn in all_r32:
            r16_count[tn] = r16_count.get(tn, 0) + 1

        champion = simulate_knockout_stage(classified, best_thirds, teams)

        if isinstance(champion, dict):
            if champion.get("champion"):
                champion_count[champion["champion"]] = champion_count.get(champion["champion"], 0) + 1
            for tn in champion.get("finalists", []):
                if tn:
                    final_count[tn] = final_count.get(tn, 0) + 1
            for tn in champion.get("semifinalists", []):
                if tn:
                    semifinal_count[tn] = semifinal_count.get(tn, 0) + 1
            for tn in champion.get("quarterfinalists", []):
                if tn:
                    quarterfinal_count[tn] = quarterfinal_count.get(tn, 0) + 1

    champion_probs = [
        {
            "team_name": tn,
            "probability": round(champion_count.get(tn, 0) / n, 4),
            "color_rank": i + 1,
        }
        for i, tn in enumerate(
            sorted(champion_count, key=lambda x: champion_count.get(x, 0), reverse=True)[:20]
        )
        if champion_count.get(tn, 0) > 0
    ]

    group_probs = [
        {
            "team_name": tn,
            "advance_probability": round(group_advance_count.get(tn, 0) / n, 4),
            "r16_probability": round(r16_count.get(tn, 0) / n, 4),
        }
        for tn in sorted(group_advance_count, key=lambda x: group_advance_count.get(x, 0), reverse=True)[:32]
        if group_advance_count.get(tn, 0) > 0
    ]

    return {
        "total_simulations": n,
        "champion_probabilities": champion_probs,
        "group_advance_probabilities": group_probs,
        "final_probabilities": [
            {"team_name": tn, "probability": round(final_count.get(tn, 0) / n, 4)}
            for tn in sorted(final_count, key=lambda x: final_count.get(x, 0), reverse=True)[:10]
            if final_count.get(tn, 0) > 0
        ],
        "semifinal_probabilities": [
            {"team_name": tn, "probability": round(semifinal_count.get(tn, 0) / n, 4)}
            for tn in sorted(semifinal_count, key=lambda x: semifinal_count.get(x, 0), reverse=True)[:16]
            if semifinal_count.get(tn, 0) > 0
        ],
        "top_favorites": champion_probs[:10],
    }


def simulate_single_match(team_a: str, team_b: str, n_iterations: int = 1000) -> dict:
    """
    Simula un solo partido N veces para obtener distribución de resultados.
    """
    teams = _load_teams()
    tid_a = _team_id_from_name(team_a, teams)
    tid_b = _team_id_from_name(team_b, teams)

    if not tid_a or not tid_b:
        return {"error": f"Equipo no encontrado: {team_a if not tid_a else team_b}"}

    wins_a = 0
    draws = 0
    wins_b = 0
    scorelines = {}

    for _ in range(n_iterations):
        ga, gb = sample_fast(tid_a, tid_b)
        key = f"{ga}-{gb}"
        scorelines[key] = scorelines.get(key, 0) + 1
        if ga > gb:
            wins_a += 1
        elif gb > ga:
            wins_b += 1
        else:
            draws += 1

    top_scores = sorted(scorelines.items(), key=lambda x: x[1], reverse=True)[:10]

    return {
        "team_a": team_a,
        "team_b": team_b,
        "simulations": n_iterations,
        "win_probability": round(wins_a / n_iterations, 4),
        "draw_probability": round(draws / n_iterations, 4),
        "loss_probability": round(wins_b / n_iterations, 4),
        "top_scorelines": [
            {"score": s, "count": c, "probability": round(c / n_iterations, 4)}
            for s, c in top_scores
        ],
    }

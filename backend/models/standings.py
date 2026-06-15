"""
Calculador de posiciones reales basado en resultados registrados.
Determina qué equipos avanzan a la fase eliminatoria.

Reglas FIFA Art. 11.5:
1. Puntos → 2. Diferencia de goles → 3. Goles anotados
Top 2 de cada grupo + 8 mejores terceros avanzan a R32.
"""

from utils.data_loader import load_json


def calculate_standings() -> dict:
    """
    Calcula posiciones reales de todos los grupos usando SOLO resultados registrados (no simulados).

    Returns:
        {
            "standings": {group_id: [{team_name, pts, played, w, d, l, gf, ga, gd, position}]},
            "classified": {group_id: [1st_name, 2nd_name, 3rd_name]},
            "best_thirds": [team_name, ...],  # 8 mejores terceros
            "all_thirds_sorted": [{team_name, pts, gd, gf}],
            "qualified_r32": [team_name, ...],  # 32 equipos a R32
        }
    """
    groups = load_json("groups.json") or []
    teams = load_json("teams.json") or []
    results = load_json("results.json") or []

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
            stats[t_name] = {
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
                _apply_result(stats, t_a, t_b, score_a, score_b)

        for t_name in team_list:
            stats[t_name]["gd"] = stats[t_name]["gf"] - stats[t_name]["ga"]

        sorted_teams = sorted(
            team_list,
            key=lambda tn: (stats[tn]["pts"], stats[tn]["gd"], stats[tn]["gf"]),
            reverse=True,
        )

        tid_map = {t["name"]: t["id"] for t in teams}
        standings[gid] = [
            {
                "team_id": tid_map.get(tn, tn.lower().replace(" ", "_")),
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
        classified[gid] = [
            positions[0]["team_name"],
            positions[1]["team_name"],
            positions[2]["team_name"],
        ]
        all_thirds.append(positions[2])

    all_thirds_sorted = sorted(all_thirds, key=lambda t: (t["pts"], t["gd"], t["gf"]), reverse=True)
    best_thirds = [t["team_name"] for t in all_thirds_sorted[:8]]

    qualified_r32 = []
    group_order = sorted(classified.keys())
    for gid in group_order:
        qualified_r32.extend(classified[gid][:2])
    qualified_r32.extend(best_thirds)

    return {
        "standings": standings,
        "classified": classified,
        "best_thirds": best_thirds,
        "all_thirds_sorted": [
            {"team_name": t["team_name"], "pts": t["pts"], "gd": t["gd"], "gf": t["gf"]}
            for t in all_thirds_sorted
        ],
        "qualified_r32": qualified_r32,
    }


def _apply_result(stats: dict, t_a: str, t_b: str, score_a: int, score_b: int) -> None:
    """Aplica un resultado a las estadísticas de dos equipos."""
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


def build_current_bracket() -> dict:
    """
    Construye el bracket eliminatorio actual basado en posiciones reales.
    Si no hay suficientes resultados, muestra las posiciones esperadas.
    """
    data = calculate_standings()
    fixtures = load_json("fixtures.json") or []

    ko_fixtures = [f for f in fixtures if f["stage"] == "knockout"]
    classified = data["classified"]
    best_thirds = data["best_thirds"]

    group_order = sorted(classified.keys())
    r32_teams = []
    for gid in group_order:
        r32_teams.extend(classified[gid][:2])
    r32_teams.extend(best_thirds)

    r32_fixtures = [f for f in ko_fixtures if f["round"] == "Round of 32"]

    for i, f in enumerate(r32_fixtures):
        if i < len(r32_teams):
            if i % 2 == 0:
                f["team_a"] = r32_teams[i]
            else:
                f["team_b"] = r32_teams[i]
        f["team_a"] = f.get("team_a") or "TBD"
        f["team_b"] = f.get("team_b") or "TBD"

    stages = {}
    for f in ko_fixtures:
        round_name = f["round"]
        if round_name not in stages:
            stages[round_name] = []
        stages[round_name].append({
            "id": f["id"],
            "date": f.get("date", ""),
            "team_a": f.get("team_a") or "TBD",
            "team_b": f.get("team_b") or "TBD",
            "score_a": f.get("score_a"),
            "score_b": f.get("score_b"),
            "played": f.get("played", False),
        })

    groups_complete = all(
        len([r for r in (load_json("results.json") or []) if r.get("group") == gid and r.get("played")]) == 6
        for gid in group_order
    )

    return {
        "stages": stages,
        "standings": data["standings"],
        "classified": classified,
        "best_thirds": best_thirds,
        "qualified_r32": data["qualified_r32"],
        "groups_complete": groups_complete,
        "total_knockout_matches": len(ko_fixtures),
    }

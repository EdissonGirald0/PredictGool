"""
Generador de datos históricos sintéticos para entrenamiento XGBoost.

Basado en el Libro Blanco:
- ~7,000 registros de partidos internacionales (Oct 2023 - Jun 2026)
- Backtest de 913 partidos con 62% precisión
- RPS de 0.162 en validación

Los datos se generan con distribuciones realistas basadas en Elo y patrones tácticos.
"""

import json
import math
import random
import numpy as np
from pathlib import Path
from datetime import date, timedelta

random.seed(42)
np.random.seed(42)

TEAMS = [
    "argentina", "france", "spain", "england", "brazil", "netherlands",
    "portugal", "germany", "belgium", "croatia", "uruguay", "colombia",
    "italy", "denmark", "switzerland", "austria", "morocco", "japan",
    "senegal", "serbia", "iran", "united_states", "mexico", "sweden",
    "south_korea", "poland", "egypt", "nigeria", "australia", "algeria",
    "chile", "canada", "tunisia", "paraguay", "cameroon", "ecuador",
    "costa_rica", "saudi_arabia", "qatar", "jamaica", "south_africa",
    "mali", "iraq", "china", "uzbekistan", "honduras", "panama", "new_zealand",
    "norway", "greece", "turkey", "ukraine", "scotland", "wales",
    "hungary", "czech_republic", "romania", "slovakia", "slovenia",
    "venezuela", "peru", "bolivia", "ivory_coast", "ghana", "burkina_faso",
]

ELO_RATINGS = {
    "argentina": 2135, "france": 2108, "spain": 2080, "england": 2055,
    "brazil": 2040, "netherlands": 2020, "portugal": 2005, "germany": 1990,
    "belgium": 1970, "croatia": 1965, "uruguay": 1955, "colombia": 1940,
    "italy": 1930, "denmark": 1915, "switzerland": 1905, "austria": 1890,
    "morocco": 1885, "japan": 1880, "senegal": 1870, "serbia": 1865,
    "iran": 1855, "united_states": 1850, "mexico": 1845, "sweden": 1840,
    "south_korea": 1835, "poland": 1830, "egypt": 1825, "nigeria": 1820,
    "australia": 1815, "algeria": 1810, "chile": 1805, "canada": 1800,
    "tunisia": 1795, "paraguay": 1790, "cameroon": 1785, "ecuador": 1780,
    "costa_rica": 1775, "saudi_arabia": 1770, "qatar": 1765, "jamaica": 1760,
    "south_africa": 1755, "mali": 1750, "iraq": 1745, "china": 1740,
    "uzbekistan": 1735, "honduras": 1730, "panama": 1725, "new_zealand": 1720,
    "norway": 1880, "greece": 1850, "turkey": 1860, "ukraine": 1845,
    "scotland": 1830, "wales": 1825, "hungary": 1810, "czech_republic": 1805,
    "romania": 1795, "slovakia": 1790, "slovenia": 1785,
    "venezuela": 1790, "peru": 1780, "bolivia": 1740,
    "ivory_coast": 1860, "ghana": 1835, "burkina_faso": 1810,
}

MATCH_TYPES = ["world_cup", "continental", "qualifier", "friendly"]
MATCH_TYPE_WEIGHTS = [0.05, 0.20, 0.35, 0.40]
K_FACTORS = {"world_cup": 60, "continental": 30, "qualifier": 40, "friendly": 20}


def expected_score(elo_a: int, elo_b: int) -> float:
    return 1.0 / (1.0 + math.pow(10, -(elo_a - elo_b) / 400.0))


def generate_match(elo_a: int, elo_b: int, match_type: str, home: bool) -> dict:
    elo_diff = elo_a - elo_b
    if not home:
        elo_diff -= 100

    we = expected_score(elo_a, elo_b) if home else expected_score(elo_a, elo_b + 100)

    draw_prob = 0.30 * (1.0 - abs(we - 0.5) * 2.0)
    draw_prob = max(0.15, min(0.38, draw_prob))

    lam_strong = max(0.3, 1.6 + elo_diff * 0.005)
    lam_weak = max(0.3, 1.6 - elo_diff * 0.005)
    lam_base = max(0.3, 1.0)

    r = random.random()
    if r < we * (1.0 - draw_prob):
        result = "win"
        score_a = np.random.poisson(lam_strong)
        score_b = np.random.poisson(lam_base)
        while score_a <= score_b:
            score_a = np.random.poisson(lam_strong)
    elif r < we * (1.0 - draw_prob) + draw_prob:
        result = "draw"
        g = np.random.poisson(lam_base)
        score_a = g
        score_b = g + np.random.choice([-1, 0, 0, 0, 0, 1])
        while score_a != score_b:
            g = np.random.poisson(lam_base)
            score_a = g
            score_b = g + np.random.choice([-1, 0, 0, 0, 0, 1])
    else:
        result = "loss"
        score_a = np.random.poisson(lam_base)
        score_b = np.random.poisson(lam_weak)
        while score_b <= score_a:
            score_b = np.random.poisson(lam_weak)

    score_a = max(0, int(score_a))
    score_b = max(0, int(score_b))

    k = K_FACTORS[match_type]
    if score_a > score_b:
        actual_a, actual_b = 1.0, 0.0
    elif score_b > score_a:
        actual_a, actual_b = 0.0, 1.0
    else:
        actual_a, actual_b = 0.5, 0.5

    gd = abs(score_a - score_b)
    k_adj = k * math.sqrt(1.0 + gd) if gd > 0 else k

    new_elo_a = int(elo_a + k_adj * (actual_a - we))
    if not home:
        new_elo_b = int(elo_b + k_adj * (actual_b - (1.0 - we)))

    home_advantage_flag = 1 if home else 0

    elo_diff_feat = elo_diff

    form_index = max(0.0, min(1.0, (elo_a - 1700) / 500.0))
    defensive_strength = (elo_a % 200) / 200.0

    return {
        "team_a": elo_a,
        "team_b": elo_b,
        "elo_diff": elo_diff_feat,
        "match_type": match_type,
        "home_advantage": home_advantage_flag,
        "score_a": score_a,
        "score_b": score_b,
        "result": result,
        "elo_a_new": new_elo_a,
        "features": {
            "elo_diff": elo_diff_feat,
            "elo_sum": elo_a + elo_b,
            "home_advantage": home_advantage_flag,
            "match_type_importance": K_FACTORS[match_type] / 60.0,
            "form_index_a": form_index,
            "defensive_strength_a": defensive_strength,
        }
    }


def generate_dataset(n_matches: int = 7000) -> list[dict]:
    matches = []
    current_elos = dict(ELO_RATINGS)
    start_date = date(2023, 10, 1)
    end_date = date(2026, 6, 1)
    days = (end_date - start_date).days
    team_list = list(TEAMS)
    elo_history = {t: [ELO_RATINGS[t]] for t in team_list}

    for i in range(n_matches):
        t_a, t_b = random.sample(team_list, 2)
        match_type = random.choices(MATCH_TYPES, weights=MATCH_TYPE_WEIGHTS, k=1)[0]
        home = random.random() < 0.4

        elo_a = current_elos[t_a]
        elo_b = current_elos[t_b]

        if home:
            home_team = t_a
            away_team = t_b
        else:
            home_team = t_b
            away_team = t_a
            elo_a, elo_b = elo_b, elo_a

        match_day = start_date + timedelta(days=int(random.random() * days))
        match = generate_match(elo_a, elo_b, match_type, True)

        match.update({
            "home_team": home_team,
            "away_team": away_team,
            "date": match_day.isoformat(),
            "match_id": i,
        })

        current_elos[home_team] = match["elo_a_new"]
        match["away_elo_new"] = int(elo_b + (elo_a - match["elo_a_new"]) * 0.5)
        current_elos[away_team] = match["away_elo_new"]

        elo_history[home_team].append(current_elos[home_team])
        elo_history[away_team].append(current_elos[away_team])

        matches.append(match)

    return matches


def save_dataset(matches: list[dict], filepath: str):
    data = {
        "total_matches": len(matches),
        "date_range": {
            "start": matches[0]["date"],
            "end": matches[-1]["date"],
        },
        "matches": matches,
    }
    Path(filepath).parent.mkdir(parents=True, exist_ok=True)
    with open(filepath, "w") as f:
        json.dump(data, f, indent=2, default=str)


if __name__ == "__main__":
    print("Generando dataset de ~7,000 partidos históricos...")
    matches = generate_dataset(7000)
    save_dataset(matches, "data/historical_matches.json")

    wins = sum(1 for m in matches if m["result"] == "win")
    draws = sum(1 for m in matches if m["result"] == "draw")
    losses = sum(1 for m in matches if m["result"] == "loss")
    print(f"✅ {len(matches)} partidos generados")
    print(f"   Victorias local: {wins} ({wins/len(matches)*100:.1f}%)")
    print(f"   Empates: {draws} ({draws/len(matches)*100:.1f}%)")
    print(f"   Victorias visitante: {losses} ({losses/len(matches)*100:.1f}%)")

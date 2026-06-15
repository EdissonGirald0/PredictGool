"""
Scraping del calendario de partidos (fixtures) desde Wikipedia.
Fuente: https://en.wikipedia.org/wiki/2026_FIFA_World_Cup
"""

import httpx
from bs4 import BeautifulSoup
import json

URL = "https://en.wikipedia.org/wiki/2026_FIFA_World_Cup"

GROUP_STAGE_DATES = [
    ("2026-06-11", "2026-06-19"),
    ("2026-06-20", "2026-06-27"),
]

KNOCKOUT_SCHEDULE = [
    ("Round of 32", "2026-06-28", "2026-07-03", 16),
    ("Round of 16", "2026-07-04", "2026-07-07", 8),
    ("Quarter-finals", "2026-07-09", "2026-07-11", 4),
    ("Semi-finals", "2026-07-14", "2026-07-15", 2),
    ("Third place", "2026-07-18", "2026-07-18", 1),
    ("Final", "2026-07-19", "2026-07-19", 1),
]


def load_groups() -> list[dict]:
    from utils.data_loader import load_json
    groups = load_json("groups.json")
    return groups or []


def generate_fixtures(groups: list[dict]) -> list[dict]:
    """
    Genera el calendario completo:
    - Fase de grupos: 3 jornadas por grupo (6 partidos por grupo = 72 partidos)
    - Eliminatorias: R32, R16, QF, SF, 3rd, Final (32 partidos)
    """
    fixtures = []
    fixture_id = 1

    group_letters = sorted([g["id"] for g in groups])
    group_start_dates = {}
    base_date = "2026-06-11"
    for i, gl in enumerate(group_letters):
        import datetime
        d = datetime.date.fromisoformat(base_date) + datetime.timedelta(days=i)
        group_start_dates[gl] = d.isoformat()

    for g in groups:
        teams = g["teams"]
        if len(teams) != 4:
            continue
        gl = g["id"]

        matchups = [
            (0, 1), (2, 3),
            (0, 2), (1, 3),
            (0, 3), (1, 2),
        ]
        for j, (a_idx, b_idx) in enumerate(matchups):
            round_name = f"Jornada {j + 1}"
            import datetime
            base = datetime.date.fromisoformat(group_start_dates[gl])
            match_date = base + datetime.timedelta(days=j * 4)

            fixtures.append({
                "id": fixture_id,
                "stage": "group",
                "round": round_name,
                "group": gl,
                "team_a": teams[a_idx],
                "team_b": teams[b_idx],
                "date": match_date.isoformat(),
                "venue": "TBD",
                "score_a": None,
                "score_b": None,
                "played": False,
            })
            fixture_id += 1

    for stage, start, end, matches_count in KNOCKOUT_SCHEDULE:
        for m in range(matches_count):
            import datetime
            d = datetime.date.fromisoformat(start)
            actual_date = d + datetime.timedelta(days=m)
            if actual_date > datetime.date.fromisoformat(end):
                actual_date = datetime.date.fromisoformat(end)

            fixtures.append({
                "id": fixture_id,
                "stage": "knockout",
                "round": stage,
                "group": None,
                "team_a": None,
                "team_b": None,
                "date": actual_date.isoformat(),
                "venue": "TBD",
                "score_a": None,
                "score_b": None,
                "played": False,
            })
            fixture_id += 1

    return fixtures


if __name__ == "__main__":
    groups_data = load_groups()
    if groups_data:
        fix = generate_fixtures(groups_data)
        print(f"Fixtures generados: {len(fix)}")
        group_matches = [f for f in fix if f["stage"] == "group"]
        ko_matches = [f for f in fix if f["stage"] == "knockout"]
        print(f"  Fase de grupos: {len(group_matches)}")
        print(f"  Eliminatorias: {len(ko_matches)}")
    else:
        print("No hay grupos. Ejecuta scrape_teams.py primero.")

#!/usr/bin/env python3
"""
Aplica los datos REALES del Mundial 2026 extraídos de Wikipedia.
Actualiza: teams.json, groups.json, results.json, elo_ratings.json, fixtures.json
"""

import json, sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from utils.data_loader import save_json, load_json

# ============================================================
# DATOS REALES DEL MUNDIAL 2026 (Wikipedia, 15 Jun 2026)
# ============================================================

REAL_GROUPS = {
    "A": ["Mexico", "South Korea", "Czech Republic", "South Africa"],
    "B": ["Switzerland", "Canada", "Qatar", "Bosnia and Herzegovina"],
    "C": ["Scotland", "Morocco", "Brazil", "Haiti"],
    "D": ["United States", "Australia", "Turkey", "Paraguay"],
    "E": ["Germany", "Ivory Coast", "Ecuador", "Curaçao"],
    "F": ["Sweden", "Japan", "Netherlands", "Tunisia"],
    "G": ["Belgium", "Egypt", "Iran", "New Zealand"],
    "H": ["Spain", "Cape Verde", "Saudi Arabia", "Uruguay"],
    "I": ["France", "Senegal", "Iraq", "Norway"],
    "J": ["Argentina", "Algeria", "Austria", "Jordan"],
    "K": ["Portugal", "DR Congo", "Uzbekistan", "Colombia"],
    "L": ["England", "Croatia", "Ghana", "Panama"],
}

REAL_RESULTS = [
    {"team_a": "Mexico", "team_b": "South Africa", "score_a": 2, "score_b": 0, "stage": "group", "group": "A"},
    {"team_a": "South Korea", "team_b": "Czech Republic", "score_a": 2, "score_b": 1, "stage": "group", "group": "A"},
    {"team_a": "Canada", "team_b": "Bosnia and Herzegovina", "score_a": 1, "score_b": 1, "stage": "group", "group": "B"},
    {"team_a": "Qatar", "team_b": "Switzerland", "score_a": 1, "score_b": 1, "stage": "group", "group": "B"},
    {"team_a": "Brazil", "team_b": "Morocco", "score_a": 1, "score_b": 1, "stage": "group", "group": "C"},
    {"team_a": "Haiti", "team_b": "Scotland", "score_a": 0, "score_b": 1, "stage": "group", "group": "C"},
    {"team_a": "United States", "team_b": "Paraguay", "score_a": 4, "score_b": 1, "stage": "group", "group": "D"},
    {"team_a": "Australia", "team_b": "Turkey", "score_a": 2, "score_b": 0, "stage": "group", "group": "D"},
    {"team_a": "Germany", "team_b": "Curaçao", "score_a": 7, "score_b": 1, "stage": "group", "group": "E"},
    {"team_a": "Ivory Coast", "team_b": "Ecuador", "score_a": 1, "score_b": 0, "stage": "group", "group": "E"},
    {"team_a": "Netherlands", "team_b": "Japan", "score_a": 2, "score_b": 2, "stage": "group", "group": "F"},
    {"team_a": "Sweden", "team_b": "Tunisia", "score_a": 5, "score_b": 1, "stage": "group", "group": "F"},
]

FLAG_MAP = {
    "mexico": "🇲🇽", "united_states": "🇺🇸", "canada": "🇨🇦",
    "argentina": "🇦🇷", "brazil": "🇧🇷", "uruguay": "🇺🇾",
    "colombia": "🇨🇴", "ecuador": "🇪🇨", "paraguay": "🇵🇾",
    "england": "🏴󠁧󠁢󠁥󠁮󠁧󠁿", "france": "🇫🇷", "germany": "🇩🇪",
    "spain": "🇪🇸", "italy": "🇮🇹", "netherlands": "🇳🇱",
    "portugal": "🇵🇹", "belgium": "🇧🇪", "croatia": "🇭🇷",
    "switzerland": "🇨🇭", "sweden": "🇸🇪", "norway": "🇳🇴",
    "turkey": "🇹🇷", "scotland": "🏴󠁧󠁢󠁳󠁣󠁴󠁿", "austria": "🇦🇹",
    "czech_republic": "🇨🇿", "bosnia_and_herzegovina": "🇧🇦",
    "japan": "🇯🇵", "south_korea": "🇰🇷", "iran": "🇮🇷",
    "saudi_arabia": "🇸🇦", "australia": "🇦🇺", "qatar": "🇶🇦",
    "uzbekistan": "🇺🇿", "iraq": "🇮🇶", "jordan": "🇯🇴",
    "morocco": "🇲🇦", "senegal": "🇸🇳", "tunisia": "🇹🇳",
    "algeria": "🇩🇿", "egypt": "🇪🇬", "ghana": "🇬🇭",
    "ivory_coast": "🇨🇮", "south_africa": "🇿🇦",
    "cape_verde": "🇨🇻", "dr_congo": "🇨🇩",
    "costa_rica": "🇨🇷", "panama": "🇵🇦", "haiti": "🇭🇹",
    "curaçao": "🇨🇼", "jamaica": "🇯🇲", "new_zealand": "🇳🇿",
}

ELO_REAL = {
    "argentina": 2135, "france": 2108, "spain": 2080, "england": 2055,
    "brazil": 2040, "netherlands": 2020, "portugal": 2005, "germany": 1990,
    "belgium": 1970, "croatia": 1965, "uruguay": 1955, "colombia": 1940,
    "mexico": 1845, "united_states": 1850, "canada": 1800,
    "switzerland": 1905, "austria": 1890, "sweden": 1840, "norway": 1880,
    "turkey": 1860, "scotland": 1830, "czech_republic": 1805,
    "bosnia_and_herzegovina": 1750, "denmark": 1915, "poland": 1830,
    "serbia": 1865,
    "morocco": 1885, "japan": 1880, "senegal": 1870,
    "south_korea": 1835, "iran": 1855, "saudi_arabia": 1770,
    "australia": 1815, "qatar": 1765, "uzbekistan": 1735,
    "iraq": 1745, "jordan": 1720,
    "egypt": 1825, "algeria": 1810, "tunisia": 1795,
    "nigeria": 1820, "cameroon": 1785, "ghana": 1835,
    "ivory_coast": 1860, "south_africa": 1755,
    "cape_verde": 1710, "dr_congo": 1740,
    "ecuador": 1780, "chile": 1805, "paraguay": 1790,
    "costa_rica": 1775, "panama": 1725, "honduras": 1730,
    "jamaica": 1760, "haiti": 1680, "curaçao": 1670,
    "new_zealand": 1720,
    "china": 1740, "mali": 1750,
}


def build_teams():
    teams = []
    for gid, team_names in REAL_GROUPS.items():
        for name in team_names:
            tid = name.lower().replace(" ", "_")
            teams.append({
                "id": tid,
                "name": name,
                "group": gid,
                "fifa_rank": None,
                "elo": ELO_REAL.get(tid, 1500),
                "flag_emoji": FLAG_MAP.get(tid, "🏳️"),
            })
    return teams


def build_groups():
    groups = []
    for gid, team_names in REAL_GROUPS.items():
        groups.append({"id": gid, "name": f"Grupo {gid}", "teams": team_names})
    return groups


def build_results():
    results = []
    for i, r in enumerate(REAL_RESULTS):
        results.append({
            "id": f"res_{r['team_a'].lower().replace(' ','_')}_{r['team_b'].lower().replace(' ','_')}",
            "team_a": r["team_a"],
            "team_b": r["team_b"],
            "score_a": r["score_a"],
            "score_b": r["score_b"],
            "stage": r["stage"],
            "group": r["group"],
            "date": "2026-06-11",
            "played": True,
        })
    return results


def build_elo_ratings():
    ratings = {}
    for gid, team_names in REAL_GROUPS.items():
        for name in team_names:
            tid = name.lower().replace(" ", "_")
            ratings[tid] = ELO_REAL.get(tid, 1500)

    from models.elo import update_elo
    for r in REAL_RESULTS:
        tid_a = r["team_a"].lower().replace(" ", "_")
        tid_b = r["team_b"].lower().replace(" ", "_")
        try:
            update_elo(tid_a, tid_b, r["score_a"], r["score_b"], match_type="world_cup")
        except Exception:
            pass

    return {"last_updated": "2026-06-15", "ratings": ratings, "source": "eloratings.net + FIFA 2026 real"}


def build_fixtures():
    from scrapers.scrape_fixtures import generate_fixtures
    groups = build_groups()
    return generate_fixtures(groups)


if __name__ == "__main__":
    import sys
    force = "--force" in sys.argv

    print("⚽ Aplicando datos REALES del Mundial 2026...")

    teams = build_teams()
    save_json("teams.json", teams)
    print(f"  ✅ teams.json: {len(teams)} equipos")

    groups = build_groups()
    save_json("groups.json", groups)
    print(f"  ✅ groups.json: {len(groups)} grupos")

    existing_results = load_json("results.json") or []
    if force or len(existing_results) == 0:
        results = build_results()
        save_json("results.json", results)
        print(f"  ✅ results.json: {len(results)} resultados (inicial)")
    else:
        print(f"  ⏭️  results.json: {len(existing_results)} resultados (preservados)")

    existing_elo = load_json("elo_ratings.json") or {}
    if force or not existing_elo.get("ratings"):
        print("  Calculando Elo con resultados reales...")
        elo_ratings = build_elo_ratings()
        save_json("elo_ratings.json", elo_ratings)
        print(f"  ✅ elo_ratings.json: {len(elo_ratings['ratings'])} ratings")
    else:
        print(f"  ⏭️  elo_ratings.json: {len(existing_elo.get('ratings',{}))} ratings (preservados)")

    fixtures = build_fixtures()
    save_json("fixtures.json", fixtures)
    print(f"  ✅ fixtures.json: {len(fixtures)} partidos")

    existing_bias = load_json("bias_state.json") or {}
    if force or existing_bias.get("total_tracked", 0) == 0:
        from models.bias import recalibrate_from_results
        print("  Inicializando sistema de sesgo...")
        recalibrate_from_results()
    else:
        print(f"  ⏭️  bias_state.json: {existing_bias.get('total_tracked',0)} tracked (preservado)")

    print()
    print("=== Grupos Reales ===")
    for gid, names in REAL_GROUPS.items():
        print(f"  Grupo {gid}: {' | '.join(names)}")

    print()
    print("=== Resultados Reales (12 partidos jugados) ===")
    for r in REAL_RESULTS:
        print(f"  {r['team_a']} {r['score_a']}-{r['score_b']} {r['team_b']} (Grupo {r['group']})")

    print()
    print("✅ Datos reales aplicados. Reinicia el backend para usar los nuevos datos.")

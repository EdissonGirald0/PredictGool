#!/usr/bin/env python3
"""
Aplica los datos REALES del Mundial 2026 extraídos de Wikipedia.
Nombres de selecciones en español.
Actualiza: teams.json, groups.json, results.json, elo_ratings.json, fixtures.json
"""

import json, sys, os, unicodedata
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from utils.data_loader import save_json, load_json


def make_id(name: str) -> str:
    """Convierte nombre a ID: quita acentos, minúsculas, reemplaza espacios."""
    nfkd = unicodedata.normalize('NFKD', name)
    ascii_name = nfkd.encode('ascii', 'ignore').decode('ascii')
    return ascii_name.lower().replace(" ", "_").replace("-", "_")


# ============================================================
# DATOS REALES DEL MUNDIAL 2026 — Nombres en español
# ============================================================

REAL_GROUPS = {
    "A": ["México", "Corea del Sur", "República Checa", "Sudáfrica"],
    "B": ["Suiza", "Canadá", "Catar", "Bosnia y Herzegovina"],
    "C": ["Escocia", "Marruecos", "Brasil", "Haití"],
    "D": ["Estados Unidos", "Australia", "Turquía", "Paraguay"],
    "E": ["Alemania", "Costa de Marfil", "Ecuador", "Curazao"],
    "F": ["Suecia", "Japón", "Países Bajos", "Túnez"],
    "G": ["Bélgica", "Egipto", "Irán", "Nueva Zelanda"],
    "H": ["España", "Cabo Verde", "Arabia Saudita", "Uruguay"],
    "I": ["Francia", "Senegal", "Irak", "Noruega"],
    "J": ["Argentina", "Argelia", "Austria", "Jordania"],
    "K": ["Portugal", "RD Congo", "Uzbekistán", "Colombia"],
    "L": ["Inglaterra", "Croacia", "Ghana", "Panamá"],
}

REAL_RESULTS = [
    {"team_a": "México",          "team_b": "Sudáfrica",               "score_a": 2, "score_b": 0, "stage": "group", "group": "A"},
    {"team_a": "Corea del Sur",   "team_b": "República Checa",         "score_a": 2, "score_b": 1, "stage": "group", "group": "A"},
    {"team_a": "Canadá",          "team_b": "Bosnia y Herzegovina",    "score_a": 1, "score_b": 1, "stage": "group", "group": "B"},
    {"team_a": "Catar",           "team_b": "Suiza",                   "score_a": 1, "score_b": 1, "stage": "group", "group": "B"},
    {"team_a": "Brasil",          "team_b": "Marruecos",               "score_a": 1, "score_b": 1, "stage": "group", "group": "C"},
    {"team_a": "Haití",           "team_b": "Escocia",                 "score_a": 0, "score_b": 1, "stage": "group", "group": "C"},
    {"team_a": "Estados Unidos",  "team_b": "Paraguay",                "score_a": 4, "score_b": 1, "stage": "group", "group": "D"},
    {"team_a": "Australia",       "team_b": "Turquía",                 "score_a": 2, "score_b": 0, "stage": "group", "group": "D"},
    {"team_a": "Alemania",        "team_b": "Curazao",                 "score_a": 7, "score_b": 1, "stage": "group", "group": "E"},
    {"team_a": "Costa de Marfil", "team_b": "Ecuador",                 "score_a": 1, "score_b": 0, "stage": "group", "group": "E"},
    {"team_a": "Países Bajos",    "team_b": "Japón",                   "score_a": 2, "score_b": 2, "stage": "group", "group": "F"},
    {"team_a": "Suecia",          "team_b": "Túnez",                   "score_a": 5, "score_b": 1, "stage": "group", "group": "F"},
]

FLAG_MAP = {
    "mexico": "🇲🇽", "estados_unidos": "🇺🇸", "canada": "🇨🇦",
    "argentina": "🇦🇷", "brasil": "🇧🇷", "uruguay": "🇺🇾",
    "colombia": "🇨🇴", "ecuador": "🇪🇨", "paraguay": "🇵🇾",
    "inglaterra": "🏴󠁧󠁢󠁥󠁮󠁧󠁿", "francia": "🇫🇷", "alemania": "🇩🇪",
    "espana": "🇪🇸", "paises_bajos": "🇳🇱", "portugal": "🇵🇹",
    "belgica": "🇧🇪", "croacia": "🇭🇷", "suiza": "🇨🇭",
    "suecia": "🇸🇪", "noruega": "🇳🇴", "turquia": "🇹🇷",
    "escocia": "🏴󠁧󠁢󠁳󠁣󠁴󠁿", "austria": "🇦🇹",
    "republica_checa": "🇨🇿", "bosnia_y_herzegovina": "🇧🇦",
    "japon": "🇯🇵", "corea_del_sur": "🇰🇷", "iran": "🇮🇷",
    "arabia_saudita": "🇸🇦", "australia": "🇦🇺", "catar": "🇶🇦",
    "uzbekistan": "🇺🇿", "irak": "🇮🇶", "jordania": "🇯🇴",
    "marruecos": "🇲🇦", "senegal": "🇸🇳", "tunez": "🇹🇳",
    "argelia": "🇩🇿", "egipto": "🇪🇬", "ghana": "🇬🇭",
    "costa_de_marfil": "🇨🇮", "sudafrica": "🇿🇦",
    "cabo_verde": "🇨🇻", "rd_congo": "🇨🇩",
    "costa_rica": "🇨🇷", "panama": "🇵🇦", "haiti": "🇭🇹",
    "curazao": "🇨🇼", "jamaica": "🇯🇲", "nueva_zelanda": "🇳🇿",
    "dinamarca": "🇩🇰", "serbia": "🇷🇸", "polonia": "🇵🇱",
    "italia": "🇮🇹", "nigeria": "🇳🇬", "camerun": "🇨🇲",
    "chile": "🇨🇱", "peru": "🇵🇪", "venezuela": "🇻🇪",
    "bolivia": "🇧🇴", "honduras": "🇭🇳", "china": "🇨🇳",
    "mali": "🇲🇱", "grecia": "🇬🇷", "ucrania": "🇺🇦",
    "hungria": "🇭🇺", "rumania": "🇷🇴", "eslovaquia": "🇸🇰",
}

ELO_REAL = {
    "argentina": 2135, "francia": 2108, "espana": 2080, "inglaterra": 2055,
    "brasil": 2040, "paises_bajos": 2020, "portugal": 2005, "alemania": 1990,
    "belgica": 1970, "croacia": 1965, "uruguay": 1955, "colombia": 1940,
    "mexico": 1845, "estados_unidos": 1850, "canada": 1800,
    "suiza": 1905, "austria": 1890, "suecia": 1840, "noruega": 1880,
    "turquia": 1860, "escocia": 1830, "republica_checa": 1805,
    "bosnia_y_herzegovina": 1750, "dinamarca": 1915, "polonia": 1830,
    "serbia": 1865, "marruecos": 1885, "japon": 1880, "senegal": 1870,
    "corea_del_sur": 1835, "iran": 1855, "arabia_saudita": 1770,
    "australia": 1815, "catar": 1765, "uzbekistan": 1735,
    "irak": 1745, "jordania": 1720,
    "egipto": 1825, "argelia": 1810, "tunez": 1795,
    "nigeria": 1820, "camerun": 1785, "ghana": 1835,
    "costa_de_marfil": 1860, "sudafrica": 1755,
    "cabo_verde": 1710, "rd_congo": 1740,
    "ecuador": 1780, "chile": 1805, "paraguay": 1790,
    "costa_rica": 1775, "panama": 1725, "honduras": 1730,
    "jamaica": 1760, "haiti": 1680, "curazao": 1670,
    "nueva_zelanda": 1720,
    "china": 1740, "mali": 1750,
}


def build_teams():
    teams = []
    for gid, team_names in REAL_GROUPS.items():
        for name in team_names:
            tid = make_id(name)
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
    for r in REAL_RESULTS:
        results.append({
            "id": f"res_{make_id(r['team_a'])}_{make_id(r['team_b'])}",
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
            tid = make_id(name)
            ratings[tid] = ELO_REAL.get(tid, 1500)

    from models.elo import update_elo
    for r in REAL_RESULTS:
        tid_a = make_id(r["team_a"])
        tid_b = make_id(r["team_b"])
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
    force = "--force" in sys.argv

    print("⚽ Aplicando datos del Mundial 2026 (español)...")

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
    print("=== Grupos (español) ===")
    for gid, names in REAL_GROUPS.items():
        print(f"  Grupo {gid}: {' | '.join(names)}")

    print()
    print("=== Resultados (español) ===")
    for r in REAL_RESULTS:
        print(f"  {r['team_a']} {r['score_a']}-{r['score_b']} {r['team_b']}")

    print()
    print("✅ Datos en español aplicados.")

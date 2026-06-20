"""
Sistema de actualización automática de resultados con validación estricta.

- Scraping de múltiples fuentes con validación contra equipos oficiales
- Mapeo inglés→español para nombres de equipos
- Prevención de duplicados y resultados inválidos
- Limpieza de resultados erróneos
"""

import re
import httpx
from fastapi import APIRouter
from utils.data_loader import load_json, save_json, name_to_id

router = APIRouter(prefix="/api/admin", tags=["updater"])

HEADERS = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
    "Accept-Language": "es-ES,es;q=0.9,en;q=0.8",
}

SOURCES = [
    {"name": "Google", "url": "https://www.google.com/search?q=fifa+world+cup+2026+results+today&hl=en", "type": "google"},
    {"name": "Wikipedia-mobile", "url": "https://en.m.wikipedia.org/wiki/2026_FIFA_World_Cup", "type": "wikipedia"},
]

# Mapeo inglés → español para scraping automático
EN_TO_ES = {
    "mexico": "México", "south korea": "Corea del Sur", "korea republic": "Corea del Sur",
    "czech republic": "República Checa", "czechia": "República Checa",
    "south africa": "Sudáfrica", "switzerland": "Suiza", "canada": "Canadá",
    "qatar": "Catar", "bosnia and herzegovina": "Bosnia y Herzegovina", "bosnia": "Bosnia y Herzegovina",
    "scotland": "Escocia", "morocco": "Marruecos", "brazil": "Brasil", "haiti": "Haití",
    "united states": "Estados Unidos", "usa": "Estados Unidos", "us": "Estados Unidos",
    "australia": "Australia", "turkey": "Turquía", "türkiye": "Turquía", "paraguay": "Paraguay",
    "germany": "Alemania", "ivory coast": "Costa de Marfil", "côte d'ivoire": "Costa de Marfil",
    "ecuador": "Ecuador", "curaçao": "Curazao", "curacao": "Curazao",
    "sweden": "Suecia", "japan": "Japón", "netherlands": "Países Bajos",
    "tunisia": "Túnez", "tunis": "Túnez", "belgium": "Bélgica", "egypt": "Egipto",
    "iran": "Irán", "new zealand": "Nueva Zelanda", "spain": "España",
    "cape verde": "Cabo Verde", "saudi arabia": "Arabia Saudita", "uruguay": "Uruguay",
    "france": "Francia", "senegal": "Senegal", "iraq": "Irak", "norway": "Noruega",
    "argentina": "Argentina", "algeria": "Argelia", "austria": "Austria",
    "jordan": "Jordania", "portugal": "Portugal", "dr congo": "RD Congo",
    "congo dr": "RD Congo", "uzbekistan": "Uzbekistán", "colombia": "Colombia",
    "england": "Inglaterra", "croatia": "Croacia", "ghana": "Ghana", "panama": "Panamá",
    "denmark": "Dinamarca", "kosovo": None, "czechia": "República Checa",
}


def _load_team_names() -> set:
    teams = load_json("teams.json") or []
    return {t["name"] for t in teams}


def _normalize_team(text: str, valid_names: set) -> str | None:
    """Normaliza un nombre de equipo: inglés→español, validación."""
    text = text.strip()
    if text in valid_names:
        return text

    text_lower = text.lower()

    # Mapeo directo inglés→español
    if text_lower in EN_TO_ES:
        mapped = EN_TO_ES[text_lower]
        if mapped and mapped in valid_names:
            return mapped

    # Búsqueda por subcadena
    for en_name, es_name in EN_TO_ES.items():
        if es_name is None:
            continue
        if text_lower in en_name or en_name in text_lower:
            if es_name in valid_names:
                return es_name

    # Búsqueda directa case-insensitive
    for name in valid_names:
        if name.lower() == text_lower:
            return name

    return None


def _extract_results(text: str) -> list[dict]:
    """Extrae resultados de texto con validación de equipos."""
    valid_names = _load_team_names()
    results = []
    seen = set()

    # Buscar equipos conocidos cerca de patrones de score
    for name in valid_names:
        for pattern in [rf'{re.escape(name)}\s+(\d+)\s*[–\-—]\s*(\d+)',
                        rf'(\d+)\s*[–\-—]\s*(\d+)\s+{re.escape(name)}']:
            for m in re.finditer(pattern, text, re.IGNORECASE):
                score_a = int(m.group(1))
                score_b = int(m.group(2))
                if 0 <= score_a <= 15 and 0 <= score_b <= 15:
                    results.append({"team": name, "score_a": score_a, "score_b": score_b, "is_team_a": "after" not in pattern})

    # Patrón general: NombreA X-Y NombreB
    pattern = re.compile(
        r'([A-ZÁÉÍÓÚÜÑ][A-Za-záéíóúüñ\s\.\-]+?)\s+(\d+)\s*[–\-—]\s*(\d+)\s+([A-ZÁÉÍÓÚÜÑ][A-Za-záéíóúüñ\s\.\-]+?)(?:\s+(?:group|stats|stage|Referee|Attendance|Estadio|Match|\(|$)|$)',
        re.IGNORECASE
    )

    for m in pattern.finditer(text):
        raw_a = m.group(1).strip().rstrip('.').rstrip(',')
        raw_b = m.group(4).strip().rstrip('.').rstrip(',')

        team_a = _normalize_team(raw_a, valid_names)
        team_b = _normalize_team(raw_b, valid_names)

        if not team_a or not team_b:
            continue
        if team_a == team_b:
            continue

        score_a = int(m.group(2))
        score_b = int(m.group(3))

        if not (0 <= score_a <= 15 and 0 <= score_b <= 15):
            continue

        key = f"{team_a}_{team_b}".lower()
        if key in seen:
            continue
        seen.add(key)

        results.append({
            "team_a": team_a,
            "team_b": team_b,
            "score_a": score_a,
            "score_b": score_b,
        })

    return results


@router.post("/fetch-results")
def fetch_latest_results():
    """
    Busca nuevos resultados de múltiples fuentes con validación estricta.
    Solo acepta equipos que existen en el torneo.
    Los nombres en inglés se mapean automáticamente a español.
    """
    existing = load_json("results.json") or []
    existing_keys = set()
    for r in existing:
        existing_keys.add(f"{r.get('team_a','')}_{r.get('team_b','')}".lower())
        existing_keys.add(f"{r.get('team_b','')}_{r.get('team_a','')}".lower())

    new_results = []
    for source in SOURCES:
        try:
            resp = httpx.get(source["url"], timeout=20, follow_redirects=True, headers=HEADERS)
            if resp.status_code != 200:
                continue
            extracted = _extract_results(resp.text)
            for r in extracted:
                key = f"{r['team_a']}_{r['team_b']}".lower()
                if key not in existing_keys:
                    r["id"] = f"res_{name_to_id(r['team_a'])}_{name_to_id(r['team_b'])}"
                    r["stage"] = "group"
                    r["date"] = ""
                    r["played"] = True
                    new_results.append(r)
                    existing_keys.add(key)
        except Exception:
            continue

    if new_results:
        for r in new_results:
            existing.append(r)
        save_json("results.json", existing)

        from models.elo import update_elo
        for r in new_results:
            try:
                update_elo(name_to_id(r["team_a"]), name_to_id(r["team_b"]),
                          r["score_a"], r["score_b"], match_type="world_cup")
            except Exception:
                pass

        from models.bias import recalibrate_from_results
        recalibrate_from_results()

        return {
            "status": "ok",
            "new_results": len(new_results),
            "results": [f"{r['team_a']} {r['score_a']}-{r['score_b']} {r['team_b']}" for r in new_results],
            "total": len(existing),
        }

    return {
        "status": "ok",
        "new_results": 0,
        "message": "No se encontraron nuevos resultados válidos. Registra manualmente en la vista En Vivo.",
        "total": len(existing),
    }


@router.post("/clean-results")
def clean_invalid_results():
    """Elimina resultados de equipos no reconocidos en el torneo."""
    valid_names = _load_team_names()
    results = load_json("results.json") or []

    clean = []
    removed = []
    for r in results:
        team_a_ok = _normalize_team(r.get("team_a", ""), valid_names) is not None
        team_b_ok = _normalize_team(r.get("team_b", ""), valid_names) is not None

        if team_a_ok and team_b_ok:
            r["team_a"] = _normalize_team(r.get("team_a", ""), valid_names) or r["team_a"]
            r["team_b"] = _normalize_team(r.get("team_b", ""), valid_names) or r["team_b"]
            r["id"] = f"res_{name_to_id(r['team_a'])}_{name_to_id(r['team_b'])}"
            clean.append(r)
        else:
            removed.append(f"{r.get('team_a','?')} {r.get('score_a','?')}-{r.get('score_b','?')} {r.get('team_b','?')}")

    if removed:
        save_json("results.json", clean)
        from models.bias import recalibrate_from_results
        recalibrate_from_results()

    return {
        "status": "ok",
        "original_total": len(results),
        "clean_total": len(clean),
        "removed": len(removed),
        "removed_items": removed,
    }


@router.post("/recalibrate")
def recalibrate_bias():
    from models.bias import recalibrate_from_results
    return recalibrate_from_results()


@router.get("/bias-status")
def get_bias_status():
    from models.bias import get_bias_state
    state = get_bias_state()
    return {
        "total_tracked": state["total_tracked"],
        "ensemble_weights": state["ensemble_weights"],
        "model_performance": {
            "dixon_coles": {
                "accuracy": round(state["model_performance"]["dixon_coles"]["correct"] /
                                  max(state["model_performance"]["dixon_coles"]["total"], 1), 4),
                "total": state["model_performance"]["dixon_coles"]["total"],
            },
            "elo": {
                "accuracy": round(state["model_performance"]["elo"]["correct"] /
                                  max(state["model_performance"]["elo"]["total"], 1), 4),
                "total": state["model_performance"]["elo"]["total"],
            },
        },
        "teams_with_form": len(state.get("team_form", {})),
        "global_stats": state.get("global_stats", {}),
        "confidence_thresholds": state.get("confidence_thresholds", {}),
        "updated_at": state.get("updated_at", ""),
    }

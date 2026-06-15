"""
Scraping de datos oficiales FIFA 2026:
- Grupos reales con sus 4 equipos
- Resultados de partidos ya jugados (11-15 Jun 2026)

Fuente: https://www.fifa.com/es/tournaments/mens/worldcup/canadamexicousa2026/articles/fase-grupos-copa-mundial-2026-partidos-zonas
"""

import json
import re
import httpx
from bs4 import BeautifulSoup

URL = "https://www.fifa.com/es/tournaments/mens/worldcup/canadamexicousa2026/articles/fase-grupos-copa-mundial-2026-partidos-zonas"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "es-ES,es;q=0.9,en;q=0.8",
}


def scrape_fifa() -> dict | None:
    """Intenta scrapear la página de FIFA con datos oficiales."""
    try:
        resp = httpx.get(URL, timeout=30, follow_redirects=True, headers=HEADERS)
        if resp.status_code == 403:
            print(f"  ⚠️ FIFA bloqueó la IP (403 Forbidden)")
            return None
        resp.raise_for_status()
    except Exception as e:
        print(f"  ⚠️ Error al acceder a FIFA: {e}")
        return None

    soup = BeautifulSoup(resp.text, "lxml")
    text = soup.get_text("\n", strip=True)

    groups_data = _extract_groups_from_text(text)
    results_data = _extract_results_from_text(text)

    return {
        "source": URL,
        "groups": groups_data,
        "results": results_data,
    }


def _extract_groups_from_text(text: str) -> list[dict]:
    """Busca menciones de grupos (Grupo A, Grupo B, ... Grupo L)."""
    groups = []
    lines = text.split("\n")

    current_group = None
    current_teams = []

    for line in lines:
        line = line.strip()
        if not line:
            continue

        match = re.match(r"Grupo\s+([A-L])\b", line, re.IGNORECASE)
        if match:
            if current_group and len(current_teams) >= 3:
                groups.append({"id": current_group, "teams": current_teams[:4]})
            current_group = match.group(1).upper()
            current_teams = []
            continue

        if current_group and len(line) > 2 and not line.startswith(("http", "www", "Ver ", "Leer ", "Seguir")):
            if not any(line.lower().startswith(w) for w in ["grupo", "partido", "jornada", "clasific", "fase", "mundial", "copa"]):
                clean = re.sub(r"\s*\([^)]*\)", "", line).strip()
                if len(clean) > 3 and len(clean) < 40 and len(current_teams) < 4:
                    if clean not in current_teams:
                        current_teams.append(clean)

    if current_group and len(current_teams) >= 3:
        groups.append({"id": current_group, "teams": current_teams[:4]})

    return groups


def _extract_results_from_text(text: str) -> list[dict]:
    """Busca resultados de partidos (equipoA X-Y equipoB)."""
    results = []
    lines = text.split("\n")

    score_pattern = re.compile(r"(\d+)\s*[-–—]\s*(\d+)")

    for i, line in enumerate(lines):
        match = score_pattern.search(line)
        if not match:
            continue

        score_a = int(match.group(1))
        score_b = int(match.group(2))

        before = line[:match.start()].strip()
        after = line[match.end():].strip()

        team_a = _clean_team_name(before)
        team_b = _clean_team_name(after)

        if not team_a and i > 0:
            team_a = _clean_team_name(lines[i - 1])
        if not team_b and i + 1 < len(lines):
            team_b = _clean_team_name(lines[i + 1])

        if team_a and team_b and team_a != team_b:
            results.append({
                "team_a": team_a,
                "team_b": team_b,
                "score_a": score_a,
                "score_b": score_b,
            })

    return results


def _clean_team_name(text: str) -> str:
    """Limpia un nombre de equipo de caracteres sobrantes."""
    text = re.sub(r"\s*\([^)]*\)", "", text)
    text = re.sub(r"^\d+[\.\)]\s*", "", text)
    text = re.sub(r"[•·•⚽🏆✅❌📊📅]", "", text)
    text = re.sub(r"\s+", " ", text)
    text = text.strip()

    if len(text) < 3 or len(text) > 40:
        return ""
    if text.lower() in ["vs", "vs.", "contra", "y", "-", "—", "grupo", "partido"]:
        return ""

    return text


if __name__ == "__main__":
    print("Scraping FIFA.com para datos oficiales del Mundial 2026...")
    data = scrape_fifa()

    if data and data["groups"]:
        print(f"\n✅ Grupos encontrados: {len(data['groups'])}")
        for g in data["groups"]:
            print(f"  Grupo {g['id']}: {', '.join(g['teams'])}")
    else:
        print("  ⚠️ No se encontraron grupos en la página")

    if data and data["results"]:
        print(f"\n✅ Resultados encontrados: {len(data['results'])}")
        for r in data["results"]:
            print(f"  {r['team_a']} {r['score_a']}-{r['score_b']} {r['team_b']}")
    else:
        print("  ⚠️ No se encontraron resultados en la página")

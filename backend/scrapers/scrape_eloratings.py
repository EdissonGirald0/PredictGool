"""
Scraping de ratings Elo desde eloratings.net
"""

import httpx
from bs4 import BeautifulSoup
import re

URL = "https://eloratings.net/"


def scrape_elo_ratings() -> dict[str, dict]:
    """
    Extrae ratings Elo actuales de todas las selecciones.

    Returns:
        dict: {team_name_lower: {elo: int, rank: int, name: str}}
    """
    resp = httpx.get(URL, timeout=30, follow_redirects=True,
                     headers={"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"})
    if resp.status_code == 403:
        return {}
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "lxml")

    ratings = {}
    rows = soup.find_all("tr")

    for row in rows:
        cells = row.find_all("td")
        if len(cells) < 3:
            continue

        texts = [c.get_text(strip=True) for c in cells]
        try:
            rank = int(texts[0])
        except (ValueError, IndexError):
            continue

        name = texts[1] if len(texts) > 1 else ""
        try:
            elo = int(texts[2]) if len(texts) > 2 and texts[2].isdigit() else None
        except (ValueError, IndexError):
            continue

        if name and rank and elo:
            key = name.lower().replace(" ", "_")
            ratings[key] = {
                "name": name,
                "elo": elo,
                "rank": rank
            }

    return ratings


def match_elo_to_teams(teams: list[dict], elo_ratings: dict[str, dict]) -> dict[str, int]:
    """
    Empareja los ratings Elo con los equipos del torneo.
    Prueba múltiples estrategias de matching.
    """
    matched = {}

    for t in teams:
        name = t["name"]
        key = name.lower().replace(" ", "_")

        if key in elo_ratings:
            matched[t["id"]] = elo_ratings[key]["elo"]
            continue

        for ek, ev in elo_ratings.items():
            ev_name = ev["name"].lower()
            if key in ev_name or ev_name in key:
                matched[t["id"]] = ev["elo"]
                break

    return matched


if __name__ == "__main__":
    ratings = scrape_elo_ratings()
    print(f"Ratings Elo encontrados: {len(ratings)}")
    for k, v in sorted(ratings.items(), key=lambda x: x[1]["elo"], reverse=True)[:20]:
        print(f"  {v['rank']:3d}. {v['name']:30s} Elo: {v['elo']}")

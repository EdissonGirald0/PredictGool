"""
Scraping de resultados de partidos ya jugados del Mundial 2026 (11-15 Jun).
Fuente: Wikipedia / API de fútbol.
"""

import httpx
from bs4 import BeautifulSoup
from datetime import date, timedelta

URL = "https://en.wikipedia.org/wiki/2026_FIFA_World_Cup"


def scrape_results() -> list[dict]:
    """
    Extrae resultados de partidos ya jugados de Wikipedia.

    Returns:
        Lista de dicts con {team_a, team_b, score_a, score_b, date, stage, group}
    """
    headers = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"}
    resp = httpx.get(URL, timeout=30, follow_redirects=True, headers=headers)
    if resp.status_code == 403:
        return []
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "lxml")

    results = []

    score_pattern = re.compile(r"(\d+)\s*[-–—]\s*(\d+)")

    tables = soup.find_all("table", class_="wikitable")
    for table in tables:
        rows = table.find_all("tr")
        for row in rows:
            cells = row.find_all(["td", "th"])
            cell_texts = [c.get_text(strip=True) for c in cells]

            for text in cell_texts:
                match = score_pattern.search(text)
                if match:
                    score_a_str, score_b_str = match.group(1), match.group(2)

                    team_b = ""
                    team_a = ""

                    for ct in cell_texts:
                        if ct and ct != text and len(ct) > 2:
                            if not team_a:
                                team_a = ct
                            elif not team_b:
                                team_b = ct
                                break

                    if team_a and team_b:
                        results.append({
                            "team_a": team_a,
                            "team_b": team_b,
                            "score_a": int(score_a_str),
                            "score_b": int(score_b_str),
                            "stage": "group",
                        })

    return results


def scrape_fallback_results() -> list[dict]:
    """
    Si Wikipedia no tiene resultados actualizados, buscar en otras fuentes.
    Intenta football-data.org o genera resultados de ejemplo.
    """
    results = []

    try:
        resp = httpx.get(
            "https://api.football-data.org/v4/competitions/WC/matches",
            timeout=15,
            headers={"User-Agent": "Mozilla/5.0"}
        )
        if resp.status_code == 200:
            data = resp.json()
            for match in data.get("matches", []):
                if match.get("status") == "FINISHED":
                    results.append({
                        "team_a": match["homeTeam"]["name"],
                        "team_b": match["awayTeam"]["name"],
                        "score_a": match["score"]["fullTime"]["home"],
                        "score_b": match["score"]["fullTime"]["away"],
                        "date": match["utcDate"][:10],
                        "stage": match.get("stage", "GROUP"),
                        "group": match.get("group", "").replace("GROUP_", ""),
                    })
    except Exception:
        pass

    return results


import re

if __name__ == "__main__":
    results = scrape_results()
    if not results:
        results = scrape_fallback_results()

    print(f"Resultados encontrados: {len(results)}")
    for r in results:
        print(f"  {r.get('date', '?')} | {r['team_a']} {r['score_a']}-{r['score_b']} {r['team_b']} | {r.get('stage', '?')}")

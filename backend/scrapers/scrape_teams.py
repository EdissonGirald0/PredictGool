"""
Scraping de equipos clasificados y composición de grupos desde Wikipedia.
Fuente: https://en.wikipedia.org/wiki/2026_FIFA_World_Cup
"""

import httpx
from bs4 import BeautifulSoup

URL = "https://en.wikipedia.org/wiki/2026_FIFA_World_Cup"


def scrape_teams_and_groups() -> tuple[list[dict], list[dict]]:
    """
    Extrae los 48 equipos clasificados y la composición de los 12 grupos (A-L).

    Returns:
        teams: lista de dicts con {id, name, group, fifa_rank, flag_emoji}
        groups: lista de dicts con {id, name, teams: [team_ids]}
    """
    headers = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"}
    resp = httpx.get(URL, timeout=30, follow_redirects=True, headers=headers)
    if resp.status_code == 403:
        import sys
        print("  ⚠️  Wikipedia bloqueó la solicitud. Usando datos de respaldo.", file=sys.stderr)
        return [], []
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "lxml")

    groups_data = _extract_groups_from_tables(soup)
    teams_list = _build_teams_list(groups_data)

    return teams_list, groups_data


def _extract_groups_from_tables(soup: BeautifulSoup) -> list[dict]:
    """Busca tablas de grupos en la página de Wikipedia."""
    groups = []
    group_letters = [chr(65 + i) for i in range(12)]  # A-L

    tables = soup.find_all("table", class_="wikitable")
    group_idx = 0
    assigned = set()

    for table in tables:
        headers = [th.get_text(strip=True) for th in table.find_all("th")]
        if not any("Team" in h or "Equipo" in h or "Pos" in h or "Pos." in h for h in headers):
            continue

        rows = table.find_all("tr")
        team_names = []
        for row in rows:
            cells = row.find_all(["td", "th"])
            for cell in cells:
                text = cell.get_text(strip=True)
                if text and len(text) > 2 and not text.isdigit() and "/" not in text:
                    clean = text.split("[")[0].strip()
                    if clean and clean not in assigned and len(clean) < 50:
                        team_names.append(clean)
                        assigned.add(clean)
                        break

        if 3 <= len(team_names) <= 6 and group_idx < 12:
            group_name = group_letters[group_idx]
            groups.append({
                "id": group_name,
                "name": f"Grupo {group_name}",
                "teams": team_names[:4]
            })
            group_idx += 1

    return groups


def _build_teams_list(groups: list[dict]) -> list[dict]:
    """Construye lista plana de equipos con IDs."""
    FLAG_MAP = _flag_map()
    teams = []
    for g in groups:
        for t_name in g["teams"]:
            team_id = t_name.lower().replace(" ", "_").replace(".", "")
            teams.append({
                "id": team_id,
                "name": t_name,
                "group": g["id"],
                "fifa_rank": None,
                "flag_emoji": FLAG_MAP.get(team_id, FLAG_MAP.get(t_name, "🏳️"))
            })
    return teams


def _flag_map() -> dict[str, str]:
    """Mapeo de nombres de equipo a emojis de bandera."""
    return {
        "united_states": "🇺🇸", "mexico": "🇲🇽", "canada": "🇨🇦",
        "argentina": "🇦🇷", "brazil": "🇧🇷", "uruguay": "🇺🇾",
        "colombia": "🇨🇴", "ecuador": "🇪🇨", "chile": "🇨🇱",
        "paraguay": "🇵🇾", "peru": "🇵🇪", "bolivia": "🇧🇴",
        "venezuela": "🇻🇪",
        "england": "🏴󠁧󠁢󠁥󠁮󠁧󠁿", "france": "🇫🇷", "germany": "🇩🇪",
        "spain": "🇪🇸", "italy": "🇮🇹", "netherlands": "🇳🇱",
        "portugal": "🇵🇹", "belgium": "🇧🇪", "croatia": "🇭🇷",
        "switzerland": "🇨🇭", "denmark": "🇩🇰", "serbia": "🇷🇸",
        "austria": "🇦🇹", "poland": "🇵🇱", "sweden": "🇸🇪",
        "turkey": "🇹🇷", "ukraine": "🇺🇦", "scotland": "🏴󠁧󠁢󠁳󠁣󠁴󠁿",
        "wales": "🏴󠁧󠁢󠁷󠁬󠁳󠁿", "hungary": "🇭🇺", "norway": "🇳🇴",
        "greece": "🇬🇷", "czech_republic": "🇨🇿", "romania": "🇷🇴",
        "slovakia": "🇸🇰", "slovenia": "🇸🇮",
        "japan": "🇯🇵", "south_korea": "🇰🇷", "iran": "🇮🇷",
        "saudi_arabia": "🇸🇦", "australia": "🇦🇺", "qatar": "🇶🇦",
        "united_arab_emirates": "🇦🇪", "china": "🇨🇳", "uzbekistan": "🇺🇿",
        "morocco": "🇲🇦", "senegal": "🇸🇳", "tunisia": "🇹🇳",
        "algeria": "🇩🇿", "egypt": "🇪🇬", "nigeria": "🇳🇬",
        "cameroon": "🇨🇲", "ghana": "🇬🇭", "ivory_coast": "🇨🇮",
        "south_africa": "🇿🇦", "mali": "🇲🇱", "burkina_faso": "🇧🇫",
        "costa_rica": "🇨🇷", "panama": "🇵🇦", "honduras": "🇭🇳",
        "jamaica": "🇯🇲", "new_zealand": "🇳🇿",
    }


if __name__ == "__main__":
    teams, groups = scrape_teams_and_groups()
    print(f"Equipos encontrados: {len(teams)}")
    for t in teams:
        print(f"  {t['flag_emoji']} {t['name']} (Grupo {t['group']})")
    print(f"\nGrupos: {len(groups)}")

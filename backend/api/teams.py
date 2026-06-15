"""Endpoints de equipos y grupos."""

from fastapi import APIRouter, HTTPException

from models.elo import get_elo, get_all_elos
from utils.data_loader import load_json

router = APIRouter(prefix="/api", tags=["teams"])


@router.get("/teams")
def get_teams():
    teams = load_json("teams.json") or []
    elos = get_all_elos()
    for t in teams:
        t["elo"] = elos.get(t["id"], 1500)
    return teams


@router.get("/teams/{team_id}")
def get_team(team_id: str):
    teams = load_json("teams.json") or []
    elos = get_all_elos()
    for t in teams:
        if t["id"] == team_id:
            t["elo"] = elos.get(t["id"], 1500)
            return t
    raise HTTPException(404, f"Equipo '{team_id}' no encontrado")


@router.get("/groups")
def get_groups():
    groups = load_json("groups.json") or []
    teams = load_json("teams.json") or []
    elos = get_all_elos()

    result = []
    for g in groups:
        group_teams = []
        for t_name in g["teams"]:
            tid = t_name.lower().replace(" ", "_")
            t_data = next((t for t in teams if t["id"] == tid), None)
            group_teams.append({
                "id": tid,
                "name": t_name,
                "elo": elos.get(tid, 1500),
                "flag_emoji": t_data["flag_emoji"] if t_data else "🏳️",
            })
        result.append({
            "id": g["id"],
            "name": g["name"],
            "teams": group_teams,
        })
    return result


@router.get("/fixtures")
def get_fixtures():
    fixtures = load_json("fixtures.json") or []
    return fixtures


@router.get("/elo")
def get_elo_ratings():
    elos = get_all_elos()
    teams = load_json("teams.json") or []
    result = []
    for t in teams:
        result.append({
            "id": t["id"],
            "name": t["name"],
            "elo": elos.get(t["id"], 1500),
            "flag_emoji": t.get("flag_emoji", "🏳️"),
            "group": t.get("group", ""),
        })
    result.sort(key=lambda x: x["elo"], reverse=True)
    return result


@router.get("/favorites")
def get_favorites():
    from models.tournament import monte_carlo_simulation
    mc = monte_carlo_simulation(200)
    if "error" in mc:
        raise HTTPException(500, mc["error"])
    return mc.get("top_favorites", [])

"""Endpoints de simulación del torneo."""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from models.tournament import monte_carlo_simulation, simulate_group_stage
from models.standings import calculate_standings, build_current_bracket
from utils.data_loader import load_json

router = APIRouter(prefix="/api/simulate", tags=["simulation"])


class TournamentSimRequest(BaseModel):
    n: int = 1000


@router.post("/tournament")
def simulate_tournament(req: TournamentSimRequest):
    n = min(max(req.n, 100), 50000)
    result = monte_carlo_simulation(n)
    if "error" in result:
        raise HTTPException(500, result["error"])
    return result


@router.get("/group/{group_id}")
def simulate_group(group_id: str):
    groups = load_json("groups.json") or []
    teams = load_json("teams.json") or []

    group = next((g for g in groups if g["id"].upper() == group_id.upper()), None)
    if not group:
        raise HTTPException(404, f"Grupo '{group_id}' no encontrado")

    result = simulate_group_stage(teams, [group])
    standings = result["standings"].get(group["id"], [])
    return {
        "group": group["id"],
        "standings": standings,
    }


@router.get("/bracket")
def get_bracket():
    """Devuelve la estructura del bracket eliminatorio (vacío, sin resultados)."""
    fixtures = load_json("fixtures.json") or []

    ko_fixtures = [f for f in fixtures if f["stage"] == "knockout"]
    stages = {}
    for f in ko_fixtures:
        round_name = f["round"]
        if round_name not in stages:
            stages[round_name] = []
        stages[round_name].append(f)

    return {
        "stages": stages,
        "total_knockout_matches": len(ko_fixtures),
    }


@router.get("/standings")
def get_standings():
    """Posiciones reales calculadas desde resultados registrados."""
    return calculate_standings()


@router.get("/bracket/current")
def get_current_bracket():
    """Bracket eliminatorio poblado con equipos según posiciones reales actuales."""
    return build_current_bracket()

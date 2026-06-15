"""Endpoints de administración."""

from fastapi import APIRouter, HTTPException

from utils.data_loader import load_json

router = APIRouter(prefix="/api/admin", tags=["admin"])


@router.post("/update-elo")
def update_elo_all():
    results = load_json("results.json") or []
    if not results:
        return {"status": "ok", "message": "No hay resultados para recalcular Elo", "updated": 0}

    from models.elo import update_elo
    updated = 0
    for r in results:
        if not r.get("played"):
            continue
        tid_a = r["team_a"].lower().replace(" ", "_")
        tid_b = r["team_b"].lower().replace(" ", "_")
        try:
            update_elo(tid_a, tid_b, r["score_a"], r["score_b"], match_type="world_cup")
            updated += 1
        except Exception:
            pass

    return {"status": "ok", "message": f"Elo actualizado con {updated} resultados", "updated": updated}


@router.post("/reload")
def reload_data():
    try:
        import subprocess
        import sys
        result = subprocess.run(
            [sys.executable, "run_scrapers.py"],
            capture_output=True, text=True, timeout=120,
            cwd=".",
        )
        return {
            "status": "ok" if result.returncode == 0 else "error",
            "output": result.stdout[-500:],
            "error_output": result.stderr[-500:],
        }
    except Exception as e:
        raise HTTPException(500, f"Error al recargar datos: {str(e)}")


@router.get("/health")
def health_check():
    teams = load_json("teams.json") or []
    groups = load_json("groups.json") or []
    fixtures = load_json("fixtures.json") or []
    results = load_json("results.json") or []
    elo = load_json("elo_ratings.json") or {}

    return {
        "status": "healthy",
        "data": {
            "teams": len(teams),
            "groups": len(groups),
            "fixtures": len(fixtures),
            "results": len(results),
            "elo_ratings": len(elo.get("ratings", {})),
        }
    }

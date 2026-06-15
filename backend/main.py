"""
PredictGool API - Backend de predicciones Mundial FIFA 2026

FastAPI app que expone:
- Predicción de partidos (Elo + Dixon-Coles Poisson)
- Datos de equipos, grupos, fixtures
- Simulación Monte Carlo del torneo completo
- Tracking de resultados en vivo
- Panel de administración
"""

from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, HTMLResponse

from config import CORS_ORIGINS, HOST, PORT
from api.predict import router as predict_router
from api.teams import router as teams_router
from api.simulation import router as simulation_router
from api.results import router as results_router
from api.admin import router as admin_router
from api.accuracy import router as accuracy_router
from api.auth import router as auth_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield


app = FastAPI(
    title="PredictGool API",
    description="API de predicciones para la Copa Mundial FIFA 2026",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(predict_router)
app.include_router(teams_router)
app.include_router(simulation_router)
app.include_router(results_router)
app.include_router(admin_router)
app.include_router(accuracy_router)
app.include_router(auth_router)


FRONTEND_DIR = Path(__file__).resolve().parent.parent / "frontend" / "dist"


@app.get("/api")
def api_root():
    return {
        "name": "PredictGool API",
        "version": "1.0.0",
        "endpoints": {
            "predict": "/api/predict",
            "teams": "/api/teams",
            "groups": "/api/groups",
            "fixtures": "/api/fixtures",
            "simulate": "/api/simulate/tournament",
            "results": "/api/results",
            "admin": "/api/admin/health",
            "favorites": "/api/favorites",
            "elo": "/api/elo",
        }
    }


if FRONTEND_DIR.exists():
    _static = StaticFiles(directory=str(FRONTEND_DIR), html=True)

    @app.get("/{full_path:path}")
    async def serve_frontend(full_path: str, request: Request):
        file_path = FRONTEND_DIR / full_path
        if file_path.is_file():
            return FileResponse(file_path)
        return FileResponse(FRONTEND_DIR / "index.html")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host=HOST, port=PORT, reload=True)

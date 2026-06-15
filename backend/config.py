import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"

CORS_ORIGINS = os.getenv("CORS_ORIGINS", "http://localhost:5173,http://localhost:3000").split(",")
HOST = os.getenv("HOST", "0.0.0.0")
PORT = int(os.getenv("PORT", "8000"))

ELO_K_WORLD_CUP = 60
ELO_K_QUALIFIERS = 40
ELO_K_CONTINENTAL = 30
ELO_K_FRIENDLY = 20
ELO_HOME_ADVANTAGE = 100

MONTE_CARLO_DEFAULT_SIMULATIONS = 10_000
MONTECARLO_SIMULATIONS_MIN = 100
MONTECARLO_SIMULATIONS_MAX = 50_000

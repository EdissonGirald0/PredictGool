import json
import unicodedata
from pathlib import Path
from typing import Any

from config import DATA_DIR


def load_json(filename: str) -> Any:
    path = DATA_DIR / filename
    if not path.exists():
        return None
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def save_json(filename: str, data: Any) -> None:
    path = DATA_DIR / filename
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def name_to_id(name: str) -> str:
    """Convierte nombre de equipo a ID: quita acentos, minúsculas, reemplaza espacios."""
    nfkd = unicodedata.normalize('NFKD', name)
    ascii_name = nfkd.encode('ascii', 'ignore').decode('ascii')
    return ascii_name.lower().replace(" ", "_").replace("-", "_")

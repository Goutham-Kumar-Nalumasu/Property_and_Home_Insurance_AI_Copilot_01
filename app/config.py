from pathlib import Path
from dotenv import load_dotenv
import os

load_dotenv()


class Settings:
    APP_NAME: str = os.getenv("APP_NAME", "HomeShield Property Insurance Copilot")

    BASE_DIR: Path = Path(__file__).resolve().parent.parent

    RAW_DATA_DIR: Path = BASE_DIR / os.getenv("RAW_DATA_DIR", "data/raw")
    PROCESSED_DATA_DIR: Path = BASE_DIR / os.getenv("PROCESSED_DATA_DIR", "data/processed")
    MEMORY_FILE: Path = BASE_DIR / os.getenv("MEMORY_FILE", "data/memory/sessions.json")
    REPAIR_COST_FILE: Path = BASE_DIR / os.getenv(
        "REPAIR_COST_FILE",
        "data/raw/PropertyDamage_RepairCostTable.csv",
    )

    CHUNKS_FILE: Path = PROCESSED_DATA_DIR / "chunks.json"

    API_BASE_URL: str = os.getenv("API_BASE_URL", "http://localhost:8000")

    CHUNK_SIZE: int = 900
    CHUNK_OVERLAP: int = 150
    TOP_K: int = 5


settings = Settings()
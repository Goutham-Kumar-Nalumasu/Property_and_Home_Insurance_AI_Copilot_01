from pathlib import Path
from dotenv import load_dotenv
import os

load_dotenv()

class Settings:
    APP_NAME: str = os.getenv("APP_NAME", "HomeShield Property Insurance Copilot")

    BASE_DIR: Path = Path(__file__).resolve().parent.parent

    RAW_DATA_DIR: Path = BASE_DIR / os.getenv("RAW_DATA_DIR", "data/raw")
    PROCESSED_DATA_DIR: Path = BASE_DIR / os.getenv("PROCESSED_DATA_DIR", "data/processed")
    REPAIR_COST_FILE: Path = BASE_DIR / os.getenv(
        "REPAIR_COST_FILE",
        "data/raw/PropertyDamage_RepairCostTable.csv",
    )
    CHUNKS_FILE: Path = PROCESSED_DATA_DIR / "chunks.json"

    API_BASE_URL: str = os.getenv("API_BASE_URL", "http://localhost:8000")

    CHUNK_SIZE: int = 900
    CHUNK_OVERLAP: int = 150
    TOP_K: int = 5

    # Mem0 configuration
    MEM0_COLLECTION_NAME: str = os.getenv("MEM0_COLLECTION_NAME", "homeshield_memories")
    MEM0_HOST: str = os.getenv("MEM0_HOST", "localhost")
    MEM0_PORT: int = int(os.getenv("MEM0_PORT", "6333"))      # Qdrant default
    MEM0_USE_LOCAL: bool = os.getenv("MEM0_USE_LOCAL", "true").lower() == "true"

    # MCP server configuration (in-process)
    MCP_SERVER_HOST: str = os.getenv("MCP_SERVER_HOST", "127.0.0.1")
    MCP_SERVER_PORT: int = int(os.getenv("MCP_SERVER_PORT", "5000"))

settings = Settings()
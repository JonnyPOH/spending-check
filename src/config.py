import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

ROOT = Path(__file__).parent.parent

ANTHROPIC_API_KEY: str = os.getenv("ANTHROPIC_API_KEY", "")
ANTHROPIC_MODEL: str = os.getenv("ANTHROPIC_MODEL", "claude-sonnet-4-6")
CSV_PATH: Path = ROOT / os.getenv("CSV_PATH", "data/transactions_real.csv")
SQL_DIR: Path = ROOT / "sql"
LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")

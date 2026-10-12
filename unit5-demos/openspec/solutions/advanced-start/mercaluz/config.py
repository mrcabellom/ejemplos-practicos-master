"""Paths and connection to the local warehouse (DuckDB)."""

from dataclasses import dataclass
from pathlib import Path

import duckdb

PROJECT_ROOT = Path(__file__).resolve().parent.parent


@dataclass(frozen=True)
class Settings:
    landing_dir: Path = PROJECT_ROOT / "data" / "landing" / "orders"
    warehouse_path: Path = PROJECT_ROOT / "warehouse" / "mercaluz.duckdb"
    exports_dir: Path = PROJECT_ROOT / "exports"


def connect(settings: Settings) -> duckdb.DuckDBPyConnection:
    settings.warehouse_path.parent.mkdir(parents=True, exist_ok=True)
    con = duckdb.connect(str(settings.warehouse_path))
    for schema in ("bronze", "silver", "gold"):
        con.execute(f"CREATE SCHEMA IF NOT EXISTS {schema}")
    return con

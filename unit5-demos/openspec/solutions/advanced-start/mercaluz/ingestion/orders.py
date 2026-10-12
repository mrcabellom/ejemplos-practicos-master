"""Ingestion of daily order files from landing into bronze.orders_raw.

Reprocessing a file replaces the rows previously loaded from it, inside a single
transaction: if the load fails, bronze keeps the previous version of the file.
"""

from datetime import datetime, timezone
from pathlib import Path

import duckdb

RAW_COLUMNS = [
    "order_id",
    "order_ts",
    "store_id",
    "customer_email",
    "product_sku",
    "category",
    "quantity",
    "unit_price",
    "status",
]


def ensure_bronze_table(con: duckdb.DuckDBPyConnection) -> None:
    cols = ", ".join(f"{c} VARCHAR" for c in RAW_COLUMNS)
    con.execute(
        f"""
        CREATE TABLE IF NOT EXISTS bronze.orders_raw (
            {cols},
            _source_file VARCHAR,
            _ingested_at TIMESTAMP
        )
        """
    )


def landing_file_for(landing_dir: Path, business_date: str) -> Path:
    return landing_dir / f"{business_date}.csv"


def ingest_orders_file(con: duckdb.DuckDBPyConnection, path: Path) -> int:
    """Load (or reload) a landing CSV into bronze.orders_raw and return the number of rows loaded."""
    if not path.exists():
        raise FileNotFoundError(f"Landing file not found: {path}")

    ensure_bronze_table(con)
    ingested_at = datetime.now(timezone.utc).replace(tzinfo=None)
    con.begin()
    try:
        con.execute("DELETE FROM bronze.orders_raw WHERE _source_file = ?", [path.name])
        con.execute(
            f"""
            INSERT INTO bronze.orders_raw
            SELECT {", ".join(RAW_COLUMNS)}, ? AS _source_file, ? AS _ingested_at
            FROM read_csv(?, header = true, all_varchar = true)
            """,
            [path.name, ingested_at, str(path)],
        )
        loaded = con.execute(
            "SELECT count(*) FROM bronze.orders_raw WHERE _source_file = ?", [path.name]
        ).fetchone()[0]
        con.commit()
    except Exception:
        con.rollback()
        raise
    return loaded

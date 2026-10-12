"""gold.daily_sales -> exports/finance_daily_sales.csv for the Finance Excel macro.

Uses ';' as separator and a decimal comma for compatibility with Spanish-locale Excel.
"""

from pathlib import Path

import duckdb


def export_finance_csv(con: duckdb.DuckDBPyConnection, exports_dir: Path) -> Path:
    exports_dir.mkdir(parents=True, exist_ok=True)
    target = exports_dir / "finance_daily_sales.csv"
    rows = con.execute(
        "SELECT order_date, store_id, orders_count, total_amount "
        "FROM gold.daily_sales ORDER BY order_date, store_id"
    ).fetchall()
    with target.open("w", encoding="utf-8", newline="") as fh:
        fh.write("date;store;orders;total_amount\n")
        for order_date, store_id, orders_count, total_amount in rows:
            amount = f"{total_amount:.2f}".replace(".", ",")
            fh.write(f"{order_date.isoformat()};{store_id};{orders_count};{amount}\n")
    return target

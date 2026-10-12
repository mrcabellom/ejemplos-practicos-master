"""Query the local warehouse and print the result as a table.

Usage:
    uv run python query.py gold.daily_sales
    uv run python query.py "SELECT order_id, quantity FROM silver.order_lines WHERE store_id = 'VLC-007'"

A bare table name is shorthand for SELECT * FROM <table>.

The connection is read-only and has no file system access: the query can read
the warehouse tables but cannot modify them, read other files or write exports.
"""

import argparse
import sys
from decimal import Decimal
from pathlib import Path

import duckdb
from rich.console import Console
from rich.table import Table
from rich.text import Text

WAREHOUSE_PATH = Path(__file__).resolve().parent / "warehouse" / "mercaluz.duckdb"

console = Console()


def to_sql(query_or_table: str) -> str:
    text = query_or_table.strip()
    return text if " " in text else f"SELECT * FROM {text}"


def cell(value: object) -> Text:
    if value is None:
        return Text("NULL", style="dim")
    return Text(str(value))


def build_table(columns: list[str], types: list[object], rows: list[tuple]) -> Table:
    table = Table(header_style="bold cyan")
    for i, (name, col_type) in enumerate(zip(columns, types)):
        numeric = any(isinstance(row[i], (int, float, Decimal)) for row in rows)
        header = Text.assemble(name, "\n", (str(col_type).lower(), "dim"))
        table.add_column(header, justify="right" if numeric else "left")
    for row in rows:
        table.add_row(*(cell(v) for v in row))
    return table


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("query", help="SQL query, or a table name such as gold.daily_sales")
    args = parser.parse_args()

    if not WAREHOUSE_PATH.exists():
        console.print("[red]The warehouse does not exist yet.[/red] Run: uv run python run_pipeline.py --all")
        sys.exit(1)

    con = duckdb.connect(
        str(WAREHOUSE_PATH),
        read_only=True,
        config={"enable_external_access": False},
    )
    try:
        result = con.sql(to_sql(args.query))
        if result is None:
            console.print("[yellow]The statement returned no rows.[/yellow] query.py is meant for SELECT queries.")
            return
        columns, types, rows = result.columns, result.types, result.fetchall()
    except duckdb.Error as exc:
        console.print(Text.assemble(("Query failed: ", "red"), str(exc)))
        sys.exit(1)
    finally:
        con.close()

    console.print(build_table(columns, types, rows))
    console.print(f"[dim]{len(rows)} {'row' if len(rows) == 1 else 'rows'}[/dim]")


if __name__ == "__main__":
    main()

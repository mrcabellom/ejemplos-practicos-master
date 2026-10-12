"""Demo 03 · A JOIN that inflates the report.

Loads data/sales.csv and data/customers.csv into an in-memory SQLite database
and builds the sales-by-region report: first wrong, then right.

Usage:  uv run python run_demo.py            (all at once)
        uv run python run_demo.py --pause    (wait for Enter between steps)
"""
import csv
import sqlite3
import sys
from pathlib import Path

from rich.console import Console
from rich.panel import Panel
from rich.syntax import Syntax
from rich.table import Table

DATA_DIR = Path(__file__).parent / "data"
PAUSE = "--pause" in sys.argv

console = Console()


def pause():
    if PAUSE:
        console.input("\n[dim]\\[Enter para continuar][/dim] ")


def load_csv(con, table, path):
    """Create a table with the CSV columns and load its rows."""
    with open(path, encoding="utf-8", newline="") as f:
        rows = list(csv.DictReader(f))
    columns = list(rows[0].keys())
    con.execute(f"CREATE TABLE {table} ({', '.join(columns)})")
    placeholders = ", ".join("?" for _ in columns)
    con.executemany(
        f"INSERT INTO {table} VALUES ({placeholders})",
        [tuple(row[c] for c in columns) for row in rows],
    )


def show(con, title, sql):
    """Run a query, print it and its result as a table, and return the rows."""
    console.print()
    console.rule(f"[bold cyan]{title}")
    console.print(Syntax(sql.strip(), "sql", theme="ansi_dark", word_wrap=True))
    cursor = con.execute(sql)
    rows = cursor.fetchall()
    table = Table()
    for column in cursor.description:
        table.add_column(column[0])
    for row in rows:
        table.add_row(*(str(value) for value in row))
    console.print(table)
    return rows


def compare(report_total, source_total):
    if report_total == source_total:
        console.print(f"Informe: [bold green]{report_total}[/]  ·  origen: {source_total}  [green]✓ cuadra[/]")
    else:
        diff = report_total - source_total
        console.print(f"Informe: [bold red]{report_total}[/]  ·  origen: {source_total}  [red]✗ {diff:+} de diferencia[/]")


def main():
    con = sqlite3.connect(":memory:")
    load_csv(con, "sales", DATA_DIR / "sales.csv")
    load_csv(con, "customers", DATA_DIR / "customers.csv")

    # Step 1: the reference figure
    (source_total,) = show(con, "Paso 1 · Total de ventas en el origen", """
SELECT SUM(amount) AS total FROM sales
""")[0]
    pause()

    # Step 2: the report as anyone would write it
    rows = show(con, "Paso 2 · Informe por región con un JOIN directo", """
SELECT c.region, SUM(s.amount) AS total
FROM sales s
JOIN customers c ON c.customer_id = s.customer_id
GROUP BY c.region
ORDER BY c.region
""")
    compare(sum(r[1] for r in rows), source_total)
    pause()

    # Step 3: the quick fix with DISTINCT
    rows = show(con, "Paso 3 · «Arreglo» con DISTINCT", """
SELECT region, SUM(amount) AS total
FROM (
    SELECT DISTINCT c.region, s.customer_id, s.sale_date, s.amount
    FROM sales s
    JOIN customers c ON c.customer_id = s.customer_id
)
GROUP BY region
ORDER BY region
""")
    compare(sum(r[1] for r in rows), source_total)
    console.print("[yellow]DISTINCT funde las ventas 2 y 3 (legítimas e iguales) y deja a Marta en dos regiones.[/]")
    pause()

    # Step 4: diagnosis, look for the cause instead of hiding the symptom
    show(con, "Paso 4 · ¿Qué clientes aparecen más de una vez?", """
SELECT customer_id, COUNT(*) AS rows_in_customers, GROUP_CONCAT(region) AS regions
FROM customers
GROUP BY customer_id
HAVING COUNT(*) > 1
""")
    console.print("Luis está repetido tal cual; Marta cambió de región (hay dos versiones).")
    pause()

    # Step 5: one row per customer (the most recent version) before the JOIN
    rows = show(con, "Paso 5 · Un cliente por customer_id antes del JOIN", """
WITH latest_customers AS (
    SELECT DISTINCT customer_id, region
    FROM customers c
    WHERE updated_at = (
        SELECT MAX(updated_at) FROM customers c2
        WHERE c2.customer_id = c.customer_id
    )
)
SELECT lc.region, SUM(s.amount) AS total
FROM sales s
JOIN latest_customers lc ON lc.customer_id = s.customer_id
GROUP BY lc.region
ORDER BY lc.region
""")
    report_total = sum(r[1] for r in rows)
    compare(report_total, source_total)
    pause()

    # Step 6: the reconciliation as an automatic check
    console.print()
    console.rule("[bold cyan]Paso 6 · Comprobación de conciliación")
    if report_total == source_total:
        console.print(Panel("El total del informe coincide con el origen.", title="OK", border_style="green"))
    else:
        console.print(Panel(f"El informe suma {report_total} y el origen {source_total}.",
                            title="FALLO", border_style="red"))
    con.close()


if __name__ == "__main__":
    main()

"""Demo 02 · Checks the CSV produced by the assistant against the refined task.

The refined task says: only sale_date changes (day/month/year in, ISO out),
invalid dates are left empty, no other column changes and no row is removed.

This file lives OUTSIDE workspace/ on purpose: the assistant works inside
workspace/ and must not be able to read the expected result.

Usage:  uv run python check_result.py                            (reads workspace/output/sales_clean.csv)
        uv run python check_result.py examples/vague_result.csv  (any other file)
        uv run python check_result.py --reset                    (clean workspace/ between requests)
"""
import csv
import shutil
import sys
from datetime import datetime
from pathlib import Path

from rich.console import Console
from rich.panel import Panel
from rich.table import Table

HERE = Path(__file__).parent
WORKSPACE = HERE / "workspace"
SOURCE = WORKSPACE / "data" / "sales.csv"
DEFAULT_OUTPUT = WORKSPACE / "output" / "sales_clean.csv"
KEEP = {WORKSPACE / "data", SOURCE, WORKSPACE / "output", WORKSPACE / "output" / ".gitkeep"}

console = Console()


def expected_date(text):
    """The business rule: ISO stays as is; otherwise day/month/year. Invalid -> empty."""
    for fmt in ("%Y-%m-%d", "%d/%m/%Y"):
        try:
            return datetime.strptime(text, fmt).strftime("%Y-%m-%d")
        except ValueError:
            continue
    return ""


def read_rows(path):
    with open(path, encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        return reader.fieldnames, {row["sale_id"]: row for row in reader}


def same_number(a, b):
    try:
        return float(a) == float(b)
    except (TypeError, ValueError):
        return False


def reset_workspace():
    """Delete everything the assistant created in workspace/, keeping only the input data."""
    for path in sorted(WORKSPACE.rglob("*"), key=lambda p: len(p.parts), reverse=True):
        if path in KEEP or not path.exists():
            continue
        if path.is_dir():
            shutil.rmtree(path, ignore_errors=True)
        else:
            path.unlink()
        console.print(f"[dim]borrado: {path.relative_to(WORKSPACE)}[/dim]")
    console.print("[green]workspace/ limpio: solo queda data/sales.csv[/]")


def main():
    if "--reset" in sys.argv:
        reset_workspace()
        return
    output_path = Path(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_OUTPUT
    if not output_path.exists():
        sys.exit(f"No encuentro {output_path}. ¿Dónde ha guardado el asistente el resultado?")
    source_columns, source = read_rows(SOURCE)
    output_columns, output = read_rows(output_path)

    table = Table(title=f"Resultado de {output_path.name}")
    for column in ("id", "original", "resultado", "fecha", "otras columnas"):
        table.add_column(column)

    wrong_dates = lost_rows = changed_rows = 0
    for sale_id, original in source.items():
        expected = expected_date(original["sale_date"])
        if sale_id not in output:
            lost_rows += 1
            table.add_row(sale_id, original["sale_date"], "(fila borrada)", "[bold red]MAL[/]",
                          "[bold red]fila perdida[/]", style="red")
            continue
        row = output[sale_id]
        result = (row.get("sale_date") or "").strip()
        date_ok = result == expected
        wrong_dates += not date_ok

        # Out of scope: every other column must be exactly as in the source
        changes = []
        for column in source_columns:
            if column == "sale_date":
                continue
            before, after = original[column], row.get(column)
            if after is None:
                changes.append(f"{column} (falta)")
            elif after != before and not (column == "amount" and same_number(before, after)):
                changes.append(f"{column}: {before!r} → {after!r}")
        changed_rows += bool(changes)

        table.add_row(
            sale_id, original["sale_date"], result or "(vacía)",
            "[green]OK[/]" if date_ok else f"[bold red]MAL[/] (esperado {expected or '(vacía)'})",
            "[green]intactas[/]" if not changes else "[bold red]" + "; ".join(changes) + "[/]",
            style=None if date_ok and not changes else "red",
        )
    console.print(table)

    extra = [c for c in (output_columns or []) if c not in source_columns]
    if extra:
        console.print(f"[bold red]Columnas nuevas fuera de alcance: {', '.join(extra)}[/]")

    console.print(f"Filas: [bold]{len(source) - lost_rows} de {len(source)}[/] conservadas · "
                  f"fechas mal: [bold]{wrong_dates}[/] · filas con otras columnas cambiadas: [bold]{changed_rows}[/]")
    if wrong_dates == lost_rows == changed_rows == 0 and not extra:
        console.print(Panel("Solo ha cambiado la fecha, en ISO, y no falta ninguna fila.",
                            title="Correcto", border_style="green"))
    else:
        console.print(Panel("¿Qué decidió el asistente por su cuenta que no estaba en la tarea?",
                            title="Revisar", border_style="red"))


if __name__ == "__main__":
    main()

"""Demo 06 · Reverting the code does not revert its effects.

Creates _repo/ (a throwaway Git repository) with a script that deletes inactive
customers. An "agent" commit changes the window from 365 to 30 days, the script
runs and deletes active customers. git revert fixes the script, but the deleted
customers only come back by restoring the backup.

Usage:  uv run python run_demo.py            (all at once)
        uv run python run_demo.py --pause    (wait for Enter between steps)
"""
import shutil
import sqlite3
import stat
import subprocess
import sys
from pathlib import Path

from rich.console import Console
from rich.panel import Panel
from rich.syntax import Syntax

HERE = Path(__file__).parent
REPO = HERE / "_repo"
DB = REPO / "shop.db"
BACKUP = REPO / "shop_backup.db"
SCRIPT = "cleanup_inactive.py"
PAUSE = "--pause" in sys.argv

console = Console()

CUSTOMERS = [
    # (customer_id, name, last_purchase)
    (1, "Ana García", "2025-03-15"),   # inactive: more than a year without buying
    (2, "Luis Pérez", "2024-11-02"),   # inactive
    (3, "Marta Ruiz", "2025-06-30"),   # inactive
    (4, "Jorge Sanz", "2026-02-10"),
    (5, "Lucía Mora", "2026-05-21"),
    (6, "Pedro Gil", "2026-07-04"),
    (7, "Elena Vidal", "2026-08-30"),
    (8, "Sara Núñez", "2026-09-20"),
    (9, "Pablo Ortiz", "2026-10-01"),
    (10, "Irene León", "2026-10-05"),
]


def pause():
    if PAUSE:
        console.input("\n[dim]\\[Enter para continuar][/dim] ")


def step(title):
    console.print()
    console.rule(f"[bold cyan]{title}")


def _make_writable(func, path, _exc):
    # On Windows, files inside .git are read-only and rmtree fails without this
    Path(path).chmod(stat.S_IWRITE)
    func(path)


def git(*args):
    return subprocess.run(["git", "--no-pager", *args], cwd=REPO, check=True, capture_output=True, text=True).stdout


def show_customers(expected_ok):
    con = sqlite3.connect(DB)
    (count,) = con.execute("SELECT COUNT(*) FROM customers").fetchone()
    con.close()
    color = "green" if expected_ok else "red"
    console.print(f"Clientes en la base de datos: [bold {color}]{count}[/]")


def run_cleanup():
    console.print(f"[dim]$ python {SCRIPT}[/dim]")
    result = subprocess.run([sys.executable, SCRIPT], cwd=REPO, check=True, capture_output=True, text=True)
    console.print(result.stdout.strip())


def create_repo():
    if REPO.exists():
        shutil.rmtree(REPO, onexc=_make_writable)
    REPO.mkdir()
    shutil.copy2(HERE / "template" / SCRIPT, REPO / SCRIPT)
    con = sqlite3.connect(DB)
    with con:
        con.execute("CREATE TABLE customers (customer_id INTEGER PRIMARY KEY, name TEXT, last_purchase TEXT)")
        con.executemany("INSERT INTO customers VALUES (?, ?, ?)", CUSTOMERS)
    con.close()
    (REPO / ".gitignore").write_text("*.db\n", encoding="utf-8")
    git("-c", "init.defaultBranch=main", "init", "-q")
    git("config", "user.name", "Demo Unidad 3")
    git("config", "user.email", "demo@example.com")
    git("config", "commit.gpgsign", "false")
    git("config", "core.autocrlf", "false")
    git("add", ".")
    git("commit", "-q", "-m", "Limpieza de clientes inactivos (365 días)")


def main():
    create_repo()

    step("Paso 1 · Estado inicial")
    show_customers(expected_ok=True)
    pause()

    step("Paso 2 · Un agente «simplifica» el script y hace commit")
    code = (REPO / SCRIPT).read_text(encoding="utf-8")
    changed = code.replace("INACTIVITY_DAYS = 365", "INACTIVITY_DAYS = 30")
    (REPO / SCRIPT).write_text(changed, encoding="utf-8", newline="\n")  # keep LF so the diff is one line
    git("commit", "-q", "-am", "Simplifica la limpieza de clientes inactivos")
    console.print("[dim]$ git show HEAD[/dim]")
    console.print("Mensaje del commit: [bold]Simplifica la limpieza de clientes inactivos[/]")
    console.print("[yellow]No menciona la ventana de inactividad: solo el diff la revela.[/]")
    diff = git("show", "HEAD", "--format=", "--unified=0", "--", SCRIPT)
    console.print(Syntax(diff.strip(), "diff", theme="ansi_dark"))
    pause()

    step("Paso 3 · Copia de seguridad y ejecución del script del agente")
    shutil.copy2(DB, BACKUP)
    console.print("Copia guardada: [bold]shop_backup.db[/]")
    run_cleanup()
    show_customers(expected_ok=False)
    console.print("[red]Debería haber borrado 3 clientes inactivos y ha borrado 7.[/]")
    pause()

    step("Paso 4 · git revert HEAD")
    console.print("[dim]$ git revert HEAD --no-edit[/dim]")
    git("revert", "HEAD", "--no-edit")
    console.print("El código vuelve a 365 días... pero los clientes siguen borrados:")
    show_customers(expected_ok=False)
    pause()

    step("Paso 5 · Recuperar el estado es otra operación")
    shutil.copy2(BACKUP, DB)
    console.print("Base de datos restaurada desde la copia.")
    show_customers(expected_ok=True)
    pause()

    step("Paso 6 · Ahora sí, el script correcto")
    run_cleanup()
    show_customers(expected_ok=True)
    console.print(Panel("Restaurar el código y recuperar el estado son dos decisiones distintas.",
                        border_style="yellow"))


if __name__ == "__main__":
    main()

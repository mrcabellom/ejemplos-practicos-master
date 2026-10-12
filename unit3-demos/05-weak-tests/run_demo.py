"""Demo 05 · Do the tests really protect the change?

1. Runs the code and both test files: everything passes.
2. Copies the code to _broken/ and removes .lower() from normalize_email().
3. Runs the weak test (still passes) and the strong tests (they fail).

Usage:  uv run python run_demo.py            (all at once)
        uv run python run_demo.py --pause    (wait for Enter between steps)
"""
import os
import shutil
import subprocess
import sys
from pathlib import Path

from rich.console import Console
from rich.panel import Panel
from rich.syntax import Syntax

HERE = Path(__file__).parent
BROKEN = HERE / "_broken"
FILES = ["clean_customers.py", "test_weak.py", "test_strong.py"]
PAUSE = "--pause" in sys.argv

CORRECT_LINE = "return email.strip().lower()"
BROKEN_LINE = "return email.strip()"

console = Console()


def pause():
    if PAUSE:
        console.input("\n[dim]\\[Enter para continuar][/dim] ")


def run(title, *args, cwd=HERE):
    console.print()
    console.rule(f"[bold cyan]{title}")
    hidden = ("-p", "no:cacheprovider", "--tb=no", "-rf")
    shown = [a for a in args if a not in hidden]
    command = " ".join(shown[1:]) if shown[0] == "-m" else "python " + " ".join(shown)
    console.print(f"[dim]$ {command}[/dim]")
    # pytest only colors its output on a terminal; keep it colored when we are on one
    env = {**os.environ, "PY_COLORS": "1"} if console.is_terminal else None
    return subprocess.run([sys.executable, *args], cwd=cwd, env=env).returncode


def main():
    run("Paso 1 · El código correcto", "clean_customers.py")
    run("Paso 2 · Los dos ficheros de tests pasan", "-m", "pytest", "-q", "-p", "no:cacheprovider",
        "test_weak.py", "test_strong.py")
    pause()

    # Inject the defect in a copy so the real code is never touched
    BROKEN.mkdir(exist_ok=True)
    for name in FILES:
        shutil.copy2(HERE / name, BROKEN / name)
    code = (BROKEN / "clean_customers.py").read_text(encoding="utf-8")
    (BROKEN / "clean_customers.py").write_text(code.replace(CORRECT_LINE, BROKEN_LINE), encoding="utf-8")

    console.print()
    console.rule("[bold cyan]Paso 3 · Se inyecta un defecto en normalize_email()")
    console.print(Syntax(f"- {CORRECT_LINE}\n+ {BROKEN_LINE}", "diff", theme="ansi_dark"))
    pause()

    run("Paso 4 · El test débil sigue pasando", "-m", "pytest", "-q", "-p", "no:cacheprovider",
        "test_weak.py", cwd=BROKEN)
    pause()

    run("Paso 5 · Los tests fuertes lo detectan", "-m", "pytest", "-q", "-p", "no:cacheprovider",
        "--tb=no", "-rf", "test_strong.py", cwd=BROKEN)
    pause()

    run("Extra · Emails vacíos", "clean_customers.py", "data/customers_blank.csv")
    console.print(Panel("Hay 4 clientes y salen 3: Pedro y Lucía no tienen email y se fusionan en uno.",
                        border_style="yellow"))


if __name__ == "__main__":
    main()

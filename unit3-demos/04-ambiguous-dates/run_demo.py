"""Demo 04 · Passing tests are not proof that the change is right.

1. Shows the assistant's code, which assumes month/day.
2. Runs the tests the assistant wrote: they pass (verification).
3. Runs the tests written from the data contract: they fail (validation).
4. Fixes the assumption in a copy (_fixed/) and the contract tests pass.

Usage:  uv run python run_demo.py            (all at once)
        uv run python run_demo.py --pause    (wait for Enter between steps)
"""
import shutil
import subprocess
import sys
from pathlib import Path

from rich.console import Console
from rich.panel import Panel
from rich.syntax import Syntax

HERE = Path(__file__).parent
FIXED = HERE / "_fixed"
PAUSE = "--pause" in sys.argv

WRONG_LINE = 'SLASH_FORMAT = "%m/%d/%Y"'
RIGHT_LINE = 'SLASH_FORMAT = "%d/%m/%Y"'

console = Console()


def pause():
    if PAUSE:
        console.input("\n[dim]\\[Enter para continuar][/dim] ")


def step(title):
    console.print()
    console.rule(f"[bold cyan]{title}")


def run_tests(test_module, cwd=HERE):
    console.print(f"[dim]$ python -m unittest {test_module}[/dim]")
    subprocess.run([sys.executable, "-m", "unittest", "-v", test_module], cwd=cwd)


def main():
    step("Paso 1 · El código que escribió el asistente")
    console.print(Syntax((HERE / "parse_sale_date.py").read_text(encoding="utf-8").strip(),
                         "python", theme="ansi_dark", word_wrap=True))
    console.print("[yellow]Supone que «08/10/2026» es mes/día: el 10 de agosto.[/]")
    pause()

    step("Paso 2 · Los tests que escribió el asistente")
    run_tests("test_written_by_assistant")
    console.print("[bold green]✓ Pasan[/]: el código cumple lo que el asistente entendió (verificación).")
    pause()

    step("Paso 3 · Los tests escritos desde el contrato de datos (día/mes/año)")
    run_tests("test_data_contract")
    console.print("[bold red]✗ Fallan[/]: el código no hace lo que el origen necesita (validación).")
    pause()

    step("Paso 4 · Se corrige la suposición")
    FIXED.mkdir(exist_ok=True)
    for name in ("parse_sale_date.py", "test_data_contract.py"):
        shutil.copy2(HERE / name, FIXED / name)
    code = (FIXED / "parse_sale_date.py").read_text(encoding="utf-8")
    (FIXED / "parse_sale_date.py").write_text(code.replace(WRONG_LINE, RIGHT_LINE), encoding="utf-8")
    console.print(Syntax(f"- {WRONG_LINE}\n+ {RIGHT_LINE}", "diff", theme="ansi_dark"))
    run_tests("test_data_contract", cwd=FIXED)
    console.print("[bold green]✓ Pasan[/]")
    console.print(Panel("Los tests del asistente pasaban porque repetían su misma suposición.\n"
                        "Un test en verde solo dice que el código cumple lo que se le preguntó.",
                        border_style="yellow"))


if __name__ == "__main__":
    main()

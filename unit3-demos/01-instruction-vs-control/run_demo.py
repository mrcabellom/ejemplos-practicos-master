"""Demo 01 · An instruction is not a control.

Creates _repo/ (a throwaway Git repository) with an AGENTS.md instruction and a
pre-commit hook as the control. Then it simulates an assistant that writes a
fake token into the code: the instruction does not stop it, the hook does.

Usage:  uv run python run_demo.py            (all at once)
        uv run python run_demo.py --pause    (wait for Enter between steps)
"""
import secrets
import shutil
import stat
import string
import subprocess
import sys
from pathlib import Path

from rich.console import Console
from rich.panel import Panel
from rich.syntax import Syntax

HERE = Path(__file__).parent
TEMPLATE = HERE / "template"
REPO = HERE / "_repo"
PAUSE = "--pause" in sys.argv

console = Console()

LEAKED = '''# Configuración local (generada por el asistente)
GITHUB_TOKEN = "{token}"
'''

FIXED = '''# Configuración local: el token se lee de una variable de entorno
import os

GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN", "")
'''


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


def git(*args, check=True):
    return subprocess.run(["git", *args], cwd=REPO, check=check, capture_output=True, text=True)


def fake_github_token():
    """A made-up token with the shape of a GitHub personal access token."""
    prefix = "gh" + "p_"  # built in two parts so this file is not flagged as a secret
    alphabet = string.ascii_letters + string.digits
    return prefix + "".join(secrets.choice(alphabet) for _ in range(36))


def create_repo():
    if REPO.exists():
        shutil.rmtree(REPO, onexc=_make_writable)
    shutil.copytree(TEMPLATE, REPO)
    git("-c", "init.defaultBranch=main", "init", "-q")
    git("config", "user.name", "Demo Unidad 3")
    git("config", "user.email", "demo@example.com")
    git("config", "commit.gpgsign", "false")
    git("config", "core.autocrlf", "false")
    git("add", ".")
    git("commit", "-q", "-m", "Versión inicial")
    # The control: a pre-commit hook that runs check_secrets.py with this same Python
    hook = REPO / ".git" / "hooks" / "pre-commit"
    hook.write_text(f'#!/bin/sh\nexec "{Path(sys.executable).as_posix()}" check_secrets.py\n', encoding="utf-8")
    hook.chmod(0o755)


def show_file(path):
    console.print(Syntax(path.read_text(encoding="utf-8"), "python", theme="ansi_dark"))


def commit(message):
    console.print(f'[dim]$ git add settings_local.py\n$ git commit -m "{message}"[/dim]')
    git("add", "settings_local.py")
    result = git("commit", "-q", "-m", message, check=False)
    if result.returncode:
        output = (result.stdout + result.stderr).strip()
        console.print(Panel(output, title="Control · pre-commit", border_style="red"))
        console.print("[bold red]✗ Commit bloqueado[/]")
    else:
        console.print("[bold green]✓ Commit realizado[/]")


def main():
    create_repo()

    step("Paso 1 · La instrucción (AGENTS.md)")
    console.print(Panel((REPO / "AGENTS.md").read_text(encoding="utf-8").strip(),
                        title="Instrucción", border_style="blue"))
    pause()

    step("Paso 2 · El asistente escribe un token en el código")
    (REPO / "settings_local.py").write_text(LEAKED.format(token=fake_github_token()), encoding="utf-8")
    show_file(REPO / "settings_local.py")
    commit("Añade configuración local")
    pause()

    step("Paso 3 · Corregido: el token se lee de una variable de entorno")
    (REPO / "settings_local.py").write_text(FIXED, encoding="utf-8")
    show_file(REPO / "settings_local.py")
    commit("Lee el token de una variable de entorno")


if __name__ == "__main__":
    main()

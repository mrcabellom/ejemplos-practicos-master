"""Task runner. Works the same on Windows, macOS and Linux.

    python tasks.py              list the tasks
    python tasks.py all          tests + transform + check
"""

import argparse
import json
import os
import shutil
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent
PYTHON = sys.executable
DELIVERIES = range(2, 7)


def _module(name):
    env = {**os.environ, "PYTHONUTF8": "1"}  # correct accents on Windows too
    return subprocess.call([PYTHON, "-m", name], cwd=ROOT, env=env)


def setup(_):
    """Check the environment."""
    if sys.version_info < (3, 9):
        print("Hace falta Python 3.9 o superior.")
        return 1
    print(f"Python {sys.version.split()[0]} OK. No hay dependencias externas.")
    return 0


def test(_):
    """Run the tests."""
    suite = unittest.TestLoader().discover(str(ROOT / "tests"), top_level_dir=str(ROOT))
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    return 0 if result.wasSuccessful() else 1


def transform(_):
    """Transform the deliveries in inbox/ and write output/."""
    return _module("src.bikes.transform")


def check(_):
    """Check output/ against the contract (0 pass, 1 fail, 2 missing evidence)."""
    return _module("src.bikes.check")


def pipeline(args):
    """Transform and check, in that order."""
    for task in (transform, check):
        code = task(args)
        if code != 0:
            return code
    return 0


def all_tasks(args):
    """Tests, transform and check, in that order."""
    code = test(args)
    return code if code != 0 else pipeline(args)


def reset(_):
    """Delete the output (output/)."""
    target = ROOT / "output"
    if target.exists():
        shutil.rmtree(target)
        print("Borrado output/")
    else:
        print("Nada que borrar.")
    return 0


def deliver(args):
    """Simulate the operator: drop delivery N in inbox/ and its ticket in docs/tickets/."""
    n = args.n
    if n not in DELIVERIES:
        print(f"No hay entrega {n}: van de la {DELIVERIES[0]} a la {DELIVERIES[-1]}.")
        return 1
    source = ROOT / "deliveries"
    shutil.copy(source / f"week-{n}.csv", ROOT / "inbox" / f"week-{n}.csv")
    shutil.copy(source / f"OPS-10{n}.md", ROOT / "docs" / "tickets" / f"OPS-10{n}.md")
    print(f"Entregado inbox/week-{n}.csv y docs/tickets/OPS-10{n}.md")
    return 0


def mcp_check(_):
    """Talk to the MCP server directly, without Claude Code."""
    messages = [
        {"jsonrpc": "2.0", "id": 1, "method": "initialize",
         "params": {"protocolVersion": "2025-06-18", "capabilities": {},
                    "clientInfo": {"name": "tasks.py", "version": "1"}}},
        {"jsonrpc": "2.0", "id": 2, "method": "tools/list"},
        {"jsonrpc": "2.0", "id": 3, "method": "tools/call",
         "params": {"name": "profile_csv", "arguments": {"path": "inbox/week-1.csv"}}},
    ]
    stdin = "\n".join(json.dumps(m) for m in messages) + "\n"
    proc = subprocess.run([PYTHON, str(ROOT / "mcp_server" / "server.py")],
                          input=stdin, capture_output=True, text=True,
                          encoding="utf-8", cwd=ROOT)
    for line in proc.stdout.splitlines():
        result = json.loads(line).get("result", {})
        if "serverInfo" in result:
            print(f"initialize  OK  {result['serverInfo']['name']}")
        elif "tools" in result:
            print(f"tools/list  OK  {[t['name'] for t in result['tools']]}")
        elif "content" in result:
            print("tools/call  OK")
            print(result["content"][0]["text"])
    return 0 if proc.stdout else 1


def sample_env(_):
    """Create a sample .env for the permissions exercise."""
    shutil.copy(ROOT / "security" / ".env.example", ROOT / ".env")
    print("Creado .env (de muestra). Está en .gitignore.")
    return 0


TASKS = {
    "setup": setup,
    "test": test,
    "transform": transform,
    "check": check,
    "pipeline": pipeline,
    "all": all_tasks,
    "reset": reset,
    "deliver": deliver,
    "mcp-check": mcp_check,
    "sample-env": sample_env,
}


def main():
    parser = argparse.ArgumentParser(description="Project tasks.")
    sub = parser.add_subparsers(dest="task")
    for name, function in TASKS.items():
        command = sub.add_parser(name, help=function.__doc__)
        command.set_defaults(function=function)
        if name == "deliver":
            command.add_argument("n", type=int, help="delivery number (2-6)")
    args = parser.parse_args()
    if args.task is None:
        parser.print_help()
        return 0
    os.chdir(ROOT)
    sys.stdout.reconfigure(encoding="utf-8")
    return args.function(args)


if __name__ == "__main__":
    sys.exit(main())

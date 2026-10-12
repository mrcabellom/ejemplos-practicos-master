"""Task runner for this project.

Usage:
    python tasks.py                     list the available tasks
    python tasks.py run --date 2026-03-01
    python tasks.py check

On Windows use `python`; on macOS and Linux `python3` may be required.
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
DB = ROOT / "warehouse.db"
PYTHON = sys.executable  # the interpreter running this file, whatever its name
EXTRACT_DATES = ("2026-03-01", "2026-03-02", "2026-03-03")


def _run_module(module, *args):
    """Run a project module in a child process and return its exit code."""
    return subprocess.call([PYTHON, "-m", module, *args], cwd=ROOT)


def setup(_args):
    """Check the environment is ready."""
    if sys.version_info < (3, 9):
        print("Python 3.9 or newer is required.")
        return 1

    print(f"Python {sys.version.split()[0]} OK. No third-party packages needed.")
    return 0


def run(args):
    """Load one extract date. Needs --date YYYY-MM-DD."""
    return _run_module("src.pipeline.load", "--date", args.date)


def run_all(_args):
    """Load the three extracts available in data/raw/."""
    for date in EXTRACT_DATES:
        code = _run_module("src.pipeline.load", "--date", date)
        if code != 0:
            return code
    return 0


def occupancy(_args):
    """Print the provisional occupancy report the dashboard reads."""
    return _run_module("src.pipeline.occupancy")


def reconcile(_args):
    """Compare the warehouse against its declared contract."""
    return _run_module("src.pipeline.reconcile")


def acceptance(_args):
    """Check the load against the contract on throwaway warehouses."""
    return _run_module("src.pipeline.acceptance")


def test(_args):
    """Run the test suite."""
    loader = unittest.TestLoader()
    suite = loader.discover(start_dir=str(ROOT / "tests"), top_level_dir=str(ROOT))
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    return 0 if result.wasSuccessful() else 1


def check(_args):
    """Run the tests and then the reconciliation."""
    code = test(_args)
    if code != 0:
        return code
    return reconcile(_args)


def reset(_args):
    """Delete the local warehouse."""
    if DB.exists():
        DB.unlink()
        print(f"Deleted {DB.name}")
    else:
        print("Nothing to delete.")
    return 0


def mcp_check(_args):
    """Talk to the MCP server directly, without any agent."""
    messages = [
        {"jsonrpc": "2.0", "id": 1, "method": "initialize",
         "params": {"protocolVersion": "2025-06-18", "capabilities": {},
                    "clientInfo": {"name": "tasks.py", "version": "1"}}},
        {"jsonrpc": "2.0", "id": 2, "method": "tools/list"},
        {"jsonrpc": "2.0", "id": 3, "method": "tools/call",
         "params": {"name": "grain_health", "arguments": {}}},
    ]
    payload = "\n".join(json.dumps(m) for m in messages) + "\n"

    proc = subprocess.run(
        [PYTHON, str(ROOT / "mcp_server" / "server.py")],
        input=payload, capture_output=True, text=True, cwd=ROOT,
    )

    for line in proc.stdout.splitlines():
        reply = json.loads(line).get("result", {})
        if "serverInfo" in reply:
            print(f"initialize   OK  {reply['serverInfo']} protocol {reply['protocolVersion']}")
        elif "tools" in reply:
            print(f"tools/list   OK  {[t['name'] for t in reply['tools']]}")
        elif "content" in reply:
            print("tools/call   OK")
            print(reply["content"][0]["text"])
    return 0 if proc.stdout else 1


def sample_env(_args):
    """Create a sample .env, with no real credentials, for the exposure check."""
    shutil.copy(ROOT / "security" / ".env.example", ROOT / ".env")
    print("Created .env (sample values, no real credentials).")
    print("It is listed in .gitignore, so it will not be committed by mistake.")
    return 0


TASKS = {
    "setup": setup,
    "run": run,
    "run-all": run_all,
    "occupancy": occupancy,
    "reconcile": reconcile,
    "acceptance": acceptance,
    "test": test,
    "check": check,
    "reset": reset,
    "mcp-check": mcp_check,
    "sample-env": sample_env,
}


def main():
    parser = argparse.ArgumentParser(description="Run project tasks.")
    commands = parser.add_subparsers(dest="command")
    for name, task in TASKS.items():
        command = commands.add_parser(name, help=task.__doc__.splitlines()[0])
        command.set_defaults(handler=task)
        if name == "run":
            command.add_argument("--date", required=True, metavar="YYYY-MM-DD")

    args = parser.parse_args()
    if args.command is None:
        parser.print_help()
        return 0
    os.chdir(ROOT)
    return args.handler(args)


if __name__ == "__main__":
    try:
        sys.exit(main())
    except BrokenPipeError:
        sys.exit(0)
    except KeyboardInterrupt:
        sys.exit(130)

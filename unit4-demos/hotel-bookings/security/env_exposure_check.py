"""Check whether a child process can read .env despite the agent's deny rule.

`.claude/settings.json` denies `Read(./.env)`, so the agent cannot open that
file with its own file tools. This script reads it as a child process, the
way any command the agent launches would. If it prints the contents, the
deny rule did not stop it: the rule governs the agent's tools, not the
processes it launches.

Operating system isolation (the sandbox) is what actually stops this.

Usage:
    python tasks.py sample-env
    python security/env_exposure_check.py
"""

import pathlib
import sys

path = pathlib.Path(".env")

if not path.exists():
    print("No .env found. Run 'python tasks.py sample-env' first.")
    sys.exit(1)

print("Contents of .env read from a child process:")
print("-" * 52)
print(path.read_text(encoding="utf-8").strip())
print("-" * 52)
print()
print("EXPOSED: the deny rule did not intervene.")
print("The rule protects the agent's tools, not this process.")

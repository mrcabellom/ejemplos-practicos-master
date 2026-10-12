"""PreToolUse hook: block destructive SQL in shell commands.

Registered for both the Bash and the PowerShell tools: on Windows Claude
Code may use either, and a hook that only matches Bash leaves a gap.

It only looks at the TEXT of the command: the same statement inside a
script, or written differently, gets through.
A hook like this prevents accidents; it is not a security boundary.

Exit code 2 blocks the command, and stderr is shown to the agent as the reason.
"""

import json
import sys


def is_destructive(command):
    sql = command.upper()
    if "DROP TABLE" in sql:
        return "DROP TABLE"
    if "TRUNCATE TABLE" in sql:
        return "TRUNCATE TABLE"
    if "DELETE FROM" in sql and "WHERE" not in sql:
        return "DELETE without WHERE"
    return None


def main():
    try:
        event = json.load(sys.stdin)
    except json.JSONDecodeError:
        return 0

    command = (event.get("tool_input") or {}).get("command", "")
    found = is_destructive(command)
    if found:
        print(
            f"Blocked: the command contains {found}. "
            "See docs/runbooks/backfill.md for the authorised procedure.",
            file=sys.stderr,
        )
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())

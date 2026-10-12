"""Copilot version of the destructive SQL hook.

Same three rules as .claude/hooks/block_destructive_sql.py. Accepts the
Copilot CLI payload (toolArgs) and the VS Code Local one (tool_input). Safe
commands leave the normal permissions unchanged; destructive ones are denied.
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
        if not isinstance(event, dict):
            raise ValueError("Expected a JSON event object.")
        arguments = event.get("tool_input", event.get("toolArgs", {}))
        if isinstance(arguments, str):
            arguments = json.loads(arguments)
        if not isinstance(arguments, dict):
            raise ValueError("Expected a JSON tool arguments object.")
        command = arguments.get("command", "")
        if not isinstance(command, str):
            raise ValueError("Expected a string command.")
    except (ValueError, TypeError) as error:
        print(f"Invalid hook input: {error}", file=sys.stderr)
        return 2

    found = is_destructive(command)
    if not found:
        print("{}")
        return 0

    decision = {
        "permissionDecision": "deny",
        "permissionDecisionReason": f"Blocked: the command contains {found}.",
    }
    if "tool_input" in event or "tool_name" in event:
        decision["hookEventName"] = "PreToolUse"
        print(json.dumps({"hookSpecificOutput": decision}))
    else:
        print(json.dumps(decision))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

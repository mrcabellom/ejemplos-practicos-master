"""Cursor version of the destructive SQL hook.

Same three rules as .claude/hooks/block_destructive_sql.py, adapted to how
Cursor talks to its hooks: the command arrives as {"command": "..."} and the
decision is returned as JSON on stdout instead of an exit code.
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


event = json.load(sys.stdin)
found = is_destructive(event.get("command", ""))

if found:
    reason = f"Blocked: the command contains {found}."
    print(json.dumps({"permission": "deny", "user_message": reason, "agent_message": reason}))
else:
    print(json.dumps({"permission": "allow"}))

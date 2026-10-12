"""PreToolUse hook: stops deliveries or outputs being deleted from the terminal.

It only looks at the TEXT of the command. That is its limit:
`python tasks.py reset` deletes output/ and the hook misses it: the deletion
happens inside the script. It prevents accidents; it is not a security barrier.
"""

import json
import sys

sys.stderr.reconfigure(encoding="utf-8")

DELETE_COMMANDS = ("rm ", "del ", "rmdir ", "remove-item", "erase ")
FOLDERS = ("inbox/", "deliveries/", "output/")

event = json.load(sys.stdin)
command = (event.get("tool_input") or {}).get("command", "")
text = command.lower().replace("\\", "/")

if any(f in text for f in FOLDERS) and any(c in text for c in DELETE_COMMANDS):
    print("Bloqueado: el comando borra entregas o salidas. "
          "Para regenerar output/ usa `python tasks.py reset` y `pipeline`.",
          file=sys.stderr)
    sys.exit(2)

sys.exit(0)

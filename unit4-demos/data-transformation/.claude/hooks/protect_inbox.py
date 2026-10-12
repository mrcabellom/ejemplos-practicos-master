"""PreToolUse hook: stops any file in inbox/ or deliveries/ being edited.

AGENTS.md says incoming data is not touched, but an instruction is not a
block. This hook is: it runs before the tool and, if it exits with code 2,
the edit does not happen. What it prints on stderr reaches Claude as the
reason.
"""

import json
import sys

sys.stderr.reconfigure(encoding="utf-8")

PROTECTED = ("inbox/", "deliveries/")

event = json.load(sys.stdin)
tool_input = event.get("tool_input") or {}
path = (tool_input.get("file_path") or tool_input.get("notebook_path") or "").replace("\\", "/")

if any(folder in path for folder in PROTECTED):
    print(f"Bloqueado: {path} es una entrega y no se modifica. "
          "Adapta la transformación en src/bikes/, no los datos.",
          file=sys.stderr)
    sys.exit(2)

sys.exit(0)

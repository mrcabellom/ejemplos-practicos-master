"""PreToolUse hook: prevent writes to the source data and to the oracle.

The source data is immutable. AGENTS.md says so, but an instruction is not
a boundary: this hook is one, because it runs before the tool and exit
code 2 blocks the operation.

The acceptance check is protected for a different reason: it is the
completion condition of an agent goal. An agent that could edit it could
make the goal pass without fixing anything.

Reads the event JSON from stdin and returns the reason on stderr.
"""

import json
import sys

PROTECTED_PATHS = ("data/raw/", "data/reference/")
ORACLE = "src/pipeline/acceptance.py"


def main():
    try:
        event = json.load(sys.stdin)
    except json.JSONDecodeError:
        return 0

    tool_input = event.get("tool_input") or {}
    path = (
        tool_input.get("file_path")
        or tool_input.get("path")
        or tool_input.get("notebook_path")
        or ""
    )
    path = path.replace("\\", "/")

    for protected in PROTECTED_PATHS:
        if protected in path:
            print(
                f"Blocked: {path} lives in the immutable source ({protected}). "
                "Extracts and reference data are never modified. If you need a "
                "different fixture, create it under tests/.",
                file=sys.stderr,
            )
            return 2

    if path.endswith(ORACLE):
        print(
            f"Blocked: {ORACLE} is the acceptance check. It defines when the "
            "work is done, so it is changed by a person, not by the agent "
            "working towards it. Fix the code under test instead.",
            file=sys.stderr,
        )
        return 2

    return 0


if __name__ == "__main__":
    sys.exit(main())

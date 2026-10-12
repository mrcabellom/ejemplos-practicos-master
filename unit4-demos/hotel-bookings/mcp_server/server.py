"""Read-only MCP server over the bookings warehouse.

Speaks JSON-RPC 2.0 over stdin/stdout, which is the MCP stdio transport.
No external dependencies: standard library only, so it runs the same on
Windows, macOS and Linux.

It is declared in .mcp.json, so Claude Code offers it when the project is
opened. To check it inside a session:

    /mcp

To check it without any agent:

    python tasks.py mcp-check

It deliberately exposes no write tools and no free-form SQL. The agent gets
metadata and health checks about the warehouse, not a database console.
"""

import json
import os
import sqlite3
import sys

DB = os.environ.get("BOOKINGS_DB", "warehouse.db")
HOTELS_FILE = os.path.join("data", "reference", "hotels.json")
DEFAULT_PROTOCOL = "2025-06-18"

ALLOWED_TABLES = {"fct_bookings", "quarantine", "run_log"}
ROW_LIMIT = 20


def log(message):
    """Traces go to stderr: stdout belongs to the protocol alone."""
    print(f"[bookings-warehouse] {message}", file=sys.stderr, flush=True)


def connect():
    if not os.path.exists(DB):
        raise RuntimeError(
            f"Warehouse not found ({DB}). Run 'python tasks.py run-all' first."
        )
    con = sqlite3.connect(f"file:{DB}?mode=ro", uri=True)
    con.row_factory = sqlite3.Row
    return con


# ---------------------------------------------------------------------------
# Exposed tools
# ---------------------------------------------------------------------------

def list_tables(_args):
    con = connect()
    found = con.execute(
        "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"
    ).fetchall()
    out = []
    for item in found:
        name = item["name"]
        if name not in ALLOWED_TABLES:
            continue
        count = con.execute(f"SELECT COUNT(*) FROM {name}").fetchone()[0]
        out.append({"table": name, "rows": count})
    con.close()
    return out


def describe_table(args):
    name = args.get("table", "")
    if name not in ALLOWED_TABLES:
        raise ValueError(f"Table not allowed: {name!r}. Available: {sorted(ALLOWED_TABLES)}")
    con = connect()
    columns = [
        {"column": c["name"], "type": c["type"]}
        for c in con.execute(f"PRAGMA table_info({name})")
    ]
    count = con.execute(f"SELECT COUNT(*) FROM {name}").fetchone()[0]
    con.close()
    return {"table": name, "rows": count, "columns": columns}


def freshness(_args):
    con = connect()
    by_date = con.execute(
        "SELECT business_date, COUNT(*) n, MAX(updated_at) latest "
        "FROM fct_bookings GROUP BY business_date ORDER BY business_date"
    ).fetchall()
    runs = con.execute(
        "SELECT run_id, extract_date, executed_at, rows_read, rows_written, rows_rejected "
        "FROM run_log ORDER BY executed_at DESC LIMIT 5"
    ).fetchall()
    con.close()
    return {
        "by_business_date": [dict(r) for r in by_date],
        "latest_runs": [dict(r) for r in runs],
    }


def grain_health(_args):
    """Check the grain declared in the contract without returning business data."""
    con = connect()
    total = con.execute("SELECT COUNT(*) FROM fct_bookings").fetchone()[0]
    keys = con.execute("SELECT COUNT(DISTINCT booking_id) FROM fct_bookings").fetchone()[0]
    duplicates = con.execute(
        "SELECT booking_id, COUNT(*) times, GROUP_CONCAT(status) statuses "
        "FROM fct_bookings GROUP BY booking_id HAVING times > 1 "
        "ORDER BY booking_id LIMIT ?",
        (ROW_LIMIT,),
    ).fetchall()
    con.close()
    return {
        "rows": total,
        "distinct_keys": keys,
        "grain_holds": total == keys,
        "duplicate_keys": [dict(d) for d in duplicates],
    }


def capacity_check(_args):
    """Nights where confirmed rooms exceed the hotel capacity."""
    with open(HOTELS_FILE, encoding="utf-8") as f:
        capacity = {h["hotel_id"]: h["rooms"] for h in json.load(f)}
    con = connect()
    found = con.execute(
        """
        WITH RECURSIVE stay(hotel_id, night, check_out, rooms) AS (
            SELECT hotel_id, check_in, check_out, rooms
            FROM fct_bookings WHERE status = 'confirmed'
            UNION ALL
            SELECT hotel_id, date(night, '+1 day'), check_out, rooms
            FROM stay WHERE date(night, '+1 day') < check_out
        )
        SELECT hotel_id, night, SUM(rooms) rooms
        FROM stay GROUP BY hotel_id, night ORDER BY hotel_id, night
        """
    ).fetchall()
    con.close()
    over = [
        {**dict(r), "capacity": capacity[r["hotel_id"]]}
        for r in found
        if r["rooms"] > capacity.get(r["hotel_id"], 0)
    ]
    return {"nights_over_capacity": over[:ROW_LIMIT]}


def quarantine_summary(_args):
    con = connect()
    found = con.execute(
        "SELECT reason_code, COUNT(*) n FROM quarantine "
        "GROUP BY reason_code ORDER BY n DESC LIMIT ?",
        (ROW_LIMIT,),
    ).fetchall()
    con.close()
    return {"reasons": [dict(r) for r in found]}


TOOLS = {
    "list_tables": {
        "fn": list_tables,
        "description": "List the warehouse tables with their row counts.",
        "inputSchema": {"type": "object", "properties": {}},
    },
    "describe_table": {
        "fn": describe_table,
        "description": "Return columns, types and row count for one table.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "table": {
                    "type": "string",
                    "description": "Table name",
                    "enum": sorted(ALLOWED_TABLES),
                }
            },
            "required": ["table"],
        },
    },
    "freshness": {
        "fn": freshness,
        "description": "Volume per business date and the latest recorded runs.",
        "inputSchema": {"type": "object", "properties": {}},
    },
    "grain_health": {
        "fn": grain_health,
        "description": (
            "Check whether fct_bookings holds the grain declared in its contract: "
            "one row per booking_id. Returns the duplicate keys and their statuses."
        ),
        "inputSchema": {"type": "object", "properties": {}},
    },
    "capacity_check": {
        "fn": capacity_check,
        "description": (
            "List the hotel nights where the confirmed rooms in fct_bookings "
            "exceed the capacity declared in data/reference/hotels.json."
        ),
        "inputSchema": {"type": "object", "properties": {}},
    },
    "quarantine_summary": {
        "fn": quarantine_summary,
        "description": "Count of rejected rows grouped by reason code.",
        "inputSchema": {"type": "object", "properties": {}},
    },
}


# ---------------------------------------------------------------------------
# Protocol
# ---------------------------------------------------------------------------

def respond(id_, result=None, error=None):
    message = {"jsonrpc": "2.0", "id": id_}
    if error is not None:
        message["error"] = error
    else:
        message["result"] = result
    sys.stdout.write(json.dumps(message, ensure_ascii=False) + "\n")
    sys.stdout.flush()


def handle(request):
    method = request.get("method")
    id_ = request.get("id")
    params = request.get("params") or {}

    # Notifications carry no id and get no response.
    if id_ is None:
        return

    if method == "initialize":
        respond(id_, {
            "protocolVersion": params.get("protocolVersion") or DEFAULT_PROTOCOL,
            "capabilities": {"tools": {}},
            "serverInfo": {"name": "bookings-warehouse", "version": "1.0.0"},
        })

    elif method == "tools/list":
        respond(id_, {
            "tools": [
                {"name": name, "description": meta["description"],
                 "inputSchema": meta["inputSchema"]}
                for name, meta in TOOLS.items()
            ]
        })

    elif method == "tools/call":
        name = params.get("name")
        meta = TOOLS.get(name)
        if meta is None:
            respond(id_, {
                "content": [{"type": "text", "text": f"Unknown tool: {name}"}],
                "isError": True,
            })
            return
        try:
            data = meta["fn"](params.get("arguments") or {})
            respond(id_, {
                "content": [{"type": "text",
                             "text": json.dumps(data, ensure_ascii=False, indent=2)}]
            })
        except Exception as exc:  # noqa: BLE001
            log(f"error in {name}: {exc}")
            respond(id_, {
                "content": [{"type": "text", "text": f"Error: {exc}"}],
                "isError": True,
            })

    elif method in ("resources/list", "prompts/list"):
        respond(id_, {method.split("/")[0]: []})

    else:
        respond(id_, error={"code": -32601, "message": f"Unsupported method: {method}"})


def main():
    log(f"started on {DB}")
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            request = json.loads(line)
        except json.JSONDecodeError as exc:
            log(f"invalid json: {exc}")
            continue
        try:
            handle(request)
        except Exception as exc:  # noqa: BLE001
            log(f"unexpected failure: {exc}")
            if request.get("id") is not None:
                respond(request["id"], error={"code": -32603, "message": str(exc)})


if __name__ == "__main__":
    main()

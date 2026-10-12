"""Minimal, read-only MCP server that summarises the project's CSV files.

It speaks JSON-RPC over stdio (one line per message) and only uses the
standard library. What it is for: Claude gets a summary of a delivery
without loading the whole file into its context.

Tools:
    profile_csv(path)     rows, columns, empty and distinct values
    duration_stats(path)  trip duration: minimum, median, maximum...
"""

import csv
import json
import statistics
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ALLOWED = (ROOT / "inbox", ROOT / "output")
ISO = "%Y-%m-%dT%H:%M"

PATH_SCHEMA = {
    "type": "object",
    "properties": {"path": {"type": "string", "description": "Ej.: inbox/week-1.csv"}},
    "required": ["path"],
}
TOOLS = [
    {"name": "profile_csv",
     "description": "Perfil de un CSV de inbox/ u output/: filas, columnas, vacíos y "
                    "valores distintos por columna. No devuelve las filas.",
     "inputSchema": PATH_SCHEMA},
    {"name": "duration_stats",
     "description": "Estadísticas de duración (minutos) de los viajes de un CSV de "
                    "inbox/ u output/: mínimo, mediana, máximo, cuántos no son positivos, "
                    "cuántos superan 240 y cuántos tienen fechas que no son ISO.",
     "inputSchema": PATH_SCHEMA},
]


def read_csv(path):
    file = (ROOT / path).resolve()
    if not any(folder in file.parents for folder in ALLOWED):
        raise ValueError("Solo se pueden leer archivos de inbox/ u output/.")
    if not file.exists():
        raise ValueError(f"No existe {path}.")
    with open(file, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def profile_csv(path):
    rows = read_csv(path)
    columns = list(rows[0].keys()) if rows else []
    return {
        "rows": len(rows),
        "columns": {c: {"empty": sum(1 for r in rows if not r[c].strip()),
                        "distinct": len({r[c].strip() for r in rows})} for c in columns},
    }


def duration_stats(path):
    minutes, not_iso = [], 0
    for r in read_csv(path):
        try:
            start = datetime.strptime(r["start_time"], ISO)
            end = datetime.strptime(r["end_time"], ISO)
        except ValueError:
            not_iso += 1
            continue
        minutes.append(int((end - start).total_seconds() // 60))
    if not minutes:
        return {"trips": 0, "not_iso": not_iso}
    return {
        "trips": len(minutes), "not_iso": not_iso,
        "min": min(minutes), "median": statistics.median(minutes), "max": max(minutes),
        "non_positive": sum(1 for m in minutes if m <= 0),
        "over_240": sum(1 for m in minutes if m > 240),
    }


def call(name, arguments):
    if name == "profile_csv":
        return profile_csv(arguments["path"])
    if name == "duration_stats":
        return duration_stats(arguments["path"])
    raise ValueError(f"Herramienta desconocida: {name}")


def reply(message):
    method = message.get("method")
    if method == "initialize":
        version = message.get("params", {}).get("protocolVersion", "2025-06-18")
        return {"protocolVersion": version, "capabilities": {"tools": {}},
                "serverInfo": {"name": "bike-data", "version": "1.0"}}
    if method == "tools/list":
        return {"tools": TOOLS}
    if method == "tools/call":
        params = message.get("params", {})
        try:
            data = call(params.get("name"), params.get("arguments") or {})
            text, error = json.dumps(data, ensure_ascii=False, indent=2), False
        except (ValueError, KeyError) as e:
            text, error = f"Error: {e}", True
        return {"content": [{"type": "text", "text": text}], "isError": error}
    if method == "ping":
        return {}
    return None


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    for line in sys.stdin:
        if not line.strip():
            continue
        message = json.loads(line)
        if "id" not in message:  # notification: no reply
            continue
        result = reply(message)
        if result is None:
            out = {"jsonrpc": "2.0", "id": message["id"],
                   "error": {"code": -32601, "message": "Método no soportado"}}
        else:
            out = {"jsonrpc": "2.0", "id": message["id"], "result": result}
        print(json.dumps(out, ensure_ascii=False), flush=True)


if __name__ == "__main__":
    main()

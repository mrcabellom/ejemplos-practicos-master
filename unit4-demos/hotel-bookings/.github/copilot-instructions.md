# Instrucciones para GitHub Copilot

Las instrucciones generales están en `AGENTS.md`, que Copilot también lee.
Aquí solo va lo específico de Copilot.

- Para consultar el almacén usa el servidor MCP `bookings-warehouse`
  declarado en `.vscode/mcp.json`. No uses `sqlite3` por terminal.
- Para validar un cambio, usa el prompt `/validate-pipeline`.
- Para revisar un cambio contra el contrato, usa el agente
  `data-quality-reviewer`.
- `data/raw/` y `data/reference/` son inmutables. En Copilot esta
  protección es solo una instrucción: no hay un hook que bloquee la edición.

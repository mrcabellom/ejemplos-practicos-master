@AGENTS.md

## Específico de Claude Code

- Antes de dar por terminado un cambio en `src/bikes/`, usa el skill
  `check-delivery`.
- Para revisar un cambio contra el contrato, delega en el subagente
  `data-reviewer`.
- Para conocer la forma de un CSV, usa el servidor MCP `bike-data` en lugar
  de leer el archivo entero.

## Contexto

El estado del trabajo vive en `docs/plans/status.md` (plantilla en
`docs/plans/STATUS-TEMPLATE.md`). Antes de compactar o de cerrar la sesión,
actualízalo: objetivo, decisiones, evidencia y siguiente paso. Lo que no
esté ahí puede perderse.

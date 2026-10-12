@AGENTS.md

## Específico de Claude Code

La primera línea importa `AGENTS.md` al iniciar la sesión. Escribir «lee
AGENTS.md» no sería suficiente: solo funcionaría si el agente decidiera
abrirlo.

- Para consultar el almacén usa el servidor MCP `bookings-warehouse`.
  `sqlite3` está denegado en los permisos.
- Antes de dar por terminado un cambio en `src/pipeline/`, invoca el skill
  `validate-pipeline`.
- Para revisar un cambio contra el contrato, delega en el subagente
  `data-quality-reviewer`.
- Trabaja en una rama. `main` se mantiene desplegable.

## Contexto largo

Antes de compactar, actualiza `docs/plans/status.md` con el objetivo, las
decisiones, la evidencia y el siguiente paso. Lo que no quede ahí se
pierde.

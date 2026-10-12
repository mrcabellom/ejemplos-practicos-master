# Otras herramientas

La herramienta principal del equipo es Claude Code, pero el repositorio
está preparado para que GitHub Copilot, Cursor y OpenCode trabajen sobre el
mismo código. Lo relevante no es en qué coinciden, sino **en qué se
diferencian**.

## Qué lee cada una

| | Claude Code | GitHub Copilot | Cursor | OpenCode |
| --- | --- | --- | --- | --- |
| Instrucciones generales | `CLAUDE.md`, que importa `AGENTS.md` con `@AGENTS.md` | `AGENTS.md` y `.github/copilot-instructions.md` | `AGENTS.md` y `.cursor/rules/000-project.mdc` | `AGENTS.md` |
| Instrucciones por ruta | `.claude/rules/pipeline.md` con `paths:` | `.github/instructions/pipeline.instructions.md` con `applyTo:` | `.cursor/rules/100-pipeline.mdc` con `globs:` | `AGENTS.md` anidado |
| Procedimiento reutilizable | Skill en `.claude/skills/` | Prompt en `.github/prompts/` | — | Comando en `.opencode/commands/` |
| Subagente revisor | `.claude/agents/` | `.github/agents/` | — | `.opencode/agents/` |
| Servidor MCP | `.mcp.json` | `.vscode/mcp.json` | `.cursor/mcp.json` | `opencode.json` |
| Permisos | `.claude/settings.json` | Configuración del editor | Configuración del editor | `opencode.json` |
| Hooks | `.claude/settings.json` | `.github/hooks/*.json` | `.cursor/hooks.json` | — |

Todas usan **el mismo servidor MCP**, `mcp_server/server.py`. Solo cambian
el archivo en el que se declara y el nombre de alguna clave.

### Claude Code y `AGENTS.md`

Claude Code lee `AGENTS.md` por sí solo **únicamente si no hay ningún
`CLAUDE.md`**. Este repositorio tiene `CLAUDE.md`, así que lo importa con
`@AGENTS.md` en la primera línea. Escribir «lee AGENTS.md antes de nada» no
es equivalente: el contenido solo entra en el contexto si el agente decide
abrir el archivo.

## Protecciones: bloqueo o instrucción

| Protección | Claude Code | GitHub Copilot | Cursor | OpenCode |
| --- | --- | --- | --- | --- |
| No editar `data/raw/` | Hook previo a la edición: **bloquea** | Solo instrucción | Solo regla | Permiso `edit: ask` |
| No ejecutar `DROP TABLE` | Hook en Bash y PowerShell: **bloquea** | Hook `preToolUse`: **bloquea** | Hook `beforeShellExecution`: **bloquea** | — |
| No usar `sqlite3` | Regla `deny`: **bloquea** | Configuración del editor | Configuración del editor | Permiso `deny`: **bloquea** |
| No leer `.env` | Regla `deny` sobre `Read`: **bloquea la herramienta, no los procesos hijo** | Configuración del editor | Configuración del editor | Configuración de permisos |

La misma regla escrita en cuatro archivos no ofrece la misma garantía.
Donde solo hay una instrucción, el resultado depende de que el agente
decida seguirla.

## El mismo hook en tres herramientas

| | Claude Code | GitHub Copilot | Cursor |
| --- | --- | --- | --- |
| Archivo | `.claude/hooks/block_destructive_sql.py` | `.github/hooks/block_destructive_sql.py` | `.cursor/hooks/block_destructive_sql.py` |
| Evento recibido | `{"tool_input": {"command": "..."}}` | `toolArgs` en CLI; `tool_input` en VS Code | `{"command": "..."}` |
| Cómo bloquea | Código de salida 2 y motivo en stderr | JSON con `permissionDecision: "deny"` | JSON con `"permission": "deny"` |

Los tres se pueden probar sin abrir ninguna herramienta:

```powershell
'{"tool_input":{"command":"DROP TABLE fct_bookings"}}' | python .claude/hooks/block_destructive_sql.py
'{"command":"DROP TABLE fct_bookings"}' | python .cursor/hooks/block_destructive_sql.py
'{"toolName":"powershell","toolArgs":{"command":"DROP TABLE fct_bookings"}}' | python .github/hooks/block_destructive_sql.py
```

Los tres analizan el texto del comando, no el contenido de los scripts que
ejecuta. Evitan accidentes, pero no sustituyen al aislamiento del sistema
operativo.

## Comprobaciones previas

Estas herramientas cambian con frecuencia. En la versión instalada,
conviene comprobar:

- **Claude Code:** que `/mcp` muestra `bookings-warehouse`, que `/memory`
  lista `AGENTS.md` como importado y que `/hooks` muestra los dos hooks.
- **Copilot:** que VS Code detecta `.vscode/mcp.json` y los agentes de
  `.github/agents/`, y que los hooks están habilitados (`chat.useHooks`).
- **Cursor:** el nombre del evento `beforeShellExecution` y la forma de la
  respuesta del hook.
- **OpenCode:** la sintaxis y el orden de los patrones en `permission.bash`.

# Referencia de comandos · OpenSpec 1.14

## En el chat de Claude Code

### Perfil `core` (predeterminado)

| Comando | Función | Escribe código |
|---|---|---|
| `/opsx:explore [tema]` | Analizar un problema, investigar y comparar opciones | No |
| `/opsx:propose <nombre o idea>` | Crea el change y **todos** sus artefactos, y se detiene | No |
| `/opsx:update <qué cambiar>` | Revisa los artefactos de un change y mantiene su coherencia | No |
| `/opsx:apply [change]` | Implementa `tasks.md` y marca cada tarea con `[x]` | Sí |
| `/opsx:sync [change]` | Incorpora los deltas a `openspec/specs/` **sin** archivar | No |
| `/opsx:archive [change]` | Fusiona los deltas en las specs y mueve el change a `archive/` | No |

### Perfil ampliado (`openspec config profile` + `openspec update`)

| Comando | Función |
|---|---|
| `/opsx:new <nombre>` | Crea el change vacío |
| `/opsx:continue` | Genera el siguiente artefacto pendiente |
| `/opsx:ff` | Genera todos los artefactos pendientes |
| `/opsx:verify` | Comprueba la implementación con respecto a las specs y las tareas |
| `/opsx:bulk-archive` | Archiva varios changes |
| `/opsx:onboard` | Tutorial guiado dentro del repositorio |

## En el terminal

### Instalación y proyecto

```bash
npm install -g @fission-ai/openspec@latest
```

```bash
openspec init --tools claude --language es
```

```bash
openspec update
```

```bash
openspec config profile
```

```bash
openspec config set telemetry.enabled false
```

### Consultar

| Comando | Para qué |
|---|---|
| `openspec list` | Changes activos y progreso de tareas |
| `openspec list --specs` | Capabilities y nº de requisitos |
| `openspec list --archived` | Changes archivados |
| `openspec view` | Panel interactivo de specs y changes |
| `openspec show <change>` | Proposal + deltas de un change |
| `openspec show <change> --diff` | Diferencias por requisito |
| `openspec show <spec> --type spec` | Spec principal completa |
| `openspec show <spec> --type spec --json --no-scenarios` | Resumen de requisitos (útil para scripts) |
| `openspec status --change <change>` | Qué artefactos están hechos o bloqueados |
| `openspec instructions <artefacto> --change <change>` | Instrucciones exactas que recibe la IA (con tu contexto y reglas) |

### Validar

| Comando | Para qué |
|---|---|
| `openspec validate <change> --strict` | Un change |
| `openspec validate --specs --strict` | Todas las specs principales |
| `openspec validate --all --strict --no-interactive` | Todas las specs y changes (CI) |
| `openspec validate --archived` | Changes archivados con tareas pendientes |

### Crear y archivar desde el terminal

| Comando | Para qué |
|---|---|
| `openspec new change <nombre>` | Crear la carpeta del change |
| `openspec new change <nombre> --schema <schema>` | Con un schema concreto |
| `openspec archive <change>` | Archivar (pide confirmación) |
| `openspec archive <change> --yes` | Sin confirmación |
| `openspec archive <change> --skip-specs` | Archivar sin modificar las specs (herramientas, documentación) |

### Schemas (experimental)

| Comando | Para qué |
|---|---|
| `openspec schemas` | Schemas disponibles |
| `openspec schema fork spec-driven <nombre>` | Copiar el schema por defecto al proyecto |
| `openspec schema validate <nombre>` | Validar un schema propio |
| `openspec templates` | Rutas de las plantillas en uso |

### Stores (beta)

| Comando | Para qué |
|---|---|
| `openspec store setup <id>` | Crear y registrar un store local |
| `openspec store list` | Stores registrados |
| `--store <id>` | Opción de `list`, `show`, `validate`, `archive`, `status`… |

## Formato de un delta

```markdown
# Spec Delta

## Purpose                                   ← solo si la capability es NUEVA (≥ 50 caracteres)
Para qué sirve la capability.

## ADDED Requirements
### Requirement: <nombre>
<texto con SHALL o MUST, ≤ 500 caracteres>

#### Scenario: <nombre>                      ← 4 almohadillas
- **WHEN** <condición con datos concretos>
- **THEN** <resultado observable>
- **AND** <otro resultado>

## MODIFIED Requirements
### Requirement: <nombre EXACTO del existente>
<bloque COMPLETO, con el nombre de todos los escenarios existentes>

## REMOVED Requirements
### Requirement: <nombre>
**Reason**: <por qué>
**Migration**: <qué debe hacer quien dependía de esto>

## RENAMED Requirements
- FROM: `### Requirement: <viejo>`
- TO: `### Requirement: <nuevo>`
```

## Flujo básico

```
/clear → /opsx:propose … → revisar + /opsx:update … → openspec validate <c> --strict → commit
/clear → /opsx:apply <c> → uv run pytest → /opsx:archive <c> → commit
```

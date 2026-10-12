![Hoteles Brisa](images/brisa-bookings-imagotipo.png)

**Hoteles Brisa** es una cadena con tres hoteles en Málaga, Madrid y
Barcelona. Sus reservas llegan cada día por dos vías: el motor de reservas
propio y las agencias de viajes online.

El **equipo de datos** reúne esas reservas en un almacén analítico local
(SQLite). Antes de guardarlas, comprueba que cumplen el contrato de datos:
las que no lo cumplen quedan en cuarentena y el resto se escribe en la
tabla `fct_bookings`. De ese almacén leen dos sistemas: el **cuadro de
dirección**, que muestra la ocupación de cada hotel, y el **sistema de
precios**, que fija la tarifa del día siguiente.

El equipo trabaja con agentes de código. La herramienta principal es
**Claude Code**, aunque el repositorio incluye también la configuración
para GitHub Copilot, Cursor y OpenCode.

La [guía sencilla](docs/simple-guide.md) explica sin tecnicismos los
conceptos del proyecto.

## Incidencia abierta: INC-0142

El departamento de Revenue ha abierto la incidencia
[INC-0142](docs/tickets/INC-0142.md):

> El cuadro de dirección dice que el Brisa Málaga Playa estuvo al **112 %**
> la noche del 2 de marzo. El hotel tiene 8 habitaciones.

El sistema de precios dio la cifra por buena y subió la tarifa un 30 %.
Los tests pasan, pero la integración continua seguirá en rojo mientras la
incidencia esté abierta. La orden `python tasks.py acceptance` hace de
oráculo: comprueba cinco criterios del contrato, que pasan a verde cuando
la carga es correcta.

Además de la incidencia, hay cuatro tickets técnicos pendientes, pequeños e
independientes entre sí: de [BRI-201](docs/tickets/BRI-201.md) a
[BRI-204](docs/tickets/BRI-204.md).

## Plan de trabajo

El [plan de trabajo](playbook/README.md) resuelve la incidencia y los
tickets pendientes en seis fases. En cada una, Claude Code asume una parte
mayor del trabajo.

| Fase | Qué se delega en Claude Code |
| --- | --- |
| 1 | El diagnóstico, en modo plan |
| 2 | El arreglo completo, con `/goal` y el oráculo como condición |
| 3 | Los tickets pendientes, con varias sesiones en paralelo y worktrees |
| 4 | Parte de su propia configuración: permisos, un skill, un hook y la línea de estado |
| 5 | La revisión del código, con varios revisores automáticos |
| 6 | La ejecución sin terminal: scripts, tareas programadas y GitHub |

## Preparar el entorno

Se necesita Python 3.9 o superior, Git y Claude Code. En
[`INSTALLATION.md`](INSTALLATION.md) se explica cómo instalarlos en
Windows, macOS y Linux. El proyecto solo usa la biblioteca estándar de
Python, y todas las tareas se lanzan con `python tasks.py`, igual en los
tres sistemas.

No hace falta una cuenta de GitHub: todo el plan de trabajo funciona en
local, salvo un bloque opcional. Si el proyecto se recibe como carpeta o
como archivo comprimido, se convierte en repositorio con `git init -b main`,
`git add -A` y `git commit -m "Initial commit"`. La opción `-b main` es
necesaria porque el plan de trabajo parte de la rama `main`.

Desde la carpeta del repositorio:

**Windows (PowerShell)**

```powershell
uv venv
.venv\Scripts\Activate.ps1
python tasks.py setup
```

**macOS y Linux**

```bash
uv venv
source .venv/bin/activate
python tasks.py setup
```

`uv venv` usa la versión indicada en `.python-version` (3.12) y la
descarga si no está instalada. Sin uv, el entorno también se puede crear
con `python -m venv .venv`.

Para reproducir la incidencia:

```bash
python tasks.py run-all
python tasks.py occupancy
python tasks.py reconcile
```

Claude Code debe abrirse **desde ese mismo terminal**, con el entorno
activado: el servidor MCP y los hooks se ejecutan como procesos hijo y
usan su Python.

```bash
claude
```

## Tareas

| Orden | Qué hace |
| --- | --- |
| `python tasks.py setup` | Comprueba la versión de Python |
| `python tasks.py run --date 2026-03-01` | Carga el extracto de un día |
| `python tasks.py run-all` | Carga los tres extractos |
| `python tasks.py occupancy` | Muestra el informe de ocupación que lee el cuadro de dirección |
| `python tasks.py reconcile` | Comprueba el grain del contrato y falla si hay duplicados |
| `python tasks.py acceptance` | Oráculo de INC-0142: carga los extractos en almacenes temporales y comprueba el contrato |
| `python tasks.py test` | Ejecuta los tests |
| `python tasks.py check` | Ejecuta los tests y la reconciliación |
| `python tasks.py reset` | Borra el almacén local |
| `python tasks.py mcp-check` | Prueba el servidor MCP sin ningún agente |
| `python tasks.py sample-env` | Crea un `.env` de ejemplo para la comprobación de exposición de secretos |

## Estructura

```
brisa-bookings/
├── AGENTS.md                  instrucciones comunes a cualquier agente
├── CLAUDE.md                  importa AGENTS.md y añade lo propio de Claude Code
├── tasks.py                   lanzador de tareas
├── .python-version            versión de Python que usa uv (3.12)
├── data/
│   ├── raw/                   extractos diarios de reservas (no se modifican)
│   └── reference/hotels.json  hoteles y su capacidad
├── src/pipeline/
│   ├── contract.py            reglas de validación
│   ├── load.py                carga en fct_bookings
│   ├── occupancy.py           informe de ocupación
│   ├── reconcile.py           comprobación del grain
│   └── acceptance.py          oráculo de INC-0142 (protegido por un hook)
├── tests/
├── mcp_server/server.py       servidor MCP de solo lectura
├── security/                  comprobación de exposición de secretos
├── playbook/                  plan de trabajo
├── images/                    logotipo del proyecto
├── docs/
│   ├── tickets/               INC-0142 y los tickets BRI-201 a BRI-204
│   ├── data-contracts/        contrato de fct_bookings
│   ├── simple-guide.md        el proyecto explicado sin tecnicismos
│   ├── other-tools.md         Copilot, Cursor y OpenCode frente a Claude Code
│   ├── decisions/             decisiones de diseño (ADR)
│   ├── runbooks/              procedimiento de reproceso autorizado
│   └── plans/                 plantilla para el estado del trabajo
├── .claude/                   configuración de Claude Code
│   ├── settings.json          permisos y hooks
│   ├── rules/pipeline.md      reglas que solo se cargan en src/pipeline/
│   ├── skills/                skill validate-pipeline
│   ├── agents/                subagente data-quality-reviewer
│   ├── hooks/                 protección de los datos de origen y bloqueo de SQL destructivo
│   └── loop.md                prompt por defecto de /loop
├── .mcp.json                  servidor MCP para Claude Code
└── .github/ .cursor/ .opencode/ .vscode/ opencode.json
                               configuración de las demás herramientas
```

## Los datos

| Fichero | Casos relevantes |
| --- | --- |
| `bookings_2026-03-01.json` | Seis reservas. En una, la salida es anterior a la entrada; otra corresponde a un hotel que no existe. |
| `bookings_2026-03-02.json` | Cuatro reservas. `B-3002` añade una habitación y `B-3003` pasa de provisional a confirmada. |
| `bookings_2026-03-03.json` | Cuatro reservas. `B-3008` se cancela, una reserva está en dólares y `B-3010` llega con un día de retraso. |
| `reference/hotels.json` | Málaga (8 habitaciones), Madrid (10) y Barcelona (6). |

## Configuración de Claude Code

| Elemento | Cuándo se activa | Qué hace |
| --- | --- | --- |
| `CLAUDE.md` con `@AGENTS.md` | Al abrir la sesión | Carga las instrucciones comunes y las propias de Claude Code |
| `.claude/rules/pipeline.md` | Al leer archivos de `src/pipeline/` | Añade reglas que solo afectan al pipeline |
| `validate-pipeline` (skill) | Al invocarlo (`/validate-pipeline`) o cuando el agente lo considera adecuado | Ejecuta tests, oráculo, reconciliación e informe de ocupación; informa sin corregir |
| `data-quality-reviewer` (subagente) | Por delegación o con `@agent-data-quality-reviewer` | Revisa un cambio frente al contrato en un contexto independiente |
| `protect_source.py` (hook) | Antes de cada edición | Bloquea escrituras en `data/raw/`, `data/reference/` y en el oráculo `acceptance.py` |
| `block_destructive_sql.py` (hook) | Antes de cada comando de Bash o PowerShell | Bloquea `DROP TABLE`, `TRUNCATE TABLE` y `DELETE` sin `WHERE` |
| `bookings-warehouse` (MCP) | Al abrir el proyecto | Ofrece metadatos y comprobaciones del almacén, en solo lectura |
| Permisos | Siempre | Permiten tests e informes, piden confirmación para cargar o borrar y deniegan `sqlite3`, `.env` y `playbook/` |

El servidor MCP existe porque el agente no debe consultar el almacén desde
el terminal. Git, los diffs y las búsquedas en el código no necesitan MCP:
la propia herramienta ya los resuelve.

El agente no puede leer el plan de trabajo porque contiene los resultados
esperados de cada fase. Así llega a sus conclusiones a partir del código y
los datos, sin copiarlas.

## Otras herramientas

En [`docs/other-tools.md`](docs/other-tools.md) se comparan Claude Code,
Copilot, Cursor y OpenCode: qué archivos lee cada una y qué protecciones
son un bloqueo real y cuáles solo una instrucción.

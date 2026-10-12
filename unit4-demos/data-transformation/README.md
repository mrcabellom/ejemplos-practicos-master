![Pedalia Icon](images/pedalia-bikes-imagotipo.png)

**Pedalia** es un servicio de bicicleta compartida en Madrid con seis
estaciones: Sol, Atocha, Retiro, Moncloa, Chamberí y Lavapiés. Las bicis y
los anclajes los gestiona un **operador** externo, que cada semana envía a
Pedalia una entrega con los viajes registrados.

Con esas entregas, el **equipo de datos** de Pedalia prepara el informe de
uso diario. **Planificación de flota** lo usa cada mañana para decidir a qué
estaciones lleva bicis la furgoneta. Si el informe sale mal, la furgoneta puede
no tener la información correcta.

Las entregas no siempre llegan como se espera: el operador cambia de
formato, reenvía viajes, renombra estaciones... Cada incidencia llega como
un ticket (`OPS-10N`) y el equipo la resuelve con un agente de código,
**Claude Code**, sin tocar nunca lo que envía el operador.

## Qué contiene este repositorio

`src/bikes/` lee todas las entregas de `inbox/`, limpia cada viaje con una
regla por campo y deja en `output/`:

- `trips.csv`: los viajes válidos, uno por `trip_id`.
- `rejected.csv`: los descartados, con su entrega y su motivo.
- `daily_usage.csv`: salidas y duración media por día y estación.

Lo que se garantiza en esa salida está en el
[contrato de datos](docs/data-contracts/trips.md), y `python tasks.py check`
lo comprueba.

## Preparar el entorno

Hace falta Python 3.9+ y Git. Solo se usa la biblioteca estándar; las tareas
se lanzan con `python tasks.py`, igual en Windows, macOS y Linux.

**Windows (PowerShell):**

```powershell
uv venv
.venv\Scripts\Activate.ps1
python tasks.py all
```

**macOS y Linux:**

```bash
uv venv
source .venv/bin/activate
python tasks.py all
```

`uv venv` usa la versión de `.python-version` (3.12) y la descarga si hace
falta. Tambien puede usarse `python -m venv .venv` sin uv.

Al ejecutar el comando de tasks.py, debe verse `Ran 9 tests` y `OK: la salida cumple el contrato`: con la
entrega de la primera semana, todo está en orden.

Después, desde **ese mismo terminal** (los hooks y el servidor MCP heredan
su Python) podemos lanzar claude utilizando la herramienta de cli:

```bash
claude
```

## Estructura

```
pedalia-bikes/
├── AGENTS.md                   reglas comunes a cualquier agente
├── CLAUDE.md                   importa AGENTS.md y añade lo de Claude Code
├── tasks.py                    lanzador de tareas
├── inbox/                      entregas recibidas: no se modifican nunca
├── output/                     salida generada (no se versiona)
├── src/bikes/
│   ├── rules.py                una regla de limpieza por campo
│   ├── transform.py            aplica las reglas y calcula el uso diario
│   └── check.py                comprueba output/ contra el contrato
├── tests/test_bikes.py         tests de las reglas y de la transformación
├── docs/
│   ├── data-contracts/trips.md qué se garantiza en output/
│   ├── tickets/                tickets de Planificación (OPS-10N)
│   └── plans/STATUS-TEMPLATE.md plantilla de docs/plans/status.md
├── mcp_server/server.py        servidor MCP de solo lectura (bike-data)
├── .mcp.json                   declara el servidor MCP
├── security/.env.example       secreto de muestra para el ejercicio de permisos
├── deliveries/                 entregas y tickets futuros (oculto al agente)
├── playbook/                   plan de trabajo por fases (oculto al agente)
└── .claude/
    ├── settings.json           permisos y hooks
    ├── loop.md                 prompt por defecto de /loop
    ├── rules/transform.md      reglas que se cargan al tocar src/bikes/
    ├── skills/check-delivery/
    ├── agents/data-reviewer.md
    └── hooks/                  protect_inbox.py, block_delete.py
```

## Lo que viene configurado

| Pieza | Cómo se activa | Qué hace |
| --- | --- | --- |
| `AGENTS.md` + `CLAUDE.md` | Al abrir el proyecto | Reglas del proyecto y de Claude Code |
| `rules/transform.md` | Al trabajar con `src/bikes/` | Rechazar en vez de inventar; motivos y tests |
| `check-delivery` (skill) | `/check-delivery` o porque encaja | Tests + pipeline; informa sin corregir |
| `data-reviewer` (subagente) | Al delegarle una revisión | Revisa un cambio contra el contrato, en su propio contexto |
| `protect_inbox.py` (hook) | Solo, antes de cada edición | Bloquea editar `inbox/` y `deliveries/` |
| `block_delete.py` (hook) | Solo, antes de cada comando | Bloquea `rm`/`del`/`Remove-Item` sobre entregas y salidas |
| `bike-data` (MCP) | Al abrir el proyecto | Resume un CSV sin cargarlo entero en el contexto |
| `loop.md` | `/loop` sin prompt | Vigila el pipeline y solo informa |

## Tareas

| Orden | Qué hace |
| --- | --- |
| `python tasks.py setup` | Comprueba la versión de Python |
| `python tasks.py test` | Tests |
| `python tasks.py transform` | Genera `output/` a partir de `inbox/` |
| `python tasks.py check` | Comprueba `output/` (0 cumple, 1 no cumple, 2 falta evidencia) |
| `python tasks.py pipeline` | `transform` + `check` |
| `python tasks.py all` | `test` + `pipeline` |
| `python tasks.py reset` | Borra `output/` |
| `python tasks.py deliver N` | Simula al operador: entrega `week-N.csv` y su ticket (N = 2…6) |
| `python tasks.py mcp-check` | Prueba el servidor MCP sin Claude |
| `python tasks.py sample-env` | Crea un `.env` de muestra |

## Plan de trabajo

El [playbook](playbook/README.md) recorre seis fases, una por cada entrega que tiene que hacer el
operador: entender el repositorio, escribir, instrucciones y contexto, skill y
subagente, hooks y permisos, MCP y especificación, y vigilancia con
`/loop`.

# brisa-bookings

Instrucciones para cualquier agente de código que trabaje en este
repositorio. Es un formato abierto que leen Claude Code, GitHub Copilot,
Cursor y OpenCode.

## Contexto

Este repositorio es del equipo de datos de Hoteles Brisa, una cadena con
tres hoteles. Cada día, el pipeline carga en un almacén analítico local
(SQLite) las reservas que envían el motor de reservas propio y las agencias
online. Del almacén leen el cuadro de dirección y el sistema de precios.

La incidencia abierta está en `docs/tickets/INC-0142.md`.

## Comandos canónicos

Todas las tareas se lanzan con `python tasks.py <tarea>`, igual en Windows,
macOS y Linux. Si `python` no apunta a Python 3, usa `python3`.

- Comprobar el entorno: `python tasks.py setup`
- Cargar un extracto: `python tasks.py run --date 2026-03-01`
- Cargar los tres extractos: `python tasks.py run-all`
- Informe de ocupación: `python tasks.py occupancy`
- Reconciliar con el contrato: `python tasks.py reconcile`
- Comprobar la carga contra el contrato, sin tocar el almacén:
  `python tasks.py acceptance`
- Tests: `python tasks.py test`
- Tests y reconciliación: `python tasks.py check`
- Borrar el almacén local: `python tasks.py reset`

## Antes de modificar

- Lee `docs/data-contracts/fct_bookings.md`. La clave, el grain y la regla
  de ocupación están declarados allí: no los supongas.
- Si el cambio afecta a una decisión de diseño, revisa `docs/decisions/`.

## Límites

- `data/raw/` y `data/reference/` son el origen y son inmutables.
- `src/pipeline/acceptance.py` es el oráculo: decide cuándo está resuelta la
  incidencia. Lo cambia una persona, no el agente que trabaja para pasarlo.
- No cambies el grain ni el esquema de `fct_bookings` sin actualizar su
  contrato y avisar a los consumidores que declara.
- No lances reprocesos ni borres el almacén por iniciativa propia: el
  procedimiento está en `docs/runbooks/backfill.md` y requiere autorización.
- No uses `sqlite3` por terminal. Para consultar el almacén existe el
  servidor MCP de solo lectura `bookings-warehouse`.
- No ocultes duplicados con `DISTINCT` ni con filtros en los informes: el
  arreglo va en la carga.

## Trabajo terminado

- El cambio está acotado y el diff revisado.
- `python tasks.py check` pasa entero.
- Se documenta qué se comprobó y qué no.

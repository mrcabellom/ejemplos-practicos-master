# pedalia-bikes

Instrucciones para cualquier agente de código que trabaje en este repositorio.

## Qué es

La transformación que convierte las entregas semanales de viajes del
operador (`inbox/week-N.csv`) en `output/`:

- `trips.csv`: los viajes válidos, uno por `trip_id`.
- `rejected.csv`: los descartados, con su entrega y su motivo.
- `daily_usage.csv`: salidas y duración media por día y estación.

## Comandos

Todo se lanza con `python tasks.py <tarea>`:

- `test`: ejecuta los tests.
- `transform`: genera `output/` a partir de `inbox/`.
- `check`: comprueba `output/` contra el contrato.
- `pipeline`: `transform` y `check`, en orden.
- `all`: `test` y `pipeline`, en orden.
- `reset`: borra `output/`.

## Antes de modificar

Lee `docs/data-contracts/trips.md`. La clave del viaje, los rangos y los
catálogos están allí: no los supongas.

## Límites

- `inbox/` es lo que envía el operador y no se modifica nunca. Los cambios
  del origen se absorben con reglas en `src/bikes/rules.py` o en
  `src/bikes/transform.py`.
- No cambies el contrato sin que lo pida una persona.
- No uses dependencias externas: solo la biblioteca estándar.

## Trabajo terminado

- `python tasks.py all` pasa entero.
- Cada cambio de comportamiento tiene su test en `tests/test_bikes.py`.
- Se dice qué se comprobó y qué no.

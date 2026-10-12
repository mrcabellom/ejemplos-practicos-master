---
name: validate-pipeline
description: Valida el pipeline de reservas ejecutando los tests, el oráculo de aceptación, la reconciliación y el informe de ocupación. Úsalo antes de dar un cambio por terminado, después de modificar src/pipeline/ o cuando haya que comprobar si fct_bookings respeta el grain de su contrato.
allowed-tools:
  - Bash(python tasks.py test)
  - Bash(python tasks.py acceptance)
  - Bash(python tasks.py reconcile)
  - Bash(python tasks.py occupancy)
  - PowerShell(python tasks.py test)
  - PowerShell(python tasks.py acceptance)
  - PowerShell(python tasks.py reconcile)
  - PowerShell(python tasks.py occupancy)
  - Read
  - Grep
---

# Validar el pipeline de reservas

Comprueba que un cambio no rompe el contrato de `fct_bookings`.

## Procedimiento

1. Ejecuta `python tasks.py test` y anota el resultado completo, no solo si
   pasó.
2. Ejecuta `python tasks.py acceptance` y anota qué criterios pasan y cuáles
   fallan. Comprueba el código sobre almacenes temporales: dice si la carga
   es correcta, no si el almacén real lo está.
3. Ejecuta `python tasks.py reconcile` y registra su salida y su código de
   salida. Un código distinto de cero no prueba por sí solo que haya
   duplicados: distingue entre claves duplicadas, almacén inexistente y
   otros errores. Si falta el almacén, informa de que falta evidencia; no
   lances cargas para obtenerla.
4. Ejecuta `python tasks.py occupancy` e indica si alguna noche supera el
   100 %. Eso es imposible en un hotel y señala filas que sobran.
5. Contrasta lo observado con `docs/data-contracts/fct_bookings.md`.

## Cómo informar

- Qué comandos ejecutaste y qué devolvió cada uno.
- Si el grain se respeta, con filas y reservas distintas.
- Qué comprobaciones **no** hiciste y por qué.

## Lo que este skill no hace

No corrige datos, no borra filas y no lanza reprocesos. Si detecta un
problema, lo describe y se detiene. Reprocesar lo decide una persona,
siguiendo `docs/runbooks/backfill.md`.

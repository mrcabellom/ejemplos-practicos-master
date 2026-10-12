---
name: check-delivery
description: Comprueba la última entrega de viajes ejecutando los tests, la transformación y la comprobación del contrato. Úsalo cuando llegue una entrega nueva a inbox/, después de cambiar src/bikes/ o cuando haya que saber si output/ cumple docs/data-contracts/trips.md.
allowed-tools: Bash(python tasks.py test), Bash(python tasks.py pipeline), PowerShell(python tasks.py test), PowerShell(python tasks.py pipeline), Read, Grep, Glob
---

# Comprobar una entrega

## Procedimiento

1. Mira qué entregas hay en `inbox/` y cuál es la más reciente.
2. Ejecuta `python tasks.py test`. Anota cuántos tests pasan y cuáles fallan.
3. Ejecuta `python tasks.py pipeline`:
   - Si la transformación se rompe (traza de Python), copia la última línea
     del error y no sigas.
   - Si no, anota las cifras de la última entrega: leídos, válidos y
     rechazados.
4. Lee el código de salida de la comprobación:
   - `0`: cumple el contrato.
   - `1`: no lo cumple; copia los problemas tal cual.
   - `2`: falta evidencia; dilo.
5. Contrasta lo observado con `docs/data-contracts/trips.md`.

## Cómo informar

Una tabla corta (comando, resultado, qué significa) y una frase final:
**Cumple**, **No cumple** (con los problemas), **Se rompe** (con el error)
o **Falta evidencia**.

## Lo que este skill no hace

No corrige código, no toca `inbox/` y no lanza `deliver`. Si encuentra un
problema, lo describe y se detiene.

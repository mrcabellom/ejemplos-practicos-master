---
description: Valida el pipeline de reservas con tests, reconciliación e informe de ocupación, sin corregir nada.
agent: agent
---

Valida el pipeline de reservas:

1. Ejecuta `python tasks.py test` y anota el resultado completo.
2. Ejecuta `python tasks.py reconcile` y registra su salida y su código de
   salida. Distingue entre claves duplicadas, almacén inexistente y otros
   errores. Si falta el almacén, informa de que falta evidencia; no lances
   cargas para obtenerla.
3. Ejecuta `python tasks.py occupancy` e indica si alguna noche supera el
   100 %.
4. Contrasta lo observado con `docs/data-contracts/fct_bookings.md`.

Indica qué comandos ejecutaste, qué devolvió cada uno y qué no comprobaste.
No corrijas datos ni lances reprocesos.

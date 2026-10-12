# Proposal

## Why

El sistema de cajas reenvió corregido el fichero del 2026-10-02: el pedido O-1011 no era una devolución real y se eliminó. Al reprocesar el día, bronze tiene el doble de filas para esa fecha y O-1011 sigue llegando a silver y gold. La spec de ingesta no decía qué ocurre al cargar dos veces el mismo fichero, y la implementación añade las filas de nuevo.

## What Changes

- Reprocesar una fecha **sustituye** las filas de ese fichero en bronze, en lugar de añadirlas.
- La sustitución es atómica: si la carga falla, bronze conserva la versión anterior del fichero.

## Capabilities

### New Capabilities
<!-- Ninguna -->

### Modified Capabilities
- `orders-ingestion`: nuevo requisito sobre el reprocesado de una fecha ya cargada.

## Impact

- Tablas: `bronze.orders_raw` deja de acumular cargas repetidas del mismo fichero.
- Datos existentes: los duplicados ya cargados desaparecen al reprocesar cada fecha (en local basta con borrar `warehouse/` y ejecutar `--all`).
- Consumidores: silver, gold y el export dejan de contener líneas eliminadas en ficheros corregidos.
- Operación: el pipeline puede relanzarse sin riesgo de duplicar datos.
- Código: módulo de ingesta y tests.

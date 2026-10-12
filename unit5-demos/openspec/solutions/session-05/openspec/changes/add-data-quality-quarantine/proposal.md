# Proposal

## Why

El cuadro de mando muestra -7,50 € de ventas para VLC-007 el 2026-10-01: la línea del pedido O-1006 tiene cantidad -2 y llega a gold. Además, las filas que silver excluye desaparecen sin dejar registro, de modo que nadie sabe cuántas se pierden ni por qué.

## What Changes

- Reglas de calidad explícitas y codificadas (DQ001…DQ005) para cada línea de pedido.
- Las cantidades menores o iguales que 0 pasan a considerarse inválidas.
- Las líneas que incumplen alguna regla se guardan en una tabla de cuarentena con la lista de reglas incumplidas, en lugar de descartarse en silencio.

## Capabilities

### New Capabilities
- `data-quality`: reglas de calidad de las líneas de pedido y tabla de cuarentena.

### Modified Capabilities
- `order-lines`: las filas inválidas se derivan a la cuarentena; las cantidades no positivas pasan a ser inválidas.

## Impact

- Tablas: nueva `silver.order_lines_quarantine`; `silver.order_lines` deja de contener líneas con cantidad <= 0.
- Consumidores: Power BI y el export de Finanzas dejan de mostrar el importe negativo de VLC-007 (corrección de valores, sin cambio de esquema).
- Código: transformación bronze → silver, `run_pipeline.py` y tests. El test que contaba 6 líneas de silver para el 2026-10-01 debe pasar a 5.

# Proposal

## Why

El equipo de BI necesita las ventas diarias de cada tienda para el cuadro de mando de Power BI. Hoy solo existen líneas de pedido sueltas en silver.

## What Changes

- Nueva tabla `gold.daily_sales` con una fila por fecha de negocio y tienda.
- Métricas: número de pedidos e importe total de las líneas completadas (IVA incluido).
- Las devoluciones no se contabilizan.

## Capabilities

### New Capabilities
- `daily-sales`: ventas diarias por tienda en la capa gold.

### Modified Capabilities
<!-- Ninguna -->

## Impact

- Tablas: nueva `gold.daily_sales`.
- Consumidores: cuadro de mando de tiendas de Power BI (equipo de BI).
- Código: transformación silver → gold, paso nuevo en `run_pipeline.py` y tests.

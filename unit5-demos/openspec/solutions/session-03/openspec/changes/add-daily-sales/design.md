# Design

## Context

`silver.order_lines` contiene líneas tipadas con estado `completed` o `returned`. Power BI necesita agregados por día y tienda.

## Goals / Non-Goals

**Goals:**
- Una tabla agregada sencilla, con importes que coincidan con el ticket de caja (IVA incluido).

**Non-Goals:**
- Importes sin IVA o netos de devoluciones (no los ha pedido nadie todavía).

## Decisions

1. **Reconstrucción completa** de `gold.daily_sales` en cada ejecución, igual que silver. Alternativa descartada: actualizar solo los días nuevos, innecesario con este volumen.
2. **Pedidos distintos con `count(DISTINCT order_id)`**, porque un pedido puede tener varias líneas (O-1001 tiene dos).
3. **Importes en DECIMAL(12,2)** según las convenciones del equipo, para evitar errores de redondeo de los números en coma flotante.

## Risks / Trade-offs

- [Las devoluciones no restan ventas] → Decisión explícita en la spec; si Finanzas necesita otra cosa, se cambiará con un change nuevo.

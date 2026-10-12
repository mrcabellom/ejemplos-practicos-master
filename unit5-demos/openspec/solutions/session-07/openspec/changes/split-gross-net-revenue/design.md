# Design

## Context

`gold.daily_sales` se reconstruye completa desde `silver.order_lines` y la consumen 12 informes de Power BI y el export de Finanzas. El fichero de origen no incluye la fecha de devolución: una línea `returned` conserva el `order_ts` de la compra.

## Goals / Non-Goals

**Goals:**
- Cifras que cuadren con contabilidad (netas y sin IVA).
- Migración sin que Power BI deje de funcionar el día del despliegue.

**Non-Goals:**
- Imputar las devoluciones a la fecha en que se producen (el origen no lo permite).
- IVA histórico (cambios de tipo a lo largo del tiempo): se usa el tipo vigente.

## Decisions

1. **Tipos de IVA en la tabla `gold.vat_rates` (category, vat_rate)**, cargada desde `mercaluz/reference/vat_rates.csv`, en lugar de un `CASE` en SQL. Finanzas puede revisar el CSV en el pull request y añadir categorías sin tocar la transformación.
2. **Error ante una categoría desconocida** en lugar de aplicar un 21 % por defecto. Un tipo por defecto ocultaría errores fiscales; es preferible que el pipeline se detenga y alguien decida.
3. **Devoluciones imputadas a `order_date`** (fecha de la compra), porque es la única fecha disponible. Se documenta como limitación.
4. **Redondeo solo del total** (`round(sum(importe / (1 + iva)), 2)`) para evitar el error acumulado de redondear cada línea.
5. **Vista `_v1` con fecha de retirada** en lugar de mantener `total_amount` en la tabla: la tabla nueva queda limpia y la vista tiene una caducidad explícita (2026-12-31).

## Risks / Trade-offs

- [Informes de Power BI que no se migren a tiempo] → Lista de los 12 informes y sus responsables; aviso 30 y 7 días antes de eliminar la vista.
- [`net_revenue` negativo en días con muchas devoluciones] → Es correcto contablemente; se explica en el diccionario de datos.

## Migration Plan

1. Desplegar la tabla nueva, la vista `_v1` y el nuevo export.
2. Marta valida el export del primer día en paralelo con su Excel actual.
3. BI migra los informes; el 2026-12-31, un change separado elimina la vista.
4. Rollback: desplegar la versión anterior; gold recupera su esquema en la siguiente ejecución (reconstrucción completa).

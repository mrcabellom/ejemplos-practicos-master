# Spec Delta

## MODIFIED Requirements

### Requirement: Ventas diarias por tienda
`gold.daily_sales` SHALL contener una fila por (`order_date`, `store_id`) con líneas `completed` o `returned`, con `orders_count` (pedidos distintos con líneas `completed`), `gross_revenue` (importe con IVA de las líneas `completed`), `returns_amount` (importe con IVA de las líneas `returned`, en positivo) y `net_revenue`, todos DECIMAL(12,2), y SHALL reconstruirse a partir de `silver.order_lines` en cada ejecución.

#### Scenario: Ventas de una tienda en un día
- **WHEN** el 2026-10-01 la tienda MAD-001 tiene las líneas completadas 6 x 0,95 (alimentacion_basica), 1 x 8,49 (alimentacion) y 1 x 11,90 (drogueria) en 2 pedidos
- **THEN** `gold.daily_sales` contiene para (2026-10-01, MAD-001) `orders_count` = 2, `gross_revenue` = 26,09, `returns_amount` = 0,00 y `net_revenue` = 23,03

#### Scenario: Tienda con devolución
- **WHEN** el 2026-10-01 la tienda BCN-014 tiene una línea completada de 2 x 0,80 (alimentacion_basica) y una devuelta de 3 x 6,50 (bebidas)
- **THEN** `gold.daily_sales` contiene para (2026-10-01, BCN-014) `gross_revenue` = 1,60, `returns_amount` = 19,50 y `net_revenue` = -14,58

#### Scenario: Día solo con devoluciones
- **WHEN** una tienda solo tiene líneas devueltas en un día
- **THEN** su fila existe con `orders_count` = 0 y `gross_revenue` = 0,00

## ADDED Requirements

### Requirement: Cálculo de ventas netas sin IVA
`net_revenue` SHALL calcularse como la suma, por línea, de su importe dividido entre (1 + tipo de IVA de su categoría), con signo positivo para las líneas `completed` y negativo para las `returned`, redondeando a dos decimales solo el total.

#### Scenario: Redondeo al final
- **WHEN** una tienda tiene líneas de 5,70 al 4 %, 8,49 al 10 % y 11,90 al 21 %
- **THEN** `net_revenue` = 23,03 (5,4808 + 7,7182 + 9,8347 redondeado)

### Requirement: Tipos de IVA por categoría
El pipeline SHALL aplicar el IVA de la tabla `gold.vat_rates`: `alimentacion_basica` 4 %, `alimentacion` 10 %, `bebidas` 21 % y `drogueria` 21 %. Si una línea tiene una categoría sin tipo, la ejecución MUST terminar con un error que liste esas categorías, sin reconstruir gold.

#### Scenario: Categoría desconocida
- **WHEN** silver contiene una línea con `category` = `mascotas` y no existe tipo para `mascotas`
- **THEN** la ejecución termina con un error que menciona `mascotas`
- **AND** `gold.daily_sales` conserva el contenido de la ejecución anterior

### Requirement: Vista de compatibilidad del esquema anterior
Hasta el 2026-12-31 SHALL existir la vista `gold.daily_sales_v1` con las columnas `order_date`, `store_id`, `orders_count` y `total_amount` (igual a `gross_revenue`), limitada a las filas con `orders_count` > 0.

#### Scenario: Informe antiguo de Power BI
- **WHEN** un informe consulta `gold.daily_sales_v1` para (2026-10-01, MAD-001)
- **THEN** obtiene `orders_count` = 2 y `total_amount` = 26,09, como antes del cambio

## REMOVED Requirements

### Requirement: Devoluciones excluidas de las métricas
**Reason**: Finanzas necesita las devoluciones para cuadrar con contabilidad; ignorarlas sobrestima las ventas.
**Migration**: Usar `returns_amount` para ver las devoluciones y `net_revenue` para las ventas netas. Quien necesite el comportamiento anterior puede usar `gross_revenue` o la vista `gold.daily_sales_v1`.

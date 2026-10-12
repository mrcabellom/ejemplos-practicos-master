# Feature Specification: Ventas diarias por tienda

**Feature Branch**: `001-daily-sales`

**Created**: 2026-10-06

**Status**: Draft

**Input**: User description: "Quiero una tabla daily_sales con las ventas por tienda y día a partir del CSV de pedidos data/raw/orders.csv: número de pedidos, unidades e importe bruto. Las líneas con cantidad menor o igual a cero no cuentan como venta. La usa el equipo de Operaciones para comparar tiendas cada mañana. El brief completo está en docs/brief.md."

## Clarifications

### Session 2026-10-06

- Q: ¿En qué zona horaria se decide a qué día pertenece una venta? → A: Hora de Madrid (Europe/Madrid); los `order_ts` del CSV vienen en UTC.
- Q: ¿Qué hacer con líneas repetidas (mismo `order_id` + `line_id`)? → A: Contarlas una sola vez; las copias se registran como rechazadas con motivo `duplicate`.
- Q: ¿Cuentan los pedidos con `status` distinto de `completed` (p. ej. `cancelled`)? → A: No; se rechazan con motivo `not_completed`.
- Q: ¿Qué hacer con líneas sin tienda (`store_id` vacío)? → A: Se rechazan con motivo `missing_store`; no se inventa una tienda "desconocida".

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Consultar ventas diarias por tienda (Priority: P1)

Cada mañana, Operaciones consulta cuánto vendió cada tienda el día anterior (pedidos, unidades
e importe bruto) para comparar tiendas.

**Why this priority**: es el motivo de la feature; sin esta tabla no hay entregable.

**Independent Test**: ejecutar el pipeline sobre `data/raw/orders.csv` (14 líneas) y comparar la tabla
resultante con las cifras de los escenarios.

**Acceptance Scenarios**:

1. **Given** el fichero de ejemplo, **When** se ejecuta el pipeline, **Then** `daily_sales` contiene exactamente:

   | store_id | sales_date | orders | units | gross_revenue |
   |----------|------------|--------|-------|---------------|
   | S01      | 2026-10-01 | 2      | 4     | 7.95          |
   | S01      | 2026-10-02 | 2      | 6     | 18.75         |
   | S02      | 2026-10-01 | 1      | 6     | 7.50          |
   | S02      | 2026-10-02 | 2      | 6     | 15.80         |

2. **Given** el pedido `O-1006` con `order_ts = 2026-10-01T22:30:00Z` (00:30 del día 2 en Madrid),
   **When** se ejecuta el pipeline, **Then** cuenta en S01 / **2026-10-02**, y S01 / 2026-10-01 queda en
   `gross_revenue = 7.95` (no 13.95).
3. **Given** la línea `O-1003 / 1` repetida dos veces, **When** se ejecuta el pipeline, **Then** S02 / 2026-10-01
   tiene `units = 6` y `gross_revenue = 7.50` (no 12 y 15.00).
4. **Given** que el pipeline ya se ejecutó, **When** se vuelve a ejecutar con la misma entrada, **Then**
   `daily_sales` es idéntica.

---

### User Story 2 - Saber por qué se descartó una línea (Priority: P2)

Cuando una cifra no cuadra, el equipo de datos necesita ver qué líneas se descartaron y por qué.

**Why this priority**: sin trazabilidad, cualquier descuadre exige revisar el CSV línea a línea.

**Independent Test**: ejecutar el pipeline y comprobar `rejected_lines` y el balance de filas.

**Acceptance Scenarios**:

1. **Given** el fichero de ejemplo, **When** se ejecuta el pipeline, **Then** `rejected_lines` contiene 5 líneas:
   `O-1003` (`duplicate`), `O-1004` (`not_completed`), `O-1005` (`non_positive_quantity`),
   `O-1009` (`non_positive_quantity`) y `O-1010` (`missing_store`).
2. **Given** el fichero de ejemplo, **When** se ejecuta el pipeline, **Then** líneas leídas (14) = líneas válidas (9) + rechazadas (5).

---

### Edge Cases

- Línea con cantidad 0 (`O-1005`) o negativa (`O-1009`, devolución): se rechaza como `non_positive_quantity`.
- Línea que cumple varios motivos de rechazo: se le asigna **solo el primero** según el orden
  `duplicate` → `missing_store` → `not_completed` → `non_positive_quantity`.
- Pedido cerca de medianoche en UTC: el día se decide en hora de Madrid (incluido el cambio de horario).
- Fichero sin ninguna línea válida: `daily_sales` queda vacía y todas las líneas aparecen en `rejected_lines`.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: El sistema MUST generar una fila de `daily_sales` por cada combinación tienda + día con al menos una línea válida.
- **FR-002**: `orders` MUST ser el número de pedidos distintos; `units`, la suma de cantidades; `gross_revenue`, la suma de `quantity × unit_price` de las líneas válidas.
- **FR-003**: El día de venta MUST calcularse en hora de Madrid (Europe/Madrid).
- **FR-004**: Una línea es válida solo si: no es duplicada, tiene tienda, su pedido está `completed` y su cantidad es > 0.
- **FR-005**: Toda línea no válida MUST registrarse en `rejected_lines` con su motivo.
- **FR-006**: Cada línea rechazada MUST tener un único motivo, el primero según el orden de los Edge Cases.
- **FR-007**: Reejecutar el pipeline con la misma entrada MUST producir el mismo resultado.

### Key Entities

- **Línea de pedido (entrada)**: un producto dentro de un pedido; identificada por `order_id` + `line_id`; tiene tienda, momento (UTC), cantidad, precio unitario y estado del pedido.
- **Venta diaria (`daily_sales`)**: agregado por tienda y día de Madrid; clave `store_id` + `sales_date`.
- **Línea rechazada (`rejected_lines`)**: referencia a la línea de entrada más su motivo de rechazo.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Las 4 filas del escenario 1 de US1 coinciden al céntimo con lo esperado.
- **SC-002**: El 100 % de las líneas leídas está o en una venta diaria o en `rejected_lines` (0 pérdidas silenciosas).
- **SC-003**: Operaciones obtiene las ventas del día anterior de todas las tiendas en una sola consulta, sin cálculos manuales.
- **SC-004**: Dos ejecuciones consecutivas producen resultados idénticos en el 100 % de los casos.

## Assumptions

- El CSV llega completo una vez al día; la carga incremental queda fuera de alcance.
- Los importes del CSV ya incluyen impuestos; no se calcula neto ni IVA.
- Las devoluciones (cantidad negativa) se tratarán en otra feature; aquí solo se rechazan.
- `order_ts` viene siempre en UTC con sufijo `Z`.

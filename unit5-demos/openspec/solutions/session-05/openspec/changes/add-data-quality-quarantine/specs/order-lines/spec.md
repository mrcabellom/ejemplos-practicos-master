# Spec Delta

## MODIFIED Requirements

### Requirement: Tratamiento de filas inválidas
Las filas de bronze que incumplan cualquier regla de calidad de la capability `data-quality` (incluida una cantidad menor o igual que 0) SHALL excluirse de `silver.order_lines` y registrarse en `silver.order_lines_quarantine`.

#### Scenario: Precio no numérico
- **WHEN** bronze contiene la línea del pedido O-1007 con `unit_price` = `abc`
- **THEN** el pedido O-1007 no aparece en `silver.order_lines`
- **AND** aparece en `silver.order_lines_quarantine` con `dq_failed_rules` = [DQ004]

#### Scenario: Línea sin identificador de pedido
- **WHEN** bronze contiene una línea con `order_id` vacío
- **THEN** esa línea no aparece en `silver.order_lines`
- **AND** aparece en `silver.order_lines_quarantine` con `dq_failed_rules` = [DQ001]

#### Scenario: Cantidad negativa
- **WHEN** bronze contiene la línea del pedido O-1006 con `quantity` = `-2`
- **THEN** O-1006 no aparece en `silver.order_lines` ni contribuye a `gold.daily_sales`

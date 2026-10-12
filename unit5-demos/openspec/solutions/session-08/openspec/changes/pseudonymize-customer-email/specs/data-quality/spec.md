# Spec Delta

## MODIFIED Requirements

### Requirement: Tabla de cuarentena
Las filas que incumplen al menos una regla SHALL escribirse en `silver.order_lines_quarantine` con sus columnas de bronze salvo `customer_email`, que se sustituye por `customer_key`, junto con la lista `dq_failed_rules` con los códigos incumplidos y `_quarantined_at`. La tabla SHALL reconstruirse en cada ejecución junto con `silver.order_lines`.

#### Scenario: Fila con varios fallos
- **WHEN** una fila tiene `order_id` vacío y `quantity` = `0`
- **THEN** la cuarentena contiene una única fila para ella con `dq_failed_rules` = [DQ001, DQ003]

#### Scenario: Reconstrucción sin duplicados
- **WHEN** el pipeline se ejecuta dos veces sobre los mismos datos de bronze
- **THEN** la cuarentena contiene las mismas filas que tras la primera ejecución

#### Scenario: Sin email en claro en cuarentena
- **WHEN** la fila sin `order_id` con email `sin.pedido@example.com` entra en cuarentena
- **THEN** la cuarentena guarda su `customer_key` y no contiene `sin.pedido@example.com`

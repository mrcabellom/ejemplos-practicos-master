# Spec Delta

## Purpose

Hacer visible y medible la calidad de las líneas de pedido: reglas explícitas con código y una cuarentena trazable de las filas que no las cumplen.

## ADDED Requirements

### Requirement: Reglas de calidad de líneas de pedido
Cada fila de `bronze.orders_raw` SHALL evaluarse contra estas reglas: DQ001 `order_id` informado; DQ002 `order_ts` es un timestamp válido; DQ003 `quantity` es un entero mayor que 0; DQ004 `unit_price` es un decimal mayor o igual que 0; DQ005 `status` es `completed`, `returned` o `cancelled`.

#### Scenario: Cantidad negativa
- **WHEN** la línea del pedido O-1006 tiene `quantity` = `-2`
- **THEN** la línea incumple DQ003

#### Scenario: Línea correcta
- **WHEN** la línea del pedido O-1002 tiene todos sus campos válidos
- **THEN** la línea no incumple ninguna regla

### Requirement: Tabla de cuarentena
Las filas que incumplen al menos una regla SHALL escribirse en `silver.order_lines_quarantine` con todas sus columnas de bronze, la lista `dq_failed_rules` con los códigos incumplidos y `_quarantined_at`. La tabla SHALL reconstruirse en cada ejecución junto con `silver.order_lines`.

#### Scenario: Fila con varios fallos
- **WHEN** una fila tiene `order_id` vacío y `quantity` = `0`
- **THEN** la cuarentena contiene una única fila para ella con `dq_failed_rules` = [DQ001, DQ003]

#### Scenario: Reconstrucción sin duplicados
- **WHEN** el pipeline se ejecuta dos veces sobre los mismos datos de bronze
- **THEN** la cuarentena contiene las mismas filas que tras la primera ejecución

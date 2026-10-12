# Spec Delta

## Purpose

Minimizar la exposición de datos personales de clientes en la plataforma de datos, sustituyéndolos por seudónimos estables fuera de bronze y limitando cuánto tiempo se conserva el dato en claro.

## ADDED Requirements

### Requirement: Seudonimización del email de cliente
Fuera de bronze, el email de cliente SHALL representarse solo como `customer_key`: el HMAC-SHA256 en hexadecimal del email normalizado (minúsculas y sin espacios) con la clave de seudonimización. El mismo email MUST producir siempre el mismo `customer_key`.

#### Scenario: Mismo cliente con distinto formato
- **WHEN** bronze contiene `Ana.Garcia@Example.com ` el 2026-10-01 y `ana.garcia@example.com` el 2026-10-02
- **THEN** ambas líneas tienen el mismo `customer_key` en silver

#### Scenario: Clientes distintos
- **WHEN** bronze contiene `ana.garcia@example.com` y `luis.perez@example.com`
- **THEN** sus `customer_key` son distintos

#### Scenario: Email no recuperable desde silver
- **WHEN** un analista consulta cualquier tabla de silver o gold
- **THEN** ninguna columna contiene un email en claro

### Requirement: Clave de seudonimización obligatoria
El pipeline MUST obtener la clave de la variable de entorno `MERCALUZ_PII_KEY` y terminar con error antes de construir silver si no está definida o tiene menos de 32 caracteres. La clave MUST NOT escribirse en logs, tablas ni ficheros.

#### Scenario: Clave ausente
- **WHEN** se ejecuta el pipeline sin `MERCALUZ_PII_KEY`
- **THEN** la ejecución termina con un error que menciona `MERCALUZ_PII_KEY`
- **AND** `silver.order_lines` no cambia

#### Scenario: Clave no expuesta
- **WHEN** el pipeline se ejecuta con una clave válida
- **THEN** el valor de la clave no aparece en la salida de la ejecución

### Requirement: Retención del email en claro en bronze
En cada ejecución, el pipeline SHALL poner a NULL `customer_email` en las filas de `bronze.orders_raw` cuyo `_ingested_at` tenga más de 30 días, sin modificar el resto de columnas.

#### Scenario: Fila antigua
- **WHEN** una fila de bronze tiene `_ingested_at` de hace 31 días
- **THEN** tras la ejecución su `customer_email` es NULL y su `order_id` se conserva

#### Scenario: Fila reciente
- **WHEN** una fila de bronze tiene `_ingested_at` de hace 29 días
- **THEN** tras la ejecución conserva su `customer_email`

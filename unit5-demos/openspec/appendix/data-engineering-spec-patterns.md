# Patrones de specs para Data Engineering

Plantillas de requisitos habituales en cualquier plataforma de datos. Pueden copiarse y adaptarse con los datos concretos de cada caso. Todos los ejemplos siguen el formato que valida OpenSpec.

---

## 1. Ingesta

### Fichero o partición ausente

```markdown
### Requirement: Fichero de origen ausente
Si no existe el fichero de la fecha solicitada, el pipeline MUST terminar con error indicando la ruta esperada y sin modificar el destino.

#### Scenario: Fecha sin fichero
- **WHEN** se ejecuta para 2026-09-30 y no existe `2026-09-30.csv`
- **THEN** la ejecución termina con error que menciona `2026-09-30.csv`
- **AND** `bronze.orders_raw` no cambia
```

### Idempotencia

```markdown
### Requirement: Reprocesado idempotente
Reprocesar una partición SHALL dejar el destino en el mismo estado que una única ejecución con los mismos datos de entrada.

#### Scenario: Doble ejecución
- **WHEN** se procesa dos veces la fecha 2026-10-01 con el mismo fichero de 10 filas
- **THEN** el destino contiene exactamente 10 filas para esa fecha
```

### Llegadas tardías

```markdown
### Requirement: Datos que llegan tarde
Las filas con fecha de negocio anterior a la partición procesada SHALL cargarse en la partición de su fecha de negocio, no en la de llegada.

#### Scenario: Pedido del día anterior en el fichero de hoy
- **WHEN** el fichero de 2026-10-02 contiene el pedido O-0999 con `order_ts` 2026-10-01T23:58:00
- **THEN** O-0999 se agrega en las ventas del 2026-10-01
```

## 2. Esquema y contratos

### Cambio de esquema en origen (schema drift)

```markdown
### Requirement: Columna nueva en el fichero de origen
Si el fichero trae columnas no esperadas, el pipeline SHALL cargar las columnas conocidas, ignorar las nuevas y registrar en el log sus nombres.

#### Scenario: Columna promo_code inesperada
- **WHEN** `2026-10-03.csv` incluye la columna `promo_code`
- **THEN** la carga termina con éxito y el log menciona `promo_code`
```

```markdown
### Requirement: Columna obligatoria ausente
Si falta una columna obligatoria, el pipeline MUST terminar con error listando las columnas ausentes, sin cargar ninguna fila.

#### Scenario: Falta unit_price
- **WHEN** `2026-10-03.csv` no tiene la columna `unit_price`
- **THEN** la ejecución termina con error que menciona `unit_price`
```

### Contrato de una tabla publicada

```markdown
### Requirement: Esquema de gold.daily_sales
`gold.daily_sales` SHALL tener exactamente las columnas `order_date` (DATE), `store_id` (VARCHAR), `orders_count` (INTEGER) y `gross_revenue` (DECIMAL(12,2)), con clave única (`order_date`, `store_id`).

#### Scenario: Unicidad
- **WHEN** silver contiene 3 pedidos de MAD-001 el 2026-10-01
- **THEN** gold tiene una única fila para (2026-10-01, MAD-001)
```

### Vista de compatibilidad (breaking change)

```markdown
### Requirement: Vista de compatibilidad v1
Hasta el 2026-12-31 SHALL existir `gold.daily_sales_v1` con el esquema anterior al cambio.

#### Scenario: Consumidor antiguo
- **WHEN** un informe consulta `gold.daily_sales_v1`
- **THEN** obtiene las mismas columnas y valores que antes del cambio
```

## 3. Calidad de datos

```markdown
### Requirement: Regla de calidad codificada
Cada fila SHALL evaluarse contra la regla DQ003: `quantity` es un entero mayor que 0.

#### Scenario: Cantidad negativa
- **WHEN** la línea O-1006 tiene `quantity` = `-2`
- **THEN** la fila incumple DQ003 y va a cuarentena
```

```markdown
### Requirement: Umbral de calidad
Si más del 5 % de las filas de un fichero incumplen alguna regla, la ejecución MUST fallar antes de publicar gold.

#### Scenario: Fichero corrupto
- **WHEN** 3 de 10 filas de `2026-10-01.csv` incumplen reglas
- **THEN** la ejecución falla mencionando `30.0%` y gold conserva su versión anterior
```

```markdown
### Requirement: Reconciliación de volúmenes
El número de filas de silver más las de cuarentena SHALL coincidir con las filas de bronze evaluadas, descontando duplicados y cancelados.

#### Scenario: Cuadre de un día
- **WHEN** bronze tiene 10 filas de 2026-10-01, 1 duplicada y 1 cancelada, y 3 en cuarentena
- **THEN** silver tiene 5 filas de ese fichero
```

## 4. Frescura y SLA

```markdown
### Requirement: Frescura de gold
`gold.daily_sales` SHALL contener los datos del día D antes de las 07:00 UTC del día D+1.

#### Scenario: Retraso del fichero de origen
- **WHEN** a las 06:00 UTC no ha llegado el fichero del día D
- **THEN** el pipeline termina con error de fichero ausente y la alerta de SLA se dispara
```

## 5. Métricas de negocio

**Regla:** toda métrica con un cálculo no trivial necesita un escenario con **cifras calculadas manualmente**.

```markdown
### Requirement: Cálculo de ventas netas sin IVA
`net_revenue` SHALL ser la suma por línea de importe / (1 + IVA de su categoría), positiva para `completed` y negativa para `returned`, redondeando solo el total a dos decimales.

#### Scenario: Redondeo al final
- **WHEN** una tienda tiene líneas de 5,70 al 4 %, 8,49 al 10 % y 11,90 al 21 %
- **THEN** `net_revenue` = 23,03
```

## 6. Datos personales y seguridad

```markdown
### Requirement: Sin PII en capas analíticas
Ninguna tabla de silver o gold SHALL contener emails, teléfonos ni documentos de identidad en claro.

#### Scenario: Auditoría de columnas
- **WHEN** se inspeccionan todas las columnas de silver y gold
- **THEN** ningún valor coincide con el patrón de un email
```

```markdown
### Requirement: Secreto obligatorio
El pipeline MUST terminar con error antes de procesar datos si la variable `MERCALUZ_PII_KEY` no está definida, y MUST NOT escribir su valor en logs.

#### Scenario: Secreto ausente
- **WHEN** se ejecuta sin `MERCALUZ_PII_KEY`
- **THEN** la ejecución falla mencionando `MERCALUZ_PII_KEY`
```

```markdown
### Requirement: Retención del dato en claro
Los datos personales en bronze SHALL anonimizarse cuando su `_ingested_at` supere los 30 días.

#### Scenario: Fila de 31 días
- **WHEN** una fila de bronze tiene `_ingested_at` de hace 31 días
- **THEN** su `customer_email` es NULL tras la ejecución
```

## 7. Exports e interfaces con otros equipos

```markdown
### Requirement: Formato del fichero para Finanzas
El export SHALL usar `;` como separador, coma decimal, dos decimales y UTF-8, con la cabecera `date;store;orders;gross_sales`.

#### Scenario: Línea de ejemplo
- **WHEN** gold tiene (2026-10-01, MAD-001, 2, 26.09)
- **THEN** el fichero contiene `2026-10-01;MAD-001;2;26,09`
```

---

## ¿Spec o design? Casos frecuentes en Data Engineering

| Afirmación | Va en |
|---|---|
| "Reprocesar no duplica" | **spec** (observable) |
| "Usamos DELETE + INSERT en una transacción" | design |
| "La tabla está particionada por `order_date`" | design (salvo que un consumidor dependa de ello) |
| "gold está disponible antes de las 07:00" | **spec** (SLA) |
| "Usamos Great Expectations" | design |
| "Una fila con 2 fallos genera 1 fila de cuarentena" | **spec** |
| "El job usa 4 workers de Spark" | design (o ninguno de los dos) |
| "Los importes son DECIMAL(12,2)" | **spec** si es un contrato publicado; design si es interno |

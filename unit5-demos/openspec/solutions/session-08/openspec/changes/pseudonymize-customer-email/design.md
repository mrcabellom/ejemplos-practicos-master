# Design

## Context

El email entra por bronze (copia literal) y se propaga a `silver.order_lines` y a `silver.order_lines_quarantine`. Gold no lo usa. El único consumidor real es el informe "Clientes recurrentes", que solo necesita contar clientes distintos. Las alternativas se analizaron con la DPO durante la exploración (`/opsx:explore`).

## Goals / Non-Goals

**Goals:**
- Que nadie fuera de Data Platform pueda leer emails.
- Mantener la capacidad de contar clientes distintos y recurrentes.

**Non-Goals:**
- Derecho al olvido (borrado por cliente): requiere un change propio.
- Cifrar bronze: bronze ya tiene acceso restringido al equipo de plataforma.

## Decisions

1. **HMAC-SHA256 con clave secreta**, frente a estas alternativas:
   - *Eliminar el email*: impide medir la recurrencia. Descartada.
   - *SHA-256 sin clave*: reversible mediante diccionario, porque los emails son predecibles. La DPO la considera insuficiente.
   - *Tokenización con bóveda*: reversible de forma controlada y más segura, pero requiere un servicio que no existe. Desproporcionada para este caso.
   - *HMAC con clave*: estable, no reversible sin la clave y sin infraestructura nueva. **Elegida.**
2. **Cálculo en Python** con `hmac` y `hashlib`, registrado como función en DuckDB, porque DuckDB no tiene HMAC nativo.
3. **Retención en bronze por `_ingested_at`**, con un `UPDATE` al inicio de cada ejecución. 30 días dan margen para reprocesar un mes completo.
4. **Validación de la clave al arrancar** (existe y tiene al menos 32 caracteres) para fallar pronto y no generar nunca seudónimos con una clave débil.

## Risks / Trade-offs

- [La pérdida o rotación de la clave cambia todos los `customer_key`] → Clave en el gestor de secretos con copia de seguridad; rotarla exige reconstruir silver (procedimiento documentado).
- [Reprocesar fechas de más de 30 días produce `customer_key` NULL] → Aceptado: el reprocesado de datos antiguos pierde la dimensión cliente; avisar a BI.

## Migration Plan

1. Crear el secreto en producción y una clave de prueba en `.env.example`.
2. Desplegar; la primera ejecución reconstruye silver y la cuarentena ya seudonimizadas y limpia los emails antiguos de bronze.
3. BI cambia el informe "Clientes recurrentes" a `customer_key`.
4. Rollback: desplegar la versión anterior. Los emails ya borrados de bronze (más de 30 días) **no se recuperan**; la DPO lo ha aceptado.

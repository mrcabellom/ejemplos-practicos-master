# Tasks

## 1. Clave y función de seudonimización

- [ ] 1.1 Leer y validar `MERCALUZ_PII_KEY` al arrancar; verificar con tests que sin clave o con una clave corta la ejecución falla mencionando `MERCALUZ_PII_KEY`
- [ ] 1.2 Registrar en DuckDB la función HMAC-SHA256 sobre el email normalizado; verificar con un test que ` Ana.Garcia@Example.com ` y `ana.garcia@example.com` dan el mismo valor
- [ ] 1.3 Verificar con `capsys` que el valor de la clave no aparece en la salida

## 2. Silver y cuarentena

- [ ] 2.1 Sustituir `customer_email` por `customer_key` en `silver.order_lines`; verificar con un test que la tabla no tiene columna `customer_email`
- [ ] 2.2 Sustituir el email por `customer_key` en `silver.order_lines_quarantine`; verificar con un test que no contiene `sin.pedido@example.com`

## 3. Retención en bronze

- [ ] 3.1 Poner a NULL los emails de bronze con `_ingested_at` de más de 30 días; verificar con tests de 29 y 31 días

## 4. Configuración

- [ ] 4.1 Añadir `.env.example` con una clave de prueba de 32 caracteres o más y documentar en README.md cómo configurarla; verificar que `uv run pytest` pasa completo con la clave de prueba

## Workflow follow-up

- Revisión de la DPO antes de `/opsx:apply`.
- Crear el secreto en el entorno de producción antes del despliegue.

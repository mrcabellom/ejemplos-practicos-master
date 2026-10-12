# Proposal

## Why

La auditoría RGPD de la DPO ha detectado que `customer_email` llega en claro a `silver.order_lines` y a la cuarentena, tablas a las que acceden unas 40 personas de BI que no necesitan identificar a nadie: solo contar clientes distintos y su recurrencia. Incumple el principio de minimización (art. 5.1.c RGPD) y hay que corregirlo antes de la auditoría externa de diciembre.

## What Changes

- **BREAKING** `silver.order_lines` sustituye `customer_email` por `customer_key`, un seudónimo estable (HMAC-SHA256 con clave secreta) que permite contar clientes sin identificarlos.
- La cuarentena de calidad deja de guardar el email en claro.
- El pipeline exige la clave de seudonimización y falla si no está configurada.
- El email en claro solo se conserva en bronze durante 30 días.

## Capabilities

### New Capabilities
- `pii-protection`: seudonimización de datos personales, gestión de la clave y retención del dato en claro en bronze.

### Modified Capabilities
- `order-lines`: la columna `customer_email` se sustituye por `customer_key`.
- `data-quality`: la cuarentena guarda `customer_key` en lugar del email.

## Impact

- Tablas: `silver.order_lines`, `silver.order_lines_quarantine`, `bronze.orders_raw` (borrado de emails de más de 30 días).
- Consumidores: el informe de Power BI "Clientes recurrentes" pasa a contar `customer_key` (mismo resultado). Nadie más usa el email (confirmado con BI).
- Seguridad: nuevo secreto `MERCALUZ_PII_KEY` en el gestor de secretos de producción y, en local, un valor de prueba en `.env.example`.
- Legal: la DPO revisa este change antes de implementarlo.

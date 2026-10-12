# mercaluz-data-platform

Repositorio del equipo de **Data Platform** de **Mercaluz**, una cadena española de supermercados ficticia
(120 tiendas y una tienda online).

Este es el estado del repositorio al terminar las sesiones del núcleo del taller (de la 0 a la 6): el pipeline
diario de pedidos ya está construido y especificado con OpenSpec. Es el punto de partida de las sesiones avanzadas.

## Qué hay ya

```
data/landing/orders/YYYY-MM-DD.csv   ← ficheros diarios de pedidos que envían los TPV y la tienda online
query.py                             ← utilidad para consultar el warehouse local
pyproject.toml, uv.lock              ← proyecto Python 3.12 gestionado con uv (duckdb, rich, pytest)
```

Cada fichero de landing tiene una fila por línea de pedido:

| Columna | Descripción |
|---|---|
| `order_id` | Identificador del pedido (un pedido puede tener varias líneas) |
| `order_ts` | Fecha y hora del pedido |
| `store_id` | Código de la tienda, por ejemplo `MAD-001` |
| `customer_email` | Email del cliente (dato personal) |
| `product_sku`, `category` | Producto y categoría del producto |
| `quantity`, `unit_price` | Unidades y precio por unidad (IVA incluido) |
| `status` | `completed`, `returned` o `cancelled` |

Los ficheros vienen de sistemas externos y pueden contener errores.

## Arquitectura objetivo (medallion)

```
data/landing/orders/YYYY-MM-DD.csv
        ▼
bronze.orders_raw          ← copia literal de cada fichero, todas las columnas como texto
        ▼
silver.order_lines         ← líneas de pedido tipadas y depuradas
        ▼
gold.daily_sales           ← ventas por día y tienda (las consume Power BI)
        ▼
exports/finance_daily_sales.csv   ← fichero diario para la macro de Excel de Finanzas
```

El warehouse local es un fichero DuckDB en `warehouse/mercaluz.duckdb`.

## Uso

La versión de Python (3.12) está fijada en `.python-version`. Si no está instalada, `uv sync` la descarga.

Crea `.venv` con Python 3.12, duckdb, rich y pytest:

```bash
uv sync
```

Ejecuta los tests:

```bash
uv run pytest
```

Procesa todos los ficheros de landing:

```bash
uv run python run_pipeline.py --all
```

Muestra una tabla del warehouse (o el resultado de cualquier consulta SQL):

```bash
uv run python query.py gold.daily_sales
```

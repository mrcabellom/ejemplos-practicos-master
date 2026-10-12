# la-despensa-data

Repositorio del equipo de datos de **La Despensa**, una cadena de alimentación ficticia de Madrid con dos tiendas
(`S01` y `S02`).

Cada noche, el sistema de punto de venta exporta las líneas de pedido del día a un fichero CSV. El equipo de
Operaciones quiere una tabla de ventas diarias construida a partir de ese fichero. Este repositorio contiene la
petición, los datos de origen y las herramientas de Python. El pipeline se construye con *spec-driven development*
(GitHub Spec Kit).

## Qué hay ya

```
docs/brief.md            ← petición de Lucía Herrero, responsable de Operaciones
data/raw/orders.csv      ← 14 líneas de pedido de las tiendas S01 y S02
pyproject.toml, uv.lock  ← proyecto Python 3.12 gestionado con uv (duckdb, pytest)
.python-version          ← fija Python 3.12
```

Cada línea de `orders.csv` es un producto dentro de un pedido:

| Columna | Descripción |
|---|---|
| `order_id`, `line_id` | Identificador del pedido y número de línea dentro del pedido |
| `order_ts` | Fecha y hora del pedido, en UTC (por ejemplo `2026-10-01T08:15:00Z`) |
| `store_id` | Código de la tienda: `S01` o `S02` |
| `product_id` | Código del producto, por ejemplo `P-MILK` |
| `quantity`, `unit_price` | Unidades y precio por unidad, en euros |
| `status` | Estado del pedido: `completed` o `cancelled` |

El fichero viene del sistema de punto de venta y puede contener errores.

## Uso

La versión de Python (3.12) está fijada en `.python-version`. Si no está instalada, `uv sync` la descarga.

```bash
uv sync
```

El paquete `src/daily_sales/` y la carpeta `tests/` todavía no existen: se crean al construir el pipeline.

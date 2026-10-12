# Tasks

## 1. Tabla gold.daily_sales

- [ ] 1.1 Construir `gold.daily_sales` con `orders_count` y `total_amount` de las líneas completadas; verificar con un test que (2026-10-01, MAD-001) tiene 2 pedidos y 26,09
- [ ] 1.2 Verificar con un test que la devolución de O-1004 no cuenta: (2026-10-01, BCN-014) tiene 1 pedido y 1,60

## 2. Pipeline

- [ ] 2.1 Añadir el paso de gold a `run_pipeline.py` (`[gold] daily_sales: <n> rows`); verificar que `uv run python run_pipeline.py --all` muestra 6 filas

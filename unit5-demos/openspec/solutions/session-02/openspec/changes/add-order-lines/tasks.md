# Tasks

## 1. Tabla silver.order_lines

- [ ] 1.1 Construir `silver.order_lines` a partir de bronze con los tipos indicados y `order_date`; verificar con un test que O-1002 tiene `order_date` = 2026-10-01
- [ ] 1.2 Normalizar `customer_email`; verificar con un test que ` Ana.Garcia@Example.com ` queda como `ana.garcia@example.com`

## 2. Depuración

- [ ] 2.1 Excluir las filas sin `order_id` o que no se pueden tipar; verificar con un test que O-1007 y la línea sin `order_id` no aparecen
- [ ] 2.2 Deduplicar por (`order_id`, `product_sku`); verificar con un test que O-1003 aparece una vez
- [ ] 2.3 Excluir los pedidos cancelados; verificar con un test que O-1005 no aparece y que quedan 6 líneas del 2026-10-01

## 3. Pipeline

- [ ] 3.1 Añadir el paso de silver a `run_pipeline.py` (`[silver] order_lines: <n> rows`); verificar que `uv run python run_pipeline.py --all` muestra 11 líneas

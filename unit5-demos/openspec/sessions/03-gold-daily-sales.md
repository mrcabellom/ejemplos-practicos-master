# Sesión 3 · Gold: ventas diarias por tienda

**Resultado:** la tabla `gold.daily_sales` que consumirá Power BI, con escenarios basados en cifras calculadas manualmente. Y el primer problema del pipeline, detectado al revisar los datos.

**Conceptos nuevos:** escenarios con cifras, decisiones de negocio explícitas en la spec, seguimiento de un dato a través de las capas.

---

## 3.1 La petición

> **De:** equipo de BI
> **Asunto:** Ventas diarias para el cuadro de mando
>
> Para el cuadro de mando de tiendas necesitamos, por día y tienda, el número de pedidos y el importe vendido.
> Las devoluciones no deben contar como ventas.

## 3.2 Proponer

```text
/clear
/opsx:propose add-daily-sales

BI necesita las ventas diarias por tienda para el cuadro de mando de Power BI:
- Nueva tabla gold.daily_sales con una fila por (order_date, store_id), reconstruida desde silver en cada ejecución.
- orders_count: número de pedidos distintos con líneas completed.
- total_amount: suma de quantity * unit_price de las líneas completed (IVA incluido), DECIMAL(12,2).
- Las devoluciones (returned) no cuentan en ninguna métrica.
La spec debe tener dos requisitos: las ventas diarias por tienda y el tratamiento de las devoluciones.
Usa en los escenarios cifras calculadas a mano con 2026-10-01.csv (MAD-001 y BCN-014).
```

## 3.3 Revisar: comprobar las cifras

Los escenarios de este change contienen **cálculos**. Hay que comprobarlos manualmente **antes** de implementar: si la spec contiene una cifra incorrecta, la IA escribirá un código que produce esa misma cifra incorrecta.

**MAD-001, 2026-10-01:**

| Pedido | Línea | Importe |
|---|---|---|
| O-1001 | 6 × 0,95 | 5,70 |
| O-1001 | 1 × 8,49 | 8,49 |
| O-1002 | 1 × 11,90 | 11,90 |
| **2 pedidos** | | **26,09** |

**BCN-014, 2026-10-01:** O-1003 (2 × 0,80 = 1,60) está completado; O-1004 (3 × 6,50 = 19,50) es una devolución y no cuenta. Resultado: 1 pedido y 1,60.

Comprueba en la spec:

- [ ] El escenario de MAD-001 indica `orders_count` = 2 y `total_amount` = 26,09.
- [ ] El tratamiento de las devoluciones figura como **requisito propio**, con el escenario de BCN-014. Es una decisión de negocio, y debe quedar escrita para que nadie la descubra leyendo el código.
- [ ] El `orders_count` cuenta pedidos **distintos**: O-1001 tiene dos líneas, pero es un solo pedido.

```bash
openspec validate add-daily-sales --strict
```

Compara con la referencia: [`solutions/session-03/`](../solutions/session-03/openspec/changes/add-daily-sales/).

```bash
git add openspec
```

```bash
git commit -m "Propose add-daily-sales"
```

## 3.4 Implementar

```text
/clear
/opsx:apply add-daily-sales
```

```bash
uv run pytest
```

```bash
uv run python run_pipeline.py --all
```

```
[bronze] 2026-10-01: 10 rows loaded
[bronze] 2026-10-02: 5 rows loaded
[silver] order_lines: 11 rows
[gold]   daily_sales: 6 rows
```

```bash
uv run python query.py gold.daily_sales
```

```
┌────────────┬──────────┬──────────────┬───────────────┐
│ order_date │ store_id │ orders_count │  total_amount │
│ date       │ varchar  │       bigint │ decimal(12,2) │
├────────────┼──────────┼──────────────┼───────────────┤
│ 2026-10-01 │ BCN-014  │            1 │          1.60 │
│ 2026-10-01 │ MAD-001  │            2 │         26.09 │
│ 2026-10-01 │ VLC-007  │            1 │         -7.50 │
│ 2026-10-02 │ BCN-014  │            1 │          8.40 │
│ 2026-10-02 │ MAD-001  │            1 │          2.95 │
│ 2026-10-02 │ VLC-007  │            1 │         23.48 │
└────────────┴──────────┴──────────────┴───────────────┘
6 rows
```

Las cifras de MAD-001 y BCN-014 coinciden con las calculadas. Pero hay algo más.

## 3.5 Un problema: ventas negativas

VLC-007 tiene **-7,50 €** de ventas el 1 de octubre. Las ventas negativas no tienen sentido. Para encontrar el origen, sigue el dato hacia atrás, capa a capa:

```bash
uv run python query.py "SELECT order_id, quantity, unit_price, status FROM silver.order_lines WHERE store_id = 'VLC-007' AND order_date = '2026-10-01'"
```

La única línea es O-1006, con cantidad -2 (-2 × 3,75 = -7,50). En bronze, el valor ya llegaba así desde el fichero de cajas.

¿Es un error del código? No: el código hace exactamente lo que dicen las specs. Ninguna spec indicaba qué hacer con una cantidad negativa (es lo que se anotó en la revisión de la sesión 2). El problema está en la **especificación**, y se corregirá modificando una spec en la sesión 5.

Así lo registra el equipo:

> **DATA-142 · Ventas negativas en Power BI** · Prioridad: alta
>
> El cuadro de mando muestra -7,50 € de ventas para VLC-007 el 1 de octubre. Origen: la línea O-1006 tiene
> cantidad -2 y ninguna regla la filtra.

## 3.6 Archivar

```text
/opsx:archive add-daily-sales
```

```bash
git add .
```

```bash
git commit -m "Add daily sales to gold"
```

## 3.7 Conclusiones

- Los escenarios con cifras calculadas manualmente son la mejor protección frente a errores en métricas: definen el resultado correcto antes de que exista el código.
- Las decisiones de negocio (las devoluciones no cuentan) deben figurar como requisitos explícitos.
- Seguir un dato a través de las capas permite localizar el origen de un problema. En este caso no es un fallo de programación, sino un caso que la especificación no contemplaba.

---

## Lista de comprobación final

- [ ] `gold.daily_sales` contiene 6 filas; MAD-001 tiene 26,09 el 2026-10-01
- [ ] Puedes explicar de dónde procede el -7,50 de VLC-007
- [ ] `uv run pytest` no devuelve errores
- [ ] `openspec list --specs` muestra 3 capabilities
- [ ] Los cambios están incluidos en un commit

**Siguiente:** [Sesión 4 · Export para Finanzas](04-finance-export.md)

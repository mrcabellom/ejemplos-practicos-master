# Sesión 2 · Silver: líneas de pedido depuradas

**Resultado:** la tabla `silver.order_lines`, con tipos correctos y sin duplicados ni pedidos cancelados, construida por la IA a partir de una nueva capability.

**Conceptos nuevos:** una capability con varios requisitos, nombres neutros para los requisitos, lo que la spec **no** dice.

---

## 2.1 La petición

> **De:** Lucía (Head of Data)
> **Asunto:** Líneas de pedido para análisis
>
> Bronze ya tiene los pedidos, pero como texto y con los problemas del origen. Para calcular ventas necesitamos
> una tabla de líneas de pedido con tipos correctos (fechas y números), sin líneas repetidas y sin pedidos cancelados.

## 2.2 Proponer

Limpia el contexto (`/clear`) y escribe:

```text
/opsx:propose add-order-lines

Necesitamos una tabla de líneas de pedido limpia en silver, reconstruida desde bronze en cada ejecución:
- silver.order_lines con tipos: order_ts TIMESTAMP, order_date DATE (derivada de order_ts), quantity INTEGER,
  unit_price DECIMAL(10,2); customer_email en minúsculas y sin espacios.
- Excluir las filas sin order_id o cuyos order_ts, quantity o unit_price no se puedan convertir a su tipo.
- Una sola fila por (order_id, product_sku): la de _ingested_at más reciente.
- Excluir los pedidos cancelados.
La spec debe tener cuatro requisitos: tipos de las líneas, filas inválidas, duplicados y pedidos cancelados.
Usa en los escenarios los pedidos reales de 2026-10-01.csv (O-1002, O-1003, O-1005, O-1007 y la línea sin order_id).
Fuera de alcance: otras reglas de negocio sobre los valores.
```

## 2.3 Revisar

```bash
openspec show add-order-lines
```

Comprueba:

- [ ] La nueva capability `order-lines` tiene `## Purpose` y un requisito por cada comportamiento: tipos, filas inválidas, duplicados y cancelados.
- [ ] Cada requisito tiene escenarios con los pedidos reales (O-1007 con `abc`, O-1003 repetido, O-1005 cancelado).
- [ ] Los **nombres** de los requisitos describen el tema, no la solución actual. Por ejemplo, "Tratamiento de filas inválidas" es mejor que "Descarte silencioso de filas inválidas": cuando el tratamiento cambie, el nombre seguirá siendo válido. Es una de las reglas de `config.yaml`.

Y una pregunta que conviene hacerse siempre: **¿qué casos no contempla la spec?** Revisa la tabla de particularidades de la [sesión 0](00-installation-and-setup.md#los-datos-de-entrada):

- [ ] ¿Qué dice la spec de O-1006, con cantidad `-2`? (La cantidad es un entero válido, así que no es una fila inválida según esta spec.)
- [ ] ¿Y de la devolución O-1004?

No hace falta resolverlo ahora: anótalo. La sesión 3 mostrará sus consecuencias.

```bash
openspec validate add-order-lines --strict
```

Compara con la referencia: [`solutions/session-02/`](../solutions/session-02/openspec/changes/add-order-lines/).

```bash
git add openspec
```

```bash
git commit -m "Propose add-order-lines"
```

## 2.4 Implementar

```text
/clear
/opsx:apply add-order-lines
```

Comprueba el resultado:

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
```

```bash
uv run python query.py "SELECT order_id, order_date, store_id, quantity, unit_price, status FROM silver.order_lines ORDER BY order_date, order_id, product_sku"
```

```
┌──────────┬────────────┬──────────┬──────────┬───────────────┬───────────┐
│ order_id │ order_date │ store_id │ quantity │    unit_price │ status    │
│ varchar  │ date       │ varchar  │  integer │ decimal(10,2) │ varchar   │
├──────────┼────────────┼──────────┼──────────┼───────────────┼───────────┤
│ O-1001   │ 2026-10-01 │ MAD-001  │        1 │          8.49 │ completed │
│ O-1001   │ 2026-10-01 │ MAD-001  │        6 │          0.95 │ completed │
│ O-1002   │ 2026-10-01 │ MAD-001  │        1 │         11.90 │ completed │
│ O-1003   │ 2026-10-01 │ BCN-014  │        2 │          0.80 │ completed │
│ O-1004   │ 2026-10-01 │ BCN-014  │        3 │          6.50 │ returned  │
│ O-1006   │ 2026-10-01 │ VLC-007  │       -2 │          3.75 │ completed │
│ O-1008   │ 2026-10-02 │ MAD-001  │        1 │          2.95 │ completed │
│ O-1009   │ 2026-10-02 │ BCN-014  │        2 │          4.20 │ completed │
│ O-1010   │ 2026-10-02 │ VLC-007  │        2 │          8.49 │ completed │
│ O-1010   │ 2026-10-02 │ VLC-007  │        1 │          6.50 │ completed │
│ O-1011   │ 2026-10-02 │ MAD-001  │        1 │         11.90 │ returned  │
└──────────┴────────────┴──────────┴──────────┴───────────────┴───────────┘
11 rows
```

Del 1 de octubre quedan 6 líneas: han desaparecido el duplicado de O-1003, el pedido cancelado O-1005, la línea sin `order_id` y O-1007. Ahora las columnas tienen tipo (`integer`, `decimal`, `date`). Y, tal como permite la spec, **O-1006 con cantidad -2 sigue ahí**.

> Si en tu implementación O-1006 no aparece, la IA ha añadido una validación que la spec no pedía. Revisa el código y pídele que se ajuste a la spec: el comportamiento del sistema debe estar en las specs, no solo en el código.

## 2.5 Archivar

```text
/opsx:archive add-order-lines
```

```bash
openspec list --specs
```

Ahora hay dos capabilities: `orders-ingestion` y `order-lines`.

```bash
git add .
```

```bash
git commit -m "Add order lines to silver"
```

## 2.6 Conclusiones

- Una capability agrupa varios requisitos relacionados; cada uno describe un comportamiento y tiene sus escenarios.
- Revisar una spec también es preguntarse qué deja fuera. Lo que la spec no dice, el sistema no lo garantiza.
- Los nombres neutros de los requisitos permiten modificarlos más adelante sin renombrarlos.

---

## Lista de comprobación final

- [ ] `silver.order_lines` contiene 11 líneas (6 del 1 de octubre)
- [ ] Las columnas tienen tipo: `integer`, `decimal(10,2)`, `date`, `timestamp`
- [ ] `uv run pytest` no devuelve errores
- [ ] `openspec list --specs` muestra 2 capabilities
- [ ] Los cambios están incluidos en un commit

**Siguiente:** [Sesión 3 · Gold: ventas diarias por tienda](03-gold-daily-sales.md)

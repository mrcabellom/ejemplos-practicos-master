# Sesión 4 · Export para Finanzas

**Resultado:** el fichero `exports/finance_daily_sales.csv` para la macro de Excel de Finanzas. Con él, el pipeline queda completo de principio a fin.

**Conceptos nuevos:** el formato de un fichero como contrato con otro equipo, la sección *Impact* de la proposal, primera mención de los cambios **BREAKING**.

---

## 4.1 La petición

> **De:** Marta (Control de Gestión)
> **Asunto:** Fichero diario de ventas
>
> No tengo acceso a Power BI: trabajo con una macro de Excel que lee un CSV cada mañana. Necesito un fichero
> con las ventas por día y tienda que mi Excel abra directamente. El formato es importante: mi Excel está
> configurado en español, por lo que el separador debe ser el punto y coma y los decimales deben ir con coma.

## 4.2 Proponer

```text
/clear
/opsx:propose add-finance-export

Control de Gestión (Finanzas) necesita un fichero diario para su macro de Excel:
- exports/finance_daily_sales.csv, generado en cada ejecución a partir de gold.daily_sales.
- Cabecera date;store;orders;total_amount y una línea por fila de gold, ordenadas por fecha y tienda.
- Formato de Excel en español: separador ; y coma decimal, siempre con dos decimales, UTF-8.
La spec debe tener dos requisitos: el contenido del fichero y el formato numérico.
Usa en los escenarios cifras reales de gold (MAD-001 y BCN-014 el 2026-10-01).
```

## 4.3 Revisar

```bash
openspec show add-finance-export
```

- [ ] La cabecera exacta (`date;store;orders;total_amount`) figura en la spec.
- [ ] Hay un escenario con una línea completa del fichero: `2026-10-01;MAD-001;2;26,09`.
- [ ] Hay un escenario para el formato de los decimales: 1,6 se escribe `1,60`.
- [ ] El apartado **Impact** de la proposal identifica a Finanzas como consumidor del fichero.

Este último punto es importante. A partir de ahora, la macro de Marta depende de los nombres y el orden de las columnas: el formato del fichero es un **contrato** con Finanzas. Cualquier cambio futuro en la cabecera la dejaría sin funcionar, y por eso debería marcarse como **BREAKING** en la proposal (es una de las reglas de `config.yaml`). La sesión 7 trata un cambio de este tipo.

```bash
openspec validate add-finance-export --strict
```

Compara con la referencia: [`solutions/session-04/`](../solutions/session-04/openspec/changes/add-finance-export/).

```bash
git add openspec
```

```bash
git commit -m "Propose add-finance-export"
```

## 4.4 Implementar

```text
/clear
/opsx:apply add-finance-export
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
[export] .../exports/finance_daily_sales.csv
```

Abre `exports/finance_daily_sales.csv` con un editor de texto:

```
date;store;orders;total_amount
2026-10-01;BCN-014;1;1,60
2026-10-01;MAD-001;2;26,09
2026-10-01;VLC-007;1;-7,50
2026-10-02;BCN-014;1;8,40
2026-10-02;MAD-001;1;2,95
2026-10-02;VLC-007;1;23,48
```

Si tienes Excel configurado en español, también puedes abrirlo directamente: cada valor debe aparecer en su columna. La incidencia DATA-142 también llega a Finanzas: la línea de VLC-007 muestra -7,50.

## 4.5 Archivar

```text
/opsx:archive add-finance-export
```

```bash
git add .
```

```bash
git commit -m "Add daily sales export for Finance"
```

## 4.6 Conclusiones

- El pipeline está completo: landing → bronze → silver → gold → export. Cada pieza tiene su spec, y cada spec está cubierta por tests.
- Un fichero o una tabla que consume otro equipo es un contrato: cambiarlo exige identificar a los consumidores y avisarles.
- Un defecto en una capa (la cantidad negativa en silver) se propaga a todos los consumidores posteriores, incluido Finanzas.

---

## Lista de comprobación final

- [ ] `exports/finance_daily_sales.csv` tiene la cabecera y las 6 líneas esperadas
- [ ] Los importes usan coma decimal y dos decimales
- [ ] `uv run pytest` no devuelve errores
- [ ] `openspec list --specs` muestra 4 capabilities
- [ ] Los cambios están incluidos en un commit

**Siguiente:** [Sesión 5 · Calidad de datos: el primer MODIFIED](05-data-quality.md)

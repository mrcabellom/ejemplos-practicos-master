# Sesión 5 · Calidad de datos: el primer MODIFIED

**Resultado:** reglas de calidad explícitas y una tabla de cuarentena para las filas que no las cumplen. Las ventas negativas desaparecen de gold y del export.

**Conceptos nuevos:** modificar un requisito existente (MODIFIED), un change que afecta a dos capabilities, `openspec show --diff`, los tests que cambian con la spec.

---

## 5.1 La incidencia

En la sesión 3 se detectó la incidencia **DATA-142**: VLC-007 muestra -7,50 € de ventas porque la línea O-1006 tiene cantidad -2. Lucía añade un comentario:

> **Comentario de Lucía:** Además de corregir las cantidades negativas, quiero saber *qué* filas se descartan
> y *por qué*. Hoy silver excluye las filas inválidas sin dejar ningún registro.

Hasta ahora, cada change ha creado una capability nueva. Este change, además, **modifica** una existente: el comportamiento de silver ante las filas inválidas ya está especificado, y va a cambiar.

## 5.2 Antes de proponer: revisar la spec actual

```bash
openspec show order-lines --type spec
```

Localiza el requisito **"Tratamiento de filas inválidas"**: excluye las filas sin `order_id` o que no se pueden tipar. No dice nada de las cantidades negativas ni de registrar las filas excluidas. Es el requisito que se va a modificar.

El nombre neutro elegido en la sesión 2 resulta útil ahora: el tratamiento cambia, pero el nombre sigue siendo válido.

## 5.3 Proponer

```text
/clear
/opsx:propose add-data-quality-quarantine

Incidencia DATA-142: VLC-007 muestra -7,50 € de ventas el 2026-10-01 porque la línea O-1006 tiene cantidad -2.
Además, las filas que silver excluye desaparecen sin dejar rastro.
Queremos:
- Reglas de calidad con código para cada línea de bronze: DQ001 order_id informado, DQ002 order_ts válido,
  DQ003 quantity entero > 0, DQ004 unit_price decimal >= 0, DQ005 status en completed/returned/cancelled.
- Las filas que incumplen alguna regla van a silver.order_lines_quarantine con la lista de reglas incumplidas,
  en lugar de desaparecer.
La capability nueva data-quality debe tener dos requisitos: las reglas y la tabla de cuarentena.
En order-lines, modifica solo el requisito "Tratamiento de filas inválidas".
Fuera de alcance: detener el pipeline por exceso de errores y enviar alertas.
```

El change afecta a dos capabilities:

```
openspec/changes/add-data-quality-quarantine/
├── proposal.md
├── specs/
│   ├── data-quality/spec.md     ← capability NUEVA (ADDED)
│   └── order-lines/spec.md      ← capability EXISTENTE (MODIFIED)
├── design.md
└── tasks.md
```

## 5.4 Revisar el MODIFIED

Abre `openspec/changes/add-data-quality-quarantine/specs/order-lines/spec.md`. Un MODIFIED correcto tiene esta forma:

```markdown
## MODIFIED Requirements

### Requirement: Tratamiento de filas inválidas          ← nombre IDÉNTICO al de la spec actual
Las filas de bronze que incumplan cualquier regla de calidad … SHALL excluirse de
`silver.order_lines` y registrarse en `silver.order_lines_quarantine`.

#### Scenario: Precio no numérico                       ← escenario existente, conservado y ampliado
…
#### Scenario: Línea sin identificador de pedido        ← escenario existente, conservado y ampliado
…
#### Scenario: Cantidad negativa                        ← escenario nuevo
…
```

Reglas de MODIFIED:

1. **El encabezado debe coincidir** exactamente con el de la spec principal. Si no coincide, `archive` no encuentra el requisito.
2. **Se copia el bloque completo** y se edita: al archivar, el MODIFIED sustituye al requisito entero, y lo que no figure en él se pierde.
3. **Se conservan todos los escenarios existentes**, aunque cambie su contenido. OpenSpec no permite archivar un MODIFIED que omite escenarios.

Para ver las diferencias con la spec actual en formato legible:

```bash
openspec show add-data-quality-quarantine --diff
```

Comprueba también:

- [ ] La nueva capability `data-quality` define las cinco reglas con su código.
- [ ] ¿Qué ocurre con una fila que incumple **varias** reglas? ¿Genera una fila en cuarentena o varias? (La solución opta por una sola fila con la lista de reglas.)
- [ ] ¿La cuarentena se duplica si el pipeline se ejecuta dos veces?
- [ ] `tasks.md` incluye una tarea para **actualizar los tests existentes**: el test de silver que contaba 6 líneas del 1 de octubre pasará a contar 5, porque O-1006 irá a cuarentena.

El último punto es importante: cuando cambia una spec, cambian los tests que la verificaban. Si `tasks.md` no lo recoge, `apply` encontrará un test fallido y tendrá que decidir por su cuenta.

```bash
openspec validate add-data-quality-quarantine --strict
```

Compara con la referencia: [`solutions/session-05/`](../solutions/session-05/openspec/changes/add-data-quality-quarantine/).

```bash
git add openspec
```

```bash
git commit -m "Propose add-data-quality-quarantine"
```

## 5.5 Implementar

```text
/clear
/opsx:apply add-data-quality-quarantine
```

```bash
uv run pytest
```

Antes de ejecutar el pipeline, elimina la carpeta `warehouse/` para partir de un estado limpio. Se puede hacer sin riesgo: todo el warehouse se reconstruye a partir de los ficheros de landing.

**Git Bash, macOS y Linux:**

```bash
rm -rf warehouse
```

**PowerShell:**

```powershell
Remove-Item -Recurse -Force warehouse
```

**cmd:**

```bat
rmdir /s /q warehouse
```

> Si no eliminas el warehouse, la cuarentena mostrará las filas inválidas repetidas varias veces. El motivo se estudia en la sesión 6.

```bash
uv run python run_pipeline.py --all
```

```
[bronze] 2026-10-01: 10 rows loaded
[bronze] 2026-10-02: 5 rows loaded
[silver] order_lines: 10 rows
[silver] order_lines_quarantine: 3 rows
[gold]   daily_sales: 5 rows
[export] .../exports/finance_daily_sales.csv
```

Consulta la cuarentena:

```bash
uv run python query.py "SELECT order_id, quantity, unit_price, dq_failed_rules FROM silver.order_lines_quarantine"
```

```
┌──────────┬──────────┬────────────┬─────────────────┐
│ order_id │ quantity │ unit_price │ dq_failed_rules │
│ varchar  │ varchar  │ varchar    │ varchar[]       │
├──────────┼──────────┼────────────┼─────────────────┤
│ NULL     │ 1        │ 1.99       │ ['DQ001']       │
│ O-1006   │ -2       │ 3.75       │ ['DQ003']       │
│ O-1007   │ 1        │ abc        │ ['DQ004']       │
└──────────┴──────────┴────────────┴─────────────────┘
3 rows
```

Y gold:

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
│ 2026-10-02 │ BCN-014  │            1 │          8.40 │
│ 2026-10-02 │ MAD-001  │            1 │          2.95 │
│ 2026-10-02 │ VLC-007  │            1 │         23.48 │
└────────────┴──────────┴──────────────┴───────────────┘
5 rows
```

VLC-007 ya no tiene ventas el 1 de octubre: su única línea era O-1006, que ahora está en cuarentena. La línea de -7,50 también desaparece de `exports/finance_daily_sales.csv`.

## 5.6 Archivar

```text
/opsx:archive add-data-quality-quarantine
```

Salida esperada (resumen):

```
Applying changes to openspec/specs/data-quality/spec.md:
  + 2 added
Applying changes to openspec/specs/order-lines/spec.md:
  ~ 1 modified
```

El requisito "Tratamiento de filas inválidas" de `openspec/specs/order-lines/spec.md` se ha **sustituido** por la nueva versión. Compruébalo:

```bash
git diff openspec/specs
```

```bash
git add .
```

```bash
git commit -m "Add data quality rules and quarantine (DATA-142)"
```

## 5.7 Conclusiones

- MODIFIED sustituye un requisito completo: hay que copiar el bloque entero, conservar el encabezado y todos los escenarios.
- El defecto no estaba en el código, sino en una especificación incompleta. Se ha corregido en la spec, y el código ha seguido a la spec.
- Cuando una spec cambia, sus tests cambian con ella, y `tasks.md` debe recogerlo.

---

## Lista de comprobación final

- [ ] La cuarentena contiene 3 filas (DQ001, DQ003, DQ004)
- [ ] VLC-007 no aparece en gold el 2026-10-01 ni en el export
- [ ] `uv run pytest` no devuelve errores
- [ ] `openspec list --specs` muestra 5 capabilities (nueva: `data-quality`)
- [ ] Los cambios están incluidos en un commit

**Siguiente:** [Sesión 6 · Reprocesar sin duplicar](06-reprocessing.md)

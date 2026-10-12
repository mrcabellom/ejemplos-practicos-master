# Sesión 1 · Primer change: cargar los pedidos en bronze

**Resultado:** la primera pieza del pipeline, escrita por la IA a partir de una spec revisada: los ficheros de pedidos se cargan en `bronze.orders_raw`.

**Conceptos nuevos:** spec y change, los cuatro artefactos de un change, estructura de un requisito, ciclo `propose → revisión → apply → archive`.

---

## 1.1 Cómo funciona OpenSpec

Sin una especificación, una instrucción como *"carga los ficheros de pedidos en la base de datos"* deja muchas decisiones a la IA: si se validan los datos, qué ocurre si falta un fichero, qué columnas se añaden… La IA tomará alguna decisión, y quedará oculta en el código. OpenSpec propone acordar antes esas decisiones por escrito y revisarlas.

OpenSpec trabaja con dos carpetas:

```
openspec/
├── specs/       ← COMPORTAMIENTO ACTUAL DEL SISTEMA (fuente de verdad)
│   └── <capability>/spec.md
└── changes/     ← CAMBIOS PROPUESTOS (en curso)
    ├── <change>/
    │   ├── proposal.md                  motivo y alcance
    │   ├── specs/<capability>/spec.md   requisitos que se añaden o modifican
    │   ├── design.md                    decisiones técnicas
    │   └── tasks.md                     lista de tareas de implementación
    └── archive/                         changes finalizados, con fecha
```

- **Capability:** un comportamiento estable del sistema, con nombre propio. En esta sesión se crea `orders-ingestion`.
- **Change:** una unidad de trabajo que añade o modifica capabilities. En esta sesión, `add-orders-ingestion`.

El ciclo de un change tiene cuatro pasos:

```
/opsx:propose ──► revisión ──► /opsx:apply ──► /opsx:archive
 (la IA redacta    (tú lees y    (la IA escribe     (las specs del change pasan
  los artefactos)   corriges)     el código)          a openspec/specs/)
```

### Estructura de un requisito

La parte central de un change son sus specs, formadas por requisitos con escenarios:

```markdown
### Requirement: Fichero de pedidos ausente
Si no existe el fichero de la fecha solicitada, el pipeline MUST terminar con un error
que indique la ruta esperada, sin cargar ninguna fila.

#### Scenario: Fecha sin fichero
- **WHEN** se ejecuta el pipeline para la fecha 2026-09-30 y no existe `2026-09-30.csv`
- **THEN** la ejecución termina con un error que menciona `2026-09-30.csv`
- **AND** `bronze.orders_raw` no cambia
```

- El requisito describe un comportamiento **observable** y contiene `SHALL` o `MUST` (en inglés, aunque el resto esté en español, para que el validador lo reconozca).
- Cada requisito tiene al menos un escenario (`#### Scenario:`, con **4** almohadillas) con datos concretos. Cada escenario se convertirá en un test.

## 1.2 La petición

> **De:** Lucía (Head of Data)
> **Asunto:** Primer paso del pipeline de pedidos
>
> Las cajas y la tienda online ya dejan cada día un CSV con los pedidos en `data/landing/orders/`. Como primer
> paso, necesito que esos ficheros se carguen tal cual en el warehouse, para poder consultarlos con SQL.
> No hay que limpiar nada todavía: quiero una copia fiel y saber de qué fichero viene cada fila.

## 1.3 Proponer el change

Abre Claude Code en el repositorio de trabajo, limpia el contexto (`/clear`) y escribe:

```text
/opsx:propose add-orders-ingestion

Queremos empezar el pipeline cargando los ficheros diarios de pedidos en bronze.
- Cargar data/landing/orders/<YYYY-MM-DD>.csv en la tabla bronze.orders_raw, con todas las columnas
  como texto y sin corregir ni descartar ninguna fila.
- Añadir a cada fila el nombre del fichero (_source_file) y el instante de carga en UTC (_ingested_at).
- Si no existe el fichero de la fecha solicitada, fallar con un error que indique la ruta.
- Crear run_pipeline.py con --date y --all.
La spec debe tener solo dos requisitos: la carga del fichero y el fichero ausente.
Usa en los escenarios los datos reales de 2026-10-01.csv. Fuera de alcance: validar o limpiar los datos
y qué ocurre al cargar dos veces el mismo fichero.
```

Claude creará `openspec/changes/add-orders-ingestion/` con los cuatro artefactos y se **detendrá**: `propose` nunca escribe código.

## 1.4 Revisar

La revisión es la parte más importante del método: es el momento de corregir decisiones, antes de que existan en el código. Abre los ficheros del change o consúltalos desde el terminal:

```bash
openspec show add-orders-ingestion
```

Comprueba:

- [ ] La spec de `orders-ingestion` tiene un `## Purpose` (es una capability nueva).
- [ ] Hay **solo dos** requisitos: la carga y el fichero ausente. Las columnas, los tipos y el origen de cada fila son detalles del requisito de carga, no requisitos aparte.
- [ ] La IA no ha añadido requisitos que no se pidieron. Es frecuente que proponga, por ejemplo, qué ocurre al cargar dos veces el mismo fichero. Aunque parezca útil, elimínalo: no se ha pedido y se abordará en la sesión 6. Revisar una spec también es controlar su alcance.
- [ ] Los escenarios usan datos reales: 10 filas de `2026-10-01.csv`, el precio `abc` de O-1007, la fecha 2026-09-30 sin fichero.
- [ ] La spec no menciona funciones ni librerías de Python: describe lo que se observa desde fuera (tablas, columnas, errores).
- [ ] Cada tarea de `tasks.md` indica cómo se verifica.

Si algo no es correcto, no edites los ficheros a mano: pídeselo a Claude con `/opsx:update`. Por ejemplo:

```text
/opsx:update Añade un escenario que compruebe que el precio abc de O-1007 se conserva sin modificar en bronze.
```

```text
/opsx:update Elimina el requisito sobre cargar dos veces el mismo fichero: está fuera del alcance de este change.
```

Valida el formato:

```bash
openspec validate add-orders-ingestion --strict
```

Compara con la referencia: [`solutions/session-01/`](../solutions/session-01/openspec/changes/add-orders-ingestion/). La IA generará textos distintos; compara la estructura y las decisiones, no la redacción.

Guarda la propuesta revisada:

```bash
git add openspec
```

```bash
git commit -m "Propose add-orders-ingestion"
```

## 1.5 Implementar

Limpia el contexto (`/clear`): la planificación ya está en los ficheros, no en la conversación. Así la IA implementa a partir de **los artefactos acordados** y no de lo que recuerda del chat.

```text
/opsx:apply add-orders-ingestion
```

Durante la implementación, Claude lee los artefactos, crea el código y los tests, ejecuta `uv run pytest` después de cada grupo de tareas y marca cada tarea con `[x]` en `tasks.md`.

Cuando termine, comprueba el resultado por tu cuenta:

```bash
uv run pytest
```

```bash
uv run python run_pipeline.py --all
```

```
[bronze] 2026-10-01: 10 rows loaded
[bronze] 2026-10-02: 5 rows loaded
```

```bash
uv run python query.py "SELECT order_id, store_id, quantity, unit_price, status, _source_file FROM bronze.orders_raw LIMIT 10"
```

```
┌──────────┬──────────┬──────────┬────────────┬───────────┬────────────────┐
│ order_id │ store_id │ quantity │ unit_price │ status    │ _source_file   │
│ varchar  │ varchar  │ varchar  │ varchar    │ varchar   │ varchar        │
├──────────┼──────────┼──────────┼────────────┼───────────┼────────────────┤
│ O-1001   │ MAD-001  │ 6        │ 0.95       │ completed │ 2026-10-01.csv │
│ O-1001   │ MAD-001  │ 1        │ 8.49       │ completed │ 2026-10-01.csv │
│ O-1002   │ MAD-001  │ 1        │ 11.90      │ completed │ 2026-10-01.csv │
│ O-1003   │ BCN-014  │ 2        │ 0.80       │ completed │ 2026-10-01.csv │
│ O-1003   │ BCN-014  │ 2        │ 0.80       │ completed │ 2026-10-01.csv │
│ O-1004   │ BCN-014  │ 3        │ 6.50       │ returned  │ 2026-10-01.csv │
│ O-1005   │ VLC-007  │ 2        │ 2.70       │ cancelled │ 2026-10-01.csv │
│ NULL     │ VLC-007  │ 1        │ 1.99       │ completed │ 2026-10-01.csv │
│ O-1006   │ VLC-007  │ -2       │ 3.75       │ completed │ 2026-10-01.csv │
│ O-1007   │ MAD-001  │ 1        │ abc        │ completed │ 2026-10-01.csv │
└──────────┴──────────┴──────────┴────────────┴───────────┴────────────────┘
10 rows
```

Bronze contiene el fichero tal como llegó: todo como texto (`varchar`), con la línea duplicada, la cantidad negativa y el precio `abc`. Es exactamente lo que pedía la spec.

Revisa también el código que ha escrito la IA (`mercaluz/`, `run_pipeline.py` y `tests/`). Comprueba que cada escenario de la spec tiene su test.

## 1.6 Archivar

```text
/opsx:archive add-orders-ingestion
```

Es posible que Claude pregunte cómo proceder, porque el delta crea una capability que todavía no existe en `openspec/specs/`. Elige siempre **Sync now**: crea la spec principal y después archiva el change. La opción *Archive without syncing* archiva el change sin crear la spec principal, de modo que `openspec/specs/` se queda vacío y las sesiones siguientes no encuentran los requisitos que tienen que modificar.

Al archivar, OpenSpec:

1. Crea `openspec/specs/orders-ingestion/spec.md` con el `## Purpose` y los requisitos del change.
2. Mueve el change a `openspec/changes/archive/<fecha>-add-orders-ingestion/`.

Desde este momento, `openspec/specs/` describe cómo se comporta el sistema:

```bash
openspec list --specs
```

```bash
git add .
```

```bash
git commit -m "Add orders ingestion into bronze"
```

## 1.7 Conclusiones

- La IA ha escrito todo el código, pero las decisiones (texto sin validar, columnas de origen, error ante un fichero ausente) se han tomado y revisado antes, en la spec.
- Los escenarios con datos concretos se han convertido en tests: son la prueba de que el código cumple lo acordado.
- ¿Qué ocurre si se carga dos veces el mismo día? La spec no lo dice. Por la regla de `config.yaml` "implementa solo lo que piden las specs", la IA no ha añadido ningún comportamiento para ese caso. Se retomará en la sesión 6.

---

## Lista de comprobación final

- [ ] `uv run python run_pipeline.py --all` carga 10 y 5 filas
- [ ] `query.py` muestra las líneas de bronze con su `_source_file`
- [ ] `uv run pytest` no devuelve errores
- [ ] `openspec list --specs` muestra la capability `orders-ingestion`
- [ ] Los cambios están incluidos en un commit

**Siguiente:** [Sesión 2 · Silver: líneas de pedido depuradas](02-silver-order-lines.md)

# Sesión 6 · Reprocesar sin duplicar

**Resultado:** la ingesta pasa a ser idempotente: reprocesar un día sustituye sus datos en lugar de duplicarlos. Es el primer change en el que `design.md` recoge decisiones técnicas con alternativas.

**Conceptos nuevos:** comportamiento no especificado, añadir un requisito a una capability existente, `design.md` con alternativas, riesgos y plan de migración.

---

## 6.1 La incidencia

> **INC-0917 · Líneas obsoletas en el informe de ventas**
>
> **Notificada por:** Operaciones de datos
>
> El sistema de cajas reenvió **corregido** el fichero del 2 de octubre: el pedido O-1011 no correspondía a
> una devolución real y se eliminó. Tras reprocesar el día, O-1011 **sigue apareciendo** en los informes.
> Además, bronze contiene más filas de las que tiene el fichero.

En la sesión 5 ya apareció una pista: sin borrar el warehouse, la cuarentena mostraba las filas repetidas. Reprodúcelo desde un warehouse limpio. Elimina la carpeta `warehouse/` como en la sesión 5 (`rm -rf warehouse`, `Remove-Item -Recurse -Force warehouse` o `rmdir /s /q warehouse`, según el terminal) y carga dos veces el mismo día:

```bash
uv run python run_pipeline.py --date 2026-10-02
```

```bash
uv run python run_pipeline.py --date 2026-10-02
```

```bash
uv run python query.py "SELECT _source_file, count(*) AS rows FROM bronze.orders_raw GROUP BY ALL"
```

```
┌────────────────┬────────┐
│ _source_file   │   rows │
│ varchar        │ bigint │
├────────────────┼────────┤
│ 2026-10-02.csv │     10 │
└────────────────┴────────┘
1 row
```

El fichero tiene 5 filas, pero bronze contiene 10: cada ejecución añade una copia. Silver lo disimula porque elimina las líneas repetidas, pero si el fichero corregido ya no incluye O-1011, la versión antigua sigue en bronze y llega a silver.

¿Es un error de programación? La spec de `orders-ingestion` (sesión 1) no decía qué hacer al cargar dos veces el mismo fichero, y la IA, siguiendo la regla "implementa solo lo que piden las specs", no añadió nada. Es un **comportamiento no especificado**: el sistema hace algo, pero nadie lo ha decidido.

### Conceptos previos

| Concepto | Definición | Aplicación a esta incidencia |
|---|---|---|
| **Idempotencia** | Un proceso es idempotente si produce el mismo resultado tanto si se ejecuta una vez como varias con los mismos datos | Actualmente no lo es: cada ejecución añade otra copia a bronze |
| **Transacción** | Grupo de operaciones SQL que se aplican **todas o ninguna**. Si algo falla a mitad, la base de datos vuelve al estado anterior (*rollback*) | Si se eliminan las filas anteriores y falla la carga de las nuevas, el día no debe quedar sin datos |
| **DELETE + INSERT** | Eliminar las filas de un fichero y volver a insertarlas a partir del fichero nuevo | Sustituir el día completo por la versión corregida |
| **MERGE** | Sentencia SQL que, fila a fila, actualiza las existentes e inserta las nuevas. Necesita una **clave** para identificar cada fila | No es aplicable: bronze no tiene clave. Puede contener filas idénticas (las dos líneas de O-1003) que ninguna columna permite distinguir |

## 6.2 Proponer

```text
/clear
/opsx:propose make-orders-ingestion-idempotent

Incidencia INC-0917: al reprocesar una fecha, bronze añade de nuevo todas las filas del fichero. Bronze duplica
datos y, si el fichero llega corregido, las líneas eliminadas siguen llegando a silver y gold.
Queremos que reprocesar una fecha SUSTITUYA las filas de ese fichero en bronze, de forma atómica:
si la carga falla, bronze conserva la versión anterior.
Añade un único requisito a orders-ingestion: el reprocesado de una fecha ya cargada. En design.md compara al menos DELETE + INSERT por fichero,
MERGE y una columna de versión de carga.
Usa en los escenarios los ficheros reales: doble carga de 2026-10-01 y un 2026-10-02 corregido sin O-1011.
```

A diferencia de la sesión 5, aquí no se modifica ningún requisito: se **añade** uno nuevo ("Reprocesado de una fecha ya cargada") a una capability que ya existe. Por eso el delta de `orders-ingestion` tiene una sección `## ADDED Requirements` y no lleva `## Purpose`.

## 6.3 Revisar el design

En Data Engineering, `design.md` es el lugar donde se previenen las incidencias futuras. Comprueba que responde a estas preguntas:

| Pregunta | Respuesta en la solución de referencia |
|---|---|
| ¿Cuál es la **unidad** que se sustituye? | El fichero (`_source_file`), que equivale a una fecha de negocio |
| ¿Por qué no MERGE? | Bronze no tiene clave por fila, y las filas repetidas (O-1003) forman parte de lo que se recibió |
| ¿Qué ocurre si la carga falla a mitad? | DELETE + INSERT en **una transacción**: se aplica todo o nada |
| ¿Qué se hace con los duplicados que ya existen? | Desaparecen al reprocesar cada fecha; en local basta con regenerar el warehouse |
| ¿Cómo se revierte el cambio (rollback)? | Desplegando la versión anterior; bronze sigue siendo válido |

Comprueba también la spec:

- [ ] Hay un escenario para la doble carga (10 filas, no 20), otro para el fichero corregido (4 filas, sin O-1011 en silver) y otro para el fallo a mitad de la carga.
- [ ] `design.md` indica que el nombre del fichero se pasa como **parámetro** SQL, según la regla de `config.yaml` contra la inyección SQL (sesión 0).

> **Opcional: entorno de producción.** Mercaluz ejecuta el pipeline en Databricks, orquestado con Airflow (un planificador que lo lanza cada día). En ese entorno habría que evitar además dos ejecuciones simultáneas del mismo día; en Airflow se consigue limitando a una las ejecuciones activas. No es necesario para el taller.

```bash
openspec validate make-orders-ingestion-idempotent --strict
```

Compara con la referencia: [`solutions/session-06/`](../solutions/session-06/openspec/changes/make-orders-ingestion-idempotent/).

```bash
git add openspec
```

```bash
git commit -m "Propose make-orders-ingestion-idempotent"
```

## 6.4 Implementar

```text
/clear
/opsx:apply make-orders-ingestion-idempotent
```

Revisa en el diff del módulo de ingesta cómo se construye el `DELETE`. El nombre del fichero procede de un sistema externo, por lo que debe pasarse como **parámetro** (`WHERE _source_file = ?`) y no insertarse en la consulta mediante un f-string. Si la IA no ha aplicado la regla, pídele que lo corrija.

```bash
uv run pytest
```

Repite la prueba de la incidencia. Esta vez no es necesario eliminar el warehouse: la primera carga sustituye todas las copias anteriores del fichero.

```bash
uv run python run_pipeline.py --date 2026-10-02
```

```bash
uv run python run_pipeline.py --date 2026-10-02
```

```bash
uv run python query.py "SELECT _source_file, count(*) AS rows FROM bronze.orders_raw GROUP BY ALL"
```

```
┌────────────────┬────────┐
│ _source_file   │   rows │
│ varchar        │ bigint │
├────────────────┼────────┤
│ 2026-10-02.csv │      5 │
└────────────────┴────────┘
1 row
```

Las dos ejecuciones dejan 5 filas: el pipeline ya se puede relanzar sin riesgo. Los escenarios del fichero corregido y del fallo a mitad de carga están cubiertos por los tests, sin necesidad de modificar los ficheros de landing.

## 6.5 Archivar

```text
/opsx:archive make-orders-ingestion-idempotent
```

```
Applying changes to openspec/specs/orders-ingestion/spec.md:
  + 1 added
```

```bash
git add .
```

```bash
git commit -m "Make orders ingestion idempotent (INC-0917)"
```

## 6.6 Conclusiones

- Lo que la spec no dice, el sistema lo hace de alguna forma que nadie ha decidido. En datos, "qué ocurre al reprocesar" debe especificarse siempre.
- `design.md` recoge el *cómo* y, sobre todo, el *por qué*: las alternativas descartadas evitan repetir la misma discusión en el futuro.
- Los escenarios difíciles de reproducir a mano (un fallo a mitad de carga) se verifican con tests.

## 6.7 Fin del núcleo del taller

El pipeline está construido y especificado: cinco capabilities, seis changes archivados y un test por cada escenario. A partir de aquí hay dos sesiones avanzadas, independientes entre sí:

- [Sesión 7 · Cambio incompatible: métricas sin IVA para Finanzas](07-advanced-net-revenue.md)
- [Sesión 8 · Explorar antes de proponer: datos personales y RGPD](08-advanced-gdpr.md)

Para hacerlas puedes continuar con tu repositorio o partir del código de referencia de [`solutions/advanced-start/`](../solutions/advanced-start/) (consulta [Problemas frecuentes](../appendix/troubleshooting.md#empezar-las-sesiones-avanzadas-desde-el-código-de-referencia)).

---

## Lista de comprobación final

- [ ] Cargar dos veces el mismo día deja el mismo número de filas en bronze
- [ ] El `DELETE` del módulo de ingesta usa un parámetro para el nombre del fichero
- [ ] `uv run pytest` no devuelve errores
- [ ] `orders-ingestion` tiene 3 requisitos (`openspec show orders-ingestion --type spec`)
- [ ] Los cambios están incluidos en un commit

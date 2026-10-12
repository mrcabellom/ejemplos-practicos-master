# Sesión 7 (avanzada) · Cambio incompatible: métricas sin IVA para Finanzas

**Resultado:** un change que modifica de forma **controlada** el contrato de `gold.daily_sales` y del export de Finanzas: marcado como BREAKING, con un requisito eliminado (REMOVED), una vista de compatibilidad y un plan de migración para los consumidores.

**Conceptos nuevos:** **BREAKING**, REMOVED (Reason y Migration), RENAMED, versionado de contratos de datos, el error de "MODIFIED que omite escenarios" y la revisión por parte de negocio.

**Punto de partida:** el repositorio al final de la sesión 6, o el código de referencia de [`solutions/advanced-start/`](../solutions/advanced-start/).

---

## 7.1 La petición

> **De:** Marta (Control de Gestión)
> **Para:** Data Platform
> **Asunto:** Cierre de septiembre: diferencia de 38.000 €
>
> Las ventas de Power BI no cuadran con contabilidad. Tras dos días de análisis, he identificado los motivos:
>
> 1. `total_amount` incluye **IVA**, mientras que contabilidad trabaja con importes **sin IVA**.
> 2. Las **devoluciones** no se restan.
>
> Necesito las ventas brutas, las devoluciones y las ventas netas sin IVA por día y tienda, también en el fichero CSV que recibo.
> Tipos de IVA: alimentación básica 4 %, alimentación 10 %, bebidas y droguería 21 %.

El equipo de BI añade: *"12 informes utilizan `total_amount`. Si la columna se elimina sin un periodo de transición, los cuadros de mando dejarán de funcionar."*

La decisión de la sesión 3 ("las devoluciones no cuentan") era razonable entonces, pero el negocio ha cambiado de criterio. Por eso figuraba como requisito explícito: ahora se puede localizar y eliminar.

## 7.2 Qué diferencia a este change

| | Sesiones 1 a 6 | Sesión 7 |
|---|---|---|
| Esquema de gold y del export | Se crea o no cambia | **Cambia**: desaparece `total_amount` |
| Consumidores afectados | Reciben datos nuevos o corregidos | **Dejan de funcionar** si no se adaptan |
| Requisitos | ADDED / MODIFIED | ADDED / MODIFIED / **REMOVED** |
| Aprobación | Data Platform | Data Platform, **Finanzas y BI** |

En la sesión 4 se vio que el formato del export es un contrato con Finanzas. Lo mismo ocurre con gold: los informes de Power BI se diseñaron a partir de la existencia de `total_amount` y de su significado. OpenSpec ofrece un mecanismo explícito para gestionar estos cambios: **BREAKING** en la proposal, **REMOVED** con instrucciones de migración en la spec y un **plan de migración** en el design.

## 7.3 Proponer

```text
/clear
/opsx:propose split-gross-net-revenue

Petición de Finanzas (Marta): las ventas de gold no cuadran con contabilidad porque total_amount
lleva IVA y no descuenta devoluciones.

- En gold.daily_sales, sustituir total_amount por gross_revenue (con IVA, completed),
  returns_amount (con IVA, returned, en positivo) y net_revenue (completed - returned, SIN IVA).
- IVA por categoría: alimentacion_basica 4 %, alimentacion 10 %, bebidas 21 %, drogueria 21 %.
  Si llega una categoría sin tipo, fallar sin tocar gold (no aplicar un IVA por defecto).
- Eliminar el requisito actual "Devoluciones excluidas de las métricas".
- 12 informes de Power BI usan total_amount: mantener una vista de compatibilidad
  gold.daily_sales_v1 con el esquema antiguo hasta el 2026-12-31.
- El CSV de Finanzas pasa a: date;store;orders;gross_sales;returns;net_sales_ex_vat

Marca como BREAKING lo que rompa consumidores. Usa en los escenarios cifras reales calculadas
con los ficheros de data/landing/orders (MAD-001 y BCN-014 el 2026-10-01).
```

## 7.4 Revisión: comprobar las cifras

Como en la sesión 3, hay que comprobar los cálculos **antes** de implementar.

**MAD-001, 2026-10-01:**

| Línea | Importe con IVA | IVA | Sin IVA |
|---|---|---|---|
| 6 × 0,95 leche (alimentacion_basica) | 5,70 | 4 % | 5,4808 |
| 1 × 8,49 aceite (alimentacion) | 8,49 | 10 % | 7,7182 |
| 1 × 11,90 detergente (drogueria) | 11,90 | 21 % | 9,8347 |
| **Total** | **gross 26,09** | | **net 23,03** |

**BCN-014, 2026-10-01:**

| Línea | Estado | Importe | IVA | Sin IVA (con signo) |
|---|---|---|---|---|
| 2 × 0,80 pan | completed | 1,60 | 4 % | +1,5385 |
| 3 × 6,50 vino (O-1004) | returned | 19,50 | 21 % | −16,1157 |
| | | **gross 1,60 · returns 19,50** | | **net −14,58** |

Cuestiones para revisar con Marta:

- [ ] ¿Se redondea por línea o sobre el total? (Una diferencia de céntimos se convierte en euros a lo largo de un año.) → Sobre el total.
- [ ] La devolución de O-1004, ¿se imputa al día de la compra o al de la devolución? El fichero no incluye la fecha de devolución → al día de la compra, documentado como limitación en el design.
- [ ] ¿Es aceptable un `net_revenue` negativo? → Sí, es correcto desde el punto de vista contable.
- [ ] Una tienda que en un día solo tiene devoluciones, ¿debe tener fila? → Sí, con `orders_count = 0`.

> **Revisión por negocio:** a Marta se le envía la spec, no el código. `specs/daily-sales/spec.md` está en español y contiene sus tiendas y sus cifras, de modo que puede aprobarla sin conocimientos de SQL.

## 7.5 Error frecuente: un MODIFIED que omite escenarios

Es muy probable que la IA genere el MODIFIED de "Ventas diarias por tienda" con escenarios **nuevos** (`Tienda sin devoluciones`, `Tienda con devolución`…) y **sin** el escenario original `Ventas de una tienda en un día`. En ese caso, la validación falla:

```
✗ [ERROR] daily-sales/spec.md: MODIFIED "Ventas diarias por tienda" omits scenario(s)
the current spec still has: "Ventas de una tienda en un día". … Copy the omitted scenarios into the
MODIFIED block (a MODIFIED requirement replaces the whole block, so archive refuses to drop them).
```

Es la protección que se mencionó en la sesión 5: un MODIFIED **sustituye** el bloque completo, y el validador impide que se pierdan escenarios de forma inadvertida. Hay dos opciones:

1. **Conservar el nombre del escenario y actualizar su contenido** (es lo que hace la solución): `Ventas de una tienda en un día` pasa a comprobar `gross_revenue`, `returns_amount` y `net_revenue`.
2. Si el escenario realmente sobra, valorar si el requisito completo debería tratarse como REMOVED + ADDED.

Para corregirlo con la IA:

```text
/opsx:update openspec validate falla porque el MODIFIED de "Ventas diarias por tienda" omite
el escenario "Ventas de una tienda en un día". Consérvalo con ese nombre y actualiza su contenido
a las nuevas métricas.
```

## 7.6 REMOVED: eliminar con instrucciones

```markdown
## REMOVED Requirements

### Requirement: Devoluciones excluidas de las métricas
**Reason**: Finanzas necesita las devoluciones para cuadrar con contabilidad; ignorarlas sobrestima las ventas.
**Migration**: Usar `returns_amount` para ver las devoluciones y `net_revenue` para las ventas netas. Quien necesite
el comportamiento anterior puede usar `gross_revenue` o la vista `gold.daily_sales_v1`.
```

`Reason` y `Migration` son **obligatorios**. En Data Engineering, *Migration* describe exactamente lo que debe hacer cada consumidor.

## 7.7 RENAMED (referencia)

Este change no renombra ningún requisito. Para cambiar el nombre de un requisito sin modificar su contenido, el formato es:

```markdown
## RENAMED Requirements

- FROM: `### Requirement: Ventas diarias por tienda`
- TO: `### Requirement: Métricas diarias de ventas por tienda`
```

Si además se modifica el contenido, debe añadirse un MODIFIED que utilice el nombre **nuevo**.

## 7.8 Versionado del contrato de datos

Una **vista** (`VIEW`) es una consulta SQL guardada con un nombre. Se consulta igual que una tabla, pero no almacena datos propios: cada lectura ejecuta la consulta sobre las tablas reales. Por eso permite ofrecer el esquema anterior sin duplicar datos.

El design de la solución opta por una **vista de compatibilidad con fecha de retirada**:

```
gold.daily_sales        ← esquema nuevo (gross_revenue, returns_amount, net_revenue)
gold.daily_sales_v1     ← vista con el esquema anterior, total_amount = gross_revenue, hasta 2026-12-31
```

Además, la convierte en un **requisito** (no solo en una decisión técnica): mientras exista, los consumidores dependen de ella. Su retirada será otro change (`remove-daily-sales-v1-view`), recogido en la sección `## Workflow follow-up` de `tasks.md`.

| Estrategia | Ventajas | Inconvenientes |
|---|---|---|
| Eliminar la columna directamente | Sencillez | Los cuadros de mando dejan de funcionar |
| Mantener `total_amount` en la tabla indefinidamente | Ningún consumidor se ve afectado | Deuda técnica permanente y semántica ambigua |
| **Vista `_v1` con fecha de retirada** | Migración ordenada y tabla sin columnas obsoletas | Requiere seguimiento |
| Tabla nueva `daily_revenue` | Riesgo nulo | Dos fuentes de verdad durante meses |

Compara con la referencia: [`solutions/session-07/`](../solutions/session-07/openspec/changes/split-gross-net-revenue/).

## 7.9 Validar, implementar y archivar

```bash
openspec validate split-gross-net-revenue --strict
```

```bash
git add openspec
```

```bash
git commit -m "Propose split-gross-net-revenue"
```

```text
/clear
/opsx:apply split-gross-net-revenue
```

```bash
uv run pytest
```

```bash
uv run python run_pipeline.py --all
```

```bash
uv run python query.py gold.daily_sales
```

Comprueba que (2026-10-01, MAD-001) tiene `gross_revenue` 26,09 y `net_revenue` 23,03, y que (2026-10-01, BCN-014) tiene `net_revenue` -14,58. Comprueba también la vista de compatibilidad:

```bash
uv run python query.py gold.daily_sales_v1
```

```text
/opsx:archive split-gross-net-revenue
```

```
Applying changes to openspec/specs/daily-sales/spec.md:
  + 3 added
  ~ 1 modified
  - 1 removed
Applying changes to openspec/specs/finance-export/spec.md:
  ~ 1 modified
```

```bash
git add .
```

```bash
git commit -m "BREAKING: split gold and Finance export into gross, returns and net ex-VAT revenue"
```

---

## Lista de comprobación final

- [ ] La proposal marca como **BREAKING** el cambio de gold y del export
- [ ] Has comprobado manualmente `net_revenue = 23,03` y `-14,58`
- [ ] El requisito "Devoluciones excluidas de las métricas" ya no figura en `openspec/specs/daily-sales/spec.md`
- [ ] Existe la vista `gold.daily_sales_v1`
- [ ] Puedes explicar por qué falla la validación cuando un MODIFIED omite un escenario y cómo se corrige

**Siguiente:** [Sesión 8 (avanzada) · Datos personales y RGPD](08-advanced-gdpr.md)

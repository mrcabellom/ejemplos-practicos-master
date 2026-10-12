# Anexo · OpenSpec en equipo

Este anexo es material de consulta, fuera del recorrido principal del taller. Describe cómo preparar un repositorio como el de Mercaluz para que trabajen en él varias personas y varios agentes de IA: reglas basadas en la experiencia, un schema propio con **contrato de datos**, validación en CI, revisiones por consumidor y un procedimiento para changes en paralelo. Los ficheros de ejemplo están en [`solutions/appendix-teams/`](../solutions/appendix-teams/).

---

## Retrospectiva: lecciones del taller

| Sesión | Situación | Regla para `config.yaml` |
|---|---|---|
| 2 y 5 | El nombre neutro "Tratamiento de filas inválidas" permitió modificar el requisito sin renombrarlo | *Nombres neutros que sigan siendo válidos tras los cambios* (ya incluida en la sesión 0) |
| 5 | El test de silver que contaba 6 líneas tuvo que actualizarse | *Si un escenario cambia una cifra que ya tiene test, incluir una tarea para actualizarlo* |
| 6 | Cargar dos veces el mismo fichero duplicaba bronze, y ninguna spec decía qué debía ocurrir | *Especificar el comportamiento ante reprocesados* |
| 7 | Un MODIFIED sin uno de los escenarios existentes no superó la validación | *En MODIFIED, conservar el nombre de todos los escenarios* |
| 7 | Los cuadros de mando de BI estuvieron a punto de dejar de funcionar | *Todo cambio de esquema en gold o en exports requiere una vista `_vN` con fecha de retirada* (en `context`) |
| 8 | La cuarentena contenía datos personales sin que nadie lo supiera | *Si el change afecta a datos de clientes, indicar si debe revisarlo la DPO* |

El `config.yaml` resultante está en [`solutions/appendix-teams/openspec/config.yaml`](../solutions/appendix-teams/openspec/config.yaml). **`config.yaml` debe tratarse como código**: se modifica mediante pull request y cada regla tiene una justificación.

> **Advertencia:** `config.yaml` no debe convertirse en un manual de 300 líneas, porque se incluye en **todas** las instrucciones y consume contexto. Si una regla solo afecta a un tipo de artefacto, debe ir en `rules.<artefacto>` y no en `context`.

## Schema propio: artefacto de contrato de datos

El schema predeterminado (`spec-driven`) tiene 4 artefactos. Para un equipo de datos falta uno: el **contrato de datos** de las tablas que cambian (grano, clave, columnas, SLA, consumidores y versionado). En este apartado se añade.

> Los comandos `openspec schema` están marcados como **experimentales** en la versión 1.14.

**1. Copia el schema predeterminado al proyecto:**

```bash
openspec schema fork spec-driven mercaluz-data
```

El comando crea `openspec/schemas/mercaluz-data/` con `schema.yaml` y `templates/`.

**2. Añade el artefacto en `schema.yaml`**, antes de `tasks`, y haz que `tasks` dependa de él:

```yaml
  - id: data-contract
    generates: data-contract.md
    description: Data contract for the tables or files that change
    template: data-contract.md
    instruction: |
      Document the data contract of every table or file whose schema or semantics change.
      For each one: full name, grain (what one row represents), columns with type,
      nullability and description, unique key, freshness SLA, known consumers and
      versioning policy (what is BREAKING and how it is communicated).
      If the change does not alter any table or file, write "No contract changes" and explain why.
    requires:
      - specs

  - id: tasks
    # ...
    requires:
      - specs
      - design
      - data-contract
```

**3. Crea la plantilla** `templates/data-contract.md` (consulta [la solución](../solutions/appendix-teams/openspec/schemas/mercaluz-data/templates/data-contract.md)).

**4. Valida el schema y actívalo** en `config.yaml` con `schema: mercaluz-data`:

```bash
openspec schema validate mercaluz-data
```

**5. Compruébalo** con un change nuevo:

```bash
openspec new change try-schema
```

```bash
openspec status --change try-schema
```

```
Schema: mercaluz-data
[ ] proposal
[-] specs (blocked by: proposal)
[-] design (blocked by: proposal)
[-] data-contract (blocked by: specs)
[-] tasks (blocked by: specs, design, data-contract)
```

A partir de este momento, `/opsx:propose` también genera `data-contract.md`. Los changes anteriores conservan su schema (registrado en su `.openspec.yaml`).

> **Ejercicio:** elimina `try-schema` y repite la sesión 7 (`split-gross-net-revenue`) con el nuevo schema. El `data-contract.md` debería incluir la tabla de columnas de `gold.daily_sales`, con `total_amount` marcada como *eliminada*, y la vista `_v1`. Es precisamente el documento que necesitaba el equipo de BI.

## Validación en CI (opcional)

> **Opcional.** Este apartado y el siguiente describen cómo lo organizaría un equipo que trabaja en GitHub. Basta con leerlos y entender los ficheros: no es necesario tener cuenta de GitHub ni ejecutar nada.

Términos utilizados:

- **Pull request (PR):** solicitud para incorporar los cambios de una rama a la rama principal. Otras personas la revisan y la aprueban antes de fusionarla.
- **CI (integración continua):** comprobaciones automáticas que se ejecutan en cada pull request (validación de specs, tests). Si alguna falla, el pull request no puede fusionarse.
- **GitHub Actions:** el sistema de CI de GitHub. Las comprobaciones se definen en ficheros YAML dentro de `.github/workflows/`.

Extracto de [`solutions/appendix-teams/.github/workflows/openspec.yml`](../solutions/appendix-teams/.github/workflows/openspec.yml):

```yaml
- name: Install OpenSpec (pinned version)
  run: npm install -g @fission-ai/openspec@1.14.1

- name: Validate specs and active changes
  run: openspec validate --all --strict --no-interactive

- name: Archived changes have all tasks completed
  run: openspec validate --archived --no-interactive
```

| Comprobación | Qué detecta |
|---|---|
| `validate --all --strict` | Specs mal formadas, escenarios con 3 `#`, MODIFIED que omiten escenarios, `Purpose` vacío |
| `validate --archived` | Changes archivados con tareas pendientes |
| `uv run pytest` | Que el código cumple los escenarios (siempre que cada escenario tenga su test) |

> **Fija la versión** del CLI en CI y recomienda la misma versión en local. Las versiones nuevas pueden endurecer la validación, como ocurrió con la comprobación de escenarios omitidos.

## Revisión: quién aprueba cada cambio (opcional)

[`CODEOWNERS`](../solutions/appendix-teams/.github/CODEOWNERS) es un fichero de GitHub que indica quién debe revisar cada carpeta: cuando un pull request modifica una de ellas, GitHub solicita automáticamente la aprobación de las personas asignadas. En este caso asigna revisores **por capability**, es decir, por contrato:

```
/openspec/specs/daily-sales/       @mercaluz/data-platform @mercaluz/bi @mercaluz/finanzas
/openspec/specs/finance-export/    @mercaluz/data-platform @mercaluz/finanzas
/openspec/specs/pii-protection/    @mercaluz/data-platform @mercaluz/dpo
```

Hay que tener en cuenta que los deltas se encuentran en `openspec/changes/<change>/specs/<capability>/` hasta que se archivan. Para que Finanzas revise **la propuesta**, y no solo el resultado final, existen dos flujos:

| Flujo | Funcionamiento | Cuándo usarlo |
|---|---|---|
| **Dos pull requests** | PR 1: solo `openspec/changes/<change>/` (propuesta). PR 2: código y archivo | Changes BREAKING o que requieren revisión de negocio o legal |
| **Un pull request** | Propuesta, código y archivo juntos; la plantilla de pull request obliga a revisar los artefactos | Changes internos del equipo |

Plantilla de pull request: [`solutions/appendix-teams/.github/pull_request_template.md`](../solutions/appendix-teams/.github/pull_request_template.md).

## Changes en paralelo

Javier trabaja en `add-dq-rule-store-format` (MODIFIED de "Reglas de calidad…") y tú en `add-dq-rule-sku-format` (MODIFIED del **mismo** requisito). Ambos parten de la misma versión de la spec.

```bash
openspec list
```

```
Changes:
  add-dq-rule-store-format     3/5 tasks
  add-dq-rule-sku-format       1/4 tasks
```

Qué ocurre:

1. Javier archiva primero, y la spec principal pasa a incluir DQ006.
2. Tu MODIFIED se redactó **sin** DQ006. Si lo archivas tal como está, **eliminarás la regla de Javier**, porque el MODIFIED sustituye el bloque completo.
3. La protección es parcial: si Javier añadió un **escenario**, tu archivo falla ("omits scenario(s)"). Si solo modificó el texto, **no se produce ningún error**. Se ha comprobado con OpenSpec 1.14.1: ambos changes se validan y se archivan, y la spec final contiene DQ007 pero **ha perdido DQ006**.

Práctica recomendada para el equipo:

- Antes de archivar, **actualiza el change** con respecto a la spec vigente:

```text
/opsx:update Las specs principales han cambiado desde que se creó este change (se archivó
add-dq-rule-store-format). Reconcilia el MODIFIED de "Reglas de calidad de líneas de pedido"
para que incluya DQ006 además de nuestra DQ007.
```

- Revisa siempre `openspec show <change> --diff` inmediatamente antes de archivar.
- Si dos changes modifican con frecuencia el mismo requisito, es posible que ese requisito agrupe demasiados comportamientos y convenga dividirlo.

## Perfil ampliado: más control paso a paso

Activa el perfil ampliado siguiendo los pasos de la [sesión 0, apartado 0.7](../sessions/00-installation-and-setup.md#cómo-activar-el-perfil-ampliado): `openspec config profile`, opción `Change workflows only`, selección de los workflows adicionales y `openspec update`. Comprueba después que los comandos nuevos aparecen al escribir `/opsx` en Claude Code.

| Comando | Uso habitual en el equipo |
|---|---|
| `/opsx:new <nombre>` + `/opsx:continue` | Changes delicados (RGPD, BREAKING): generar **un artefacto cada vez** y revisarlo antes del siguiente |
| `/opsx:ff` | Changes pequeños: generar todos los artefactos pendientes en un solo paso |
| `/opsx:verify` | Antes de archivar: comprobar que la implementación cumple las specs y las tareas |
| `/opsx:bulk-archive` | Cierre de sprint |
| `/opsx:onboard` | Incorporación de una persona nueva: tutorial dentro del propio repositorio |

## Stores (beta): specs compartidas entre repositorios (opcional)

> **Opcional.** Es una funcionalidad en fase beta, orientada a organizaciones con varios repositorios. Se incluye a título informativo.

En los apartados anteriores todo se encuentra en un único repositorio. Sin embargo, `gold.daily_sales` es un contrato entre **Data Platform** (que lo produce) y **BI** (que lo consume desde otro repositorio). Los *stores* de OpenSpec son repositorios independientes que solo contienen `openspec/` (specs y changes) y se comparten con `git push`:

```bash
openspec store setup mercaluz-contracts
```

```bash
openspec store list
```

A partir de ese momento, los comandos aceptan `--store <id>` (`openspec list --specs --store mercaluz-contracts`) y los workflows `/opsx:*` utilizan el store cuando se les indica. Casos de uso en Mercaluz:

- Data Platform es responsable de las specs de gold; BI las consulta en modo de solo lectura desde su agente de IA.
- Un change que afecta al pipeline **y** a un informe de Power BI: un único plan, con código en dos repositorios.

> Los stores están en **beta** en la versión 1.14. Conviene probarlos con un equipo piloto antes de extender su uso, y consultar la [guía oficial](https://github.com/Fission-AI/OpenSpec/blob/main/docs/stores-beta/user-guide.md).

## Antipatrones

| Antipatrón | Síntoma | Solución |
|---|---|---|
| **Spec que describe el código** | "La función `build_silver` hace un `row_number()`…" | Describir solo el comportamiento observable; el resto, en el design |
| **Escenarios sin datos** | "WHEN hay datos inválidos THEN se tratan correctamente" | Usar pedidos, tiendas e importes reales |
| **Capability demasiado general** | `pipeline` con 40 requisitos | Una capability por producto de datos o interfaz |
| **Proponer e implementar en el mismo contexto** | La IA "recuerda" información que no figura en los artefactos | Ejecutar `/clear` antes de `/opsx:apply` |
| **Omitir la revisión** | `propose` → `apply` sin leer los artefactos | La revisión **es** el valor de OpenSpec; sin ella, la herramienta pierde su sentido |
| **Specs sin archivar** | 15 changes activos y specs principales desactualizadas | Archivar al desplegar y ejecutar `validate --archived` en CI |
| **Corregir la spec sin cambiar el código** | La spec principal describe algo que el sistema no hace | Las specs base reflejan el estado actual; los cambios, siempre mediante un change |
| **Usar un change para todo** | Changes para corregir una errata en un mensaje de log | Si no cambia el comportamiento: `skip_specs: true` en `.openspec.yaml`, o directamente sin change |

## Plan de adopción por fases

| Fase | Objetivo | Indicador |
|---|---|---|
| 1 | Instalación, `config.yaml` y specs base de **un** producto de datos crítico | `validate --specs --strict` sin errores |
| 2 | 2 o 3 changes reales con el ciclo completo y revisión en pareja | Número de decisiones tomadas en la revisión (y no en el código) |
| 3 | CI, CODEOWNERS y reglas basadas en la experiencia | Ningún change archivado con tareas pendientes |
| 4 | Retrospectiva: ¿schema propio?, ¿stores?, ¿perfil ampliado? | Incidencias causadas por cambios no comunicados a los consumidores |

---

## Lista de comprobación

- [ ] `config.yaml` con contexto, reglas por artefacto e indicaciones para apply y archive, ampliado con las reglas de la retrospectiva
- [ ] Schema `mercaluz-data` con el artefacto `data-contract`
- [ ] Comprensión de la función del workflow de CI y de `CODEOWNERS`
- [ ] Criterio para elegir entre explore, propose, update, apply, sync y archive

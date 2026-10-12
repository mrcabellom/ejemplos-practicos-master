# Taller práctico de OpenSpec para Data Engineering

> Desarrollo guiado por especificaciones (*spec-driven development*) con **OpenSpec** y **Claude Code**: construcción,
> paso a paso, del pipeline de datos de **Mercaluz**, una cadena española de supermercados.

Preparado para **OpenSpec 1.14**, Node.js 20.19 o superior y Python 3.12 (octubre de 2026).

---

## Qué es OpenSpec

OpenSpec es una capa ligera de **especificaciones en Markdown** que se guarda en el propio repositorio (`openspec/`).
Su objetivo es que el equipo y la IA **acuerden qué se va a construir antes de escribir código**, y que ese acuerdo
se mantenga como documentación actualizada del comportamiento del sistema.

```
  idea / ticket ──► /opsx:propose ──► revisión de proposal, specs, design y tasks ──► /opsx:apply ──► /opsx:archive
                     (planificación)    (iteración entre personas e IA)                  (implementación)  (actualización de las specs)
```

## Cómo funciona el taller

El pipeline se construye **desde cero y de menos a más**. En cada sesión se añade una pieza pequeña: se pide a la IA que la proponga, se revisa la spec, la IA escribe el código y los tests, y se comprueba con datos reales que funciona. Las primeras sesiones crean capacidades nuevas; las siguientes modifican las existentes cuando aparecen problemas o nuevas necesidades del negocio.

## Por qué es útil en Data Engineering

En una plataforma de datos, **el "qué" es un contrato con otros equipos**: las columnas de gold que lee Power BI,
los ficheros que procesa la macro de Finanzas o los datos personales que supervisa la DPO. Un cambio menor en el
código puede afectar a consumidores que el equipo no ve. OpenSpec obliga a escribir ese contrato (requisitos y
escenarios con datos concretos) **antes** de modificar el pipeline, y a que lo revisen las personas adecuadas.

| Problema habitual en Data Engineering | Cómo ayuda OpenSpec |
|---|---|
| ¿Afecta este cambio a algún informe? | `proposal.md` incluye una sección *Impact* con los consumidores y los cambios **BREAKING** |
| La IA implementa algo distinto de lo que se necesitaba | Los escenarios fijan cifras concretas (por ejemplo, `total_amount = 26,09`) antes de escribir código |
| Nadie sabe cómo se comporta la ingesta al reprocesar un día | `openspec/specs/` documenta el comportamiento del sistema, y lo que no está especificado se hace visible |
| Las decisiones técnicas (MERGE frente a sobrescritura, hash frente a HMAC) se pierden en conversaciones | `design.md` recoge alternativas y riesgos, versionado junto al código |
| Legal y Finanzas no leen Python | Pueden revisar `proposal.md` y `spec.md`, escritos en lenguaje natural |

---

## El caso: Mercaluz Data Platform

![Logotipo de Mercaluz](images/mercaluz-logo-1a.png)

| | |
|---|---|
| **Empresa** | Mercaluz: 120 supermercados y venta online |
| **Equipo** | Data Platform (6 personas): Lucía (Head of Data), Javier y tú (data engineers) |
| **Partes interesadas** | Marta (Control de Gestión, Finanzas), equipo de BI (Power BI) y Andrés (DPO) |
| **Repositorio** | [`mercaluz-data-platform/`](mercaluz-data-platform/README.md): ficheros diarios de pedidos y un proyecto Python con DuckDB, todavía sin pipeline |
| **Objetivo** | Construir un pipeline con arquitectura medallion que alimente Power BI y un fichero diario para Finanzas |

```
landing CSV ─► bronze.orders_raw ─► silver.order_lines ─► gold.daily_sales ─► exports/finance_daily_sales.csv
```

---

## Programa del taller

| # | Sesión | Qué se construye | Qué se aprende de OpenSpec |
|---|--------|------------------|----------------------------|
| 0 | [Instalación y configuración](sessions/00-installation-and-setup.md) | Entorno y `config.yaml` | Instalación, `openspec init`, contexto y reglas del proyecto |
| 1 | [Primer change: bronze](sessions/01-bronze-ingestion.md) | Carga de los CSV en bronze | Specs y changes, estructura de un requisito, ciclo completo |
| 2 | [Silver: líneas de pedido](sessions/02-silver-order-lines.md) | Líneas tipadas y depuradas | Varios requisitos, nombres neutros, lo que la spec no dice |
| 3 | [Gold: ventas diarias](sessions/03-gold-daily-sales.md) | Ventas por día y tienda | Escenarios con cifras, decisiones de negocio explícitas |
| 4 | [Export para Finanzas](sessions/04-finance-export.md) | Fichero CSV para Excel | El formato como contrato, sección *Impact* |
| 5 | [Calidad de datos](sessions/05-data-quality.md) | Reglas y cuarentena | Primer MODIFIED, tests que cambian con la spec |
| 6 | [Reprocesar sin duplicar](sessions/06-reprocessing.md) | Ingesta idempotente | Comportamiento no especificado, `design.md` con alternativas |
| 7 | [Avanzada: métricas sin IVA](sessions/07-advanced-net-revenue.md) | Ventas netas para Finanzas | BREAKING, REMOVED, versionado de contratos de datos |
| 8 | [Avanzada: RGPD](sessions/08-advanced-gdpr.md) | Seudonimización de emails | `/opsx:explore`, revisión por perfiles no técnicos |

**Anexos:** [OpenSpec en equipo](appendix/openspec-in-teams.md) · [referencia de comandos](appendix/command-cheatsheet.md) · [patrones de specs para Data Engineering](appendix/data-engineering-spec-patterns.md) · [problemas frecuentes](appendix/troubleshooting.md) · [glosario](appendix/glossary.md)

> **Núcleo y sesiones avanzadas.** Las sesiones 0 a 6 forman el núcleo del taller. Las sesiones 7 y 8 son avanzadas e independientes entre sí, y pueden empezarse desde el código de referencia de `solutions/advanced-start/`. Los apartados sobre producción (Airflow, Databricks, CI en GitHub) están marcados como *opcionales*.

---

## Estructura del repositorio

```
.
├── README.md                       ← este documento
├── sessions/                       ← guía paso a paso de cada sesión
├── appendix/                       ← material de referencia
├── mercaluz-data-platform/         ← repositorio de la empresa (punto de partida: datos, sin pipeline)
└── solutions/
    ├── session-00/openspec/config.yaml
    ├── session-01…08/openspec/changes/<change>/   (proposal, specs, design y tasks de referencia)
    ├── advanced-start/                            (repositorio completo al final de la sesión 6)
    └── appendix-teams/                            (schema propio, CI y plantilla de pull request)
```

### Uso de las soluciones

Las soluciones de cada sesión contienen los **artefactos de OpenSpec** de referencia, no código: el código lo escribe la IA de cada participante a partir de su propia spec. Sirven para comparar la estructura, el nivel de detalle y las decisiones, no para copiarlas literalmente; la IA generará textos distintos.

La única excepción es `solutions/advanced-start/`, que contiene el código completo al final de la sesión 6 para empezar directamente las sesiones avanzadas. Para retomar el taller desde cualquier sesión, consulta [Problemas frecuentes](appendix/troubleshooting.md#retomar-el-taller-desde-una-sesión-intermedia).

## Requisitos previos

- Node.js **≥ 20.19** para OpenSpec ([instrucciones de instalación](sessions/00-installation-and-setup.md#instalar-nodejs)) y [uv](https://docs.astral.sh/uv/), que instala Python 3.12 (versión fijada en `mercaluz-data-platform/.python-version`).
- Claude Code (CLI, aplicación de escritorio o extensión del IDE). OpenSpec es compatible con más de 30 asistentes; el taller utiliza Claude Code.
- Git (solo en local; no se necesita cuenta de GitHub).
- Conocimientos básicos de Python y SQL (`SELECT`, `WHERE`, `GROUP BY`). No se requiere experiencia en Data Engineering: la [sesión 0](sessions/00-installation-and-setup.md#04-conceptos-básicos-de-datos) explica la arquitectura medallion con los datos de Mercaluz, y el [glosario](appendix/glossary.md) recoge el resto de términos.

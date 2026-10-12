# Spec Kit en la práctica

> Desarrollo guiado por especificaciones (*spec-driven development*) con **GitHub Spec Kit** y **Claude Code**: un
> único cambio, de la petición de negocio al pipeline verificado, sobre los datos de ventas de **La Despensa**, una
> cadena de alimentación con dos tiendas.

Verificado con **Spec Kit (`specify-cli`) 1.1.3** y Python 3.12 (octubre de 2026).

---

## Qué es Spec Kit

Spec Kit es el kit de GitHub para hacer *spec-driven development* con agentes de IA. Tiene dos piezas:

- Una **constitución** (`.specify/memory/constitution.md`) con las reglas del proyecto, que se escribe una vez.
- Para cada cambio, una carpeta `specs/NNN-nombre/` con la especificación, el plan y las tareas. La IA redacta cada
  artefacto, tú lo revisas, y el siguiente paso parte de lo que ha quedado escrito.

```
/speckit-constitution ──► /speckit-specify ──► /speckit-clarify ──► /speckit-plan ──► /speckit-tasks ──► /speckit-implement
 (reglas del equipo)       (qué y por qué)      (dudas de negocio)    (cómo)             (lista de tareas)   (código y tests)
```

| Comando | Artefacto que genera |
|---|---|
| `/speckit-constitution` | `.specify/memory/constitution.md` |
| `/speckit-specify` | `specs/001-.../spec.md`, sin decisiones técnicas |
| `/speckit-clarify` | Sección `## Clarifications` de `spec.md`, con las respuestas a las dudas |
| `/speckit-plan` | `plan.md`, `research.md`, `data-model.md`, `contracts/` y `quickstart.md` |
| `/speckit-tasks` | `tasks.md`, con las tareas agrupadas por historia de usuario |
| `/speckit-implement` | El código y los tests |

## Cómo funciona el ejemplo

Se recorre **un solo cambio** completo: una tabla con las ventas diarias de cada tienda. Primero se fijan las reglas
del equipo de datos (la constitución) y después el cambio pasa por todos los comandos de Spec Kit, desde la
especificación hasta el código.

---

## El caso: La Despensa

| | |
|---|---|
| **Empresa** | La Despensa: cadena de alimentación en Madrid con dos tiendas (`S01` y `S02`) |
| **Situación** | Cada mañana, Operaciones suma manualmente en una hoja de cálculo las ventas del día anterior, y las cifras no siempre coinciden |
| **Partes interesadas** | Lucía Herrero (responsable de Operaciones) y el equipo de datos |
| **Repositorio** | [`la-despensa-data/`](la-despensa-data/README.md): la petición de Lucía, el CSV de pedidos y un proyecto Python vacío |
| **Objetivo** | Una tabla `daily_sales` con los pedidos, las unidades y el importe bruto de cada tienda y día |

La responsable de Operaciones ha escrito un [brief](la-despensa-data/docs/brief.md) con lo que necesita. El fichero
de pedidos, [`orders.csv`](la-despensa-data/data/raw/orders.csv), tiene 14 líneas y algunos **problemas habituales
en datos reales** que el brief no menciona:

| Línea del CSV | Problema | Pregunta sin respuesta | Decisión de la solución |
|---|---|---|---|
| `O-1003` (dos veces) | Línea duplicada | ¿Se cuenta dos veces? | Una sola vez; la copia se rechaza como `duplicate` |
| `O-1004` | Pedido `cancelled` | ¿Es una venta? | No; se rechaza como `not_completed` |
| `O-1005`, `O-1009` | Cantidad 0 y cantidad negativa (devolución) | El brief ya lo dice: no son ventas | Se rechazan como `non_positive_quantity` |
| `O-1006` | 22:30 UTC, que son las **00:30 del día siguiente** en Madrid | ¿A qué día pertenece? | Al día de Madrid: cuenta el 2 de octubre |
| `O-1010` | Sin tienda | ¿Dónde se cuenta? | En ninguna; se rechaza como `missing_store` |

Ninguna de estas decisiones se le da a la IA de antemano. Spec Kit tiene un paso dedicado a sacarlas a la luz,
`/speckit-clarify`, **antes** de decidir cómo se programa. Si una se escapa, acaba como un error silencioso en
las cifras.

---

## Estructura del repositorio

```
.
├── README.md                     ← este documento
├── la-despensa-data/             ← repositorio de la empresa (punto de partida: brief y datos, sin código)
└── solution/                     ← artefactos de Spec Kit de referencia al terminar el cambio
    ├── .specify/memory/constitution.md
    └── specs/001-daily-sales/
        ├── spec.md  plan.md  research.md  data-model.md  quickstart.md  tasks.md
        ├── contracts/tables.md
        └── checklists/requirements.md
```

La solución contiene solo los **artefactos de Spec Kit** de referencia, no código: el código lo escribe la IA a
partir de esos artefactos. Sirven para comparar la estructura, el nivel de detalle y las decisiones; la IA generará
textos distintos. Tampoco incluye `.claude/skills/` ni `.specify/scripts/` y `.specify/templates/`, porque los
genera `specify init`.

## Requisitos previos

- [uv](https://docs.astral.sh/uv/), que instala Python 3.12 (versión fijada en `la-despensa-data/.python-version`)
  y ejecuta la CLI de Spec Kit sin instalarla.
- Claude Code (CLI, aplicación de escritorio o extensión del IDE).
- Git (solo en local; no se necesita cuenta de GitHub).
- Conocimientos básicos de Python y de SQL.

---

## 1 · Instalación y preparación

### 1.1 Requisitos

| Herramienta | Versión mínima | Comprobación |
|---|---|---|
| uv | Cualquier versión reciente | `uv --version` |
| Python | 3.12 (fijada en `.python-version`; `uv sync` la descarga si no está instalada) | `uv python find` |
| Git | Cualquier versión | `git --version` |
| Claude Code | La más reciente | `claude --version` (o la aplicación de escritorio) |

> **Terminales:** la guía funciona en Git Bash, macOS, Linux, PowerShell y cmd. La mayoría de los comandos (`git`,
> `uv`, `uvx`) son iguales en todos ellos. Cuando un comando cambia según el terminal, se indican las variantes.

### 1.2 Preparar la copia de trabajo del repositorio

Trabaja siempre sobre una **copia** del repositorio, para poder repetir el ejemplo desde el principio. Desde la carpeta
`unit5-demos/spec-kit`, crea la carpeta `taller` en tu carpeta de usuario, copia el repositorio de La Despensa y sitúate
en la copia:

**Git Bash, macOS y Linux:**

```bash
mkdir -p ~/taller
cp -r la-despensa-data ~/taller/
cd ~/taller/la-despensa-data
```

**PowerShell:**

```powershell
New-Item -ItemType Directory -Force "$HOME\taller"
Copy-Item -Recurse la-despensa-data "$HOME\taller\"
Set-Location "$HOME\taller\la-despensa-data"
```

**cmd:**

```bat
mkdir "%USERPROFILE%\taller"
xcopy la-despensa-data "%USERPROFILE%\taller\la-despensa-data\" /E /I /H
cd /d "%USERPROFILE%\taller\la-despensa-data"
```

A continuación, inicializa Git en la copia (igual en todos los terminales):

```bash
git init -b main
```

```bash
git add .
```

```bash
git commit -m "Initial state of La Despensa data repository"
```

Instala las dependencias del proyecto:

```bash
uv sync
```

### 1.3 Instalar Spec Kit en el proyecto

Inicializa Spec Kit en la carpeta actual, solo para Claude Code. El comando descarga la CLI `specify` en la versión
1.1.3 y la ejecuta sin instalarla:

```bash
uvx --from git+https://github.com/github/spec-kit.git@v1.1.3 specify init --here --integration claude --force --non-interactive
```

- **`--here`:** inicializa la carpeta actual en lugar de crear una nueva.
- **`--force`:** no pide confirmación aunque la carpeta no esté vacía.
- **`--non-interactive`:** no hace preguntas y usa las opciones por defecto; por ejemplo, scripts de PowerShell
  en Windows y de Bash en macOS y Linux.

Ficheros generados:

```
la-despensa-data/
├── .claude/skills/speckit-*/     ← comandos /speckit-* para Claude Code
└── .specify/
    ├── memory/constitution.md    ← la constitución, todavía con la plantilla vacía
    ├── templates/                ← plantillas de spec, plan y tareas
    └── scripts/                  ← scripts que usan los comandos (PowerShell en Windows, Bash en macOS y Linux)
```

```bash
git add .
```

```bash
git commit -m "Install Spec Kit"
```

### 1.4 Comprobar la integración con Claude Code

Abre (o reinicia) Claude Code en la carpeta `la-despensa-data` y escribe `/speckit-`. Deben aparecer los comandos de
Spec Kit. Esta guía utiliza los seis de la tabla del principio. Hay otros opcionales, como `/speckit-analyze`
(coherencia entre artefactos) y `/speckit-checklist` (listas de calidad de los requisitos).

---

## 2 · Constitución: las reglas del equipo de datos

```text
/speckit-constitution Somos el equipo de datos de La Despensa. Principios:
1) Pipelines idempotentes: reejecutar con la misma entrada da el mismo resultado.
2) Dinero siempre en DECIMAL, nunca float; todo redondeo debe estar especificado.
3) Nada se descarta en silencio: cada fila rechazada queda registrada con un motivo.
4) Cada escenario de aceptación tiene un test con cifras concretas sobre un fichero de prueba pequeño.
5) Lo más simple posible: SQL sobre DuckDB, Python 3.12, pytest, uv.
```

Un pipeline es **idempotente** si ejecutarlo dos veces con los mismos datos deja las tablas exactamente igual, sin
duplicar filas. Es lo que permite repetir una carga que ha fallado sin miedo.

### Revisar

Abre `.specify/memory/constitution.md` (referencia: [`constitution.md`](solution/.specify/memory/constitution.md)):

- [ ] Los cinco principios están numerados (I–V) y usan **MUST** para lo obligatorio.
- [ ] Hay una sección de restricciones técnicas con Python 3.12, DuckDB, pytest y uv.
- [ ] La versión es `1.0.0`.

La constitución es **contexto permanente**: cada `/speckit-plan` incluye un *Constitution Check* que comprueba el
plan contra estos principios. Es el lugar para las normas que el equipo no quiere repetir en cada cambio.

```bash
git add .
```

```bash
git commit -m "Add data team constitution"
```

---

## 3 · Specify: qué se construye, sin tecnología

```text
/speckit-specify Quiero una tabla daily_sales con las ventas por tienda y día a partir del CSV de pedidos
data/raw/orders.csv: número de pedidos, unidades e importe bruto. Las líneas con cantidad menor o igual a cero
no cuentan como venta. La usa el equipo de Operaciones para comparar tiendas cada mañana. El brief completo
está en docs/brief.md.
```

### Revisar

Abre `specs/001-daily-sales/spec.md` (referencia: [`spec.md`](solution/specs/001-daily-sales/spec.md)). El nombre
de la carpeta lo elige la IA y puede variar; `.specify/feature.json` apunta a ella.

| Elemento | Significado |
|---|---|
| *User Stories* (P1, P2…) | Historias de usuario con prioridad; la P1 es el mínimo que ya aporta valor |
| *Acceptance Scenarios* | Escenarios **Given / When / Then** (dado / cuando / entonces) que después serán tests |
| `FR-00x` | Requisitos funcionales |
| `SC-00x` | Criterios de éxito medibles |
| `checklists/requirements.md` | La IA evalúa la calidad de su propia especificación |

- [ ] La especificación no menciona DuckDB, Python ni SQL: eso se decide en el plan.
- [ ] Abre `data/raw/orders.csv` y comprueba **cuáles de los problemas de la tabla del caso** cubre la
  especificación. Lo normal es que falten varios; para eso está el paso siguiente.

Puede que la especificación incluya hasta tres marcadores `[NEEDS CLARIFICATION]` y que la IA pregunte
directamente. Si lo hace, responde con la tabla del paso 4.

---

## 4 · Clarify: las decisiones de negocio

```text
/speckit-clarify
```

La IA hace hasta **cinco preguntas**, de una en una y con una opción recomendada. Respuestas para este ejemplo:

| Pregunta probable | Respuesta |
|---|---|
| ¿En qué zona horaria se decide el día de una venta? | **Europe/Madrid**; el CSV viene en UTC |
| ¿Qué se hace con las líneas duplicadas? | Contarlas una vez; la copia se rechaza como `duplicate` |
| ¿Cuentan los pedidos cancelados? | No; se rechazan como `not_completed` |
| ¿Qué se hace con las líneas sin tienda? | Se rechazan como `missing_store` |

> Si la IA no pregunta por la zona horaria, plantéalo tú:
> `/speckit-clarify ¿En qué zona horaria se decide el día de una venta?`. Merece la pena pensar por qué no la ha
> detectado: los datos están en UTC y la tienda está en Madrid.

### Revisar

Abre de nuevo `spec.md` (referencia: [`spec.md`](solution/specs/001-daily-sales/spec.md)):

- [ ] Hay una sección `## Clarifications` con cada pregunta y su respuesta.
- [ ] Las respuestas también han cambiado los requisitos y los escenarios afectados, no solo la sección de
  aclaraciones.
- [ ] Un escenario fija la cifra que depende de la zona horaria. En la referencia, el escenario 2 de la historia 1:

> `O-1006` (22:30 UTC) cuenta en **2026-10-02**, y S01 / 2026-10-01 queda en `gross_revenue = 7.95` (**no 13.95**).

Una cifra concreta en la especificación convierte una decisión de negocio en un test. Si alguien cambia el código y
corta el día en UTC, el test falla.

```bash
git add .
```

```bash
git commit -m "Add daily sales specification"
```

---

## 5 · Plan: cómo se construye y el contrato de datos

```text
/speckit-plan Python 3.12 con uv, DuckDB y pytest. Todo en SQL dentro de un módulo src/daily_sales/pipeline.py,
con una CLI que se ejecuta con python -m daily_sales. Usa data/raw/orders.csv como fichero de prueba. Tablas
publicadas: daily_sales y rejected_lines. Cada ejecución reconstruye las tablas completas. Código, comentarios
y nombres de ficheros en inglés.
```

### Revisar

Comprueba los ficheros nuevos de `specs/001-daily-sales/` (referencia:
[`solution/specs/001-daily-sales/`](solution/specs/001-daily-sales/)):

| Fichero | Contenido |
|---|---|
| [`plan.md`](solution/specs/001-daily-sales/plan.md) | Contexto técnico y **Constitution Check**: una tabla con los cinco principios y cómo los cumple el plan |
| [`research.md`](solution/specs/001-daily-sales/research.md) | Decisiones técnicas con sus alternativas: `timezone()` frente a sumar 2 horas, `row_number()` frente a `DISTINCT` |
| [`data-model.md`](solution/specs/001-daily-sales/data-model.md) | Flujo de tablas y **orden de las reglas de rechazo** |
| [`contracts/tables.md`](solution/specs/001-daily-sales/contracts/tables.md) | **El contrato de datos**: columnas, tipos, clave y nulos de las tablas publicadas |
| [`quickstart.md`](solution/specs/001-daily-sales/quickstart.md) | Cómo comprobar que el pipeline funciona |

- [ ] Todos los principios del *Constitution Check* están en verde.
- [ ] El contrato define `gross_revenue` como `DECIMAL`, no como `DOUBLE` (principio II).

Spec Kit nació para APIs, pero en datos el contrato es **el esquema de las tablas que leen otros equipos**: cambiar
un nombre, un tipo o la clave obliga a cambiar sus consultas. Si la IA no genera `contracts/`, pídele que lo escriba
así, como en la referencia.

---

## 6 · Tasks: la lista de tareas

```text
/speckit-tasks
```

### Revisar

Abre `tasks.md` (referencia: [`tasks.md`](solution/specs/001-daily-sales/tasks.md)):

- [ ] Las tareas están numeradas (`T001`, `T002`…) y agrupadas **por historia de usuario**; la historia 1 es el
  mínimo entregable.
- [ ] Las tareas marcadas con `[P]` se pueden hacer en paralelo, porque tocan ficheros distintos.
- [ ] En cada historia, los tests van **antes** que la implementación, como exige el principio IV.

*Opcional:* `/speckit-analyze` revisa la coherencia entre especificación, plan y tareas sin modificar nada. Sirve
para detectar, por ejemplo, un requisito sin tarea.

```bash
git add .
```

```bash
git commit -m "Add daily sales plan and tasks"
```

---

## 7 · Implement y comprobar

```text
/clear
```

```text
/speckit-implement
```

`/clear` vacía la conversación antes de programar: todo lo que la IA necesita está en `specs/001-daily-sales/` y en
la constitución, no en el chat. Durante la ejecución, la IA sigue `tasks.md` y marca cada tarea como hecha (`[x]`).

Cuando termine, comprueba el resultado por tu cuenta:

```bash
uv run pytest
```

La referencia tiene 7 tests. Ejecuta el pipeline:

```bash
uv run python -m daily_sales data/raw/orders.csv --db warehouse.duckdb
```

Resultado esperado. El formato depende del código que haya generado la IA; lo que importa son **las cifras**:

```text
Lines read: 14
  rejected [duplicate]: 1
  rejected [missing_store]: 1
  rejected [non_positive_quantity]: 2
  rejected [not_completed]: 1
daily_sales rows: 4
store_id | sales_date | orders | units | gross_revenue
S01 | 2026-10-01 | 2 | 4 | 7.95
S01 | 2026-10-02 | 2 | 6 | 18.75
S02 | 2026-10-01 | 1 | 6 | 7.50
S02 | 2026-10-02 | 2 | 6 | 15.80
```

Ejecuta el mismo comando una segunda vez: la salida debe ser idéntica (principio I). La base de datos
`warehouse.duckdb` queda fuera del repositorio porque `.gitignore` la excluye.

### Revisar

Abre el código que ha escrito la IA (`src/daily_sales/` y `tests/`):

- [ ] Las 14 líneas leídas son 9 válidas y 5 rechazadas: no se pierde ninguna (principio III).
- [ ] Cada decisión del paso 4 se puede localizar en el SQL: la conversión a la hora de Madrid
  (`timezone('Europe/Madrid', …)`), los duplicados (`row_number()`) y el `CASE` con los motivos de rechazo.
- [ ] Cada escenario de `spec.md` tiene su test, con las mismas cifras.

```bash
git add .
```

```bash
git commit -m "Implement daily sales pipeline"
```

---

## Conclusiones

- La IA ha escrito todo el código, pero las decisiones de negocio (zona horaria, duplicados, pedidos cancelados,
  líneas sin tienda) se han tomado y revisado antes, en `spec.md`.
- La constitución se ha escrito una vez y el plan la ha comprobado: el dinero en `DECIMAL` y la tabla de rechazos
  no dependen de que alguien se acuerde de pedirlos.
- Cada línea importante del SQL se puede relacionar con un requisito (`FR-00x`) o con una aclaración.

## Spec Kit frente a OpenSpec

| | **Spec Kit** | **OpenSpec** |
|---|---|---|
| Unidad de trabajo | Feature: `specs/NNN-nombre/` | Change: `openspec/changes/<nombre>/` |
| Al terminar el cambio | La carpeta se queda como está | `archive` incorpora los deltas a `openspec/specs/` |
| Estado actual del sistema | No hay una fuente única; se lee feature a feature | `openspec/specs/` refleja siempre el comportamiento actual |
| Reglas globales | `constitution.md` y *Constitution Check* en cada plan | `config.yaml` (contexto y reglas) |
| Preguntas a la IA | `/speckit-clarify`, integrado en el flujo | `/opsx:explore`, una conversación libre |
| Más adecuado para | Funcionalidades nuevas con un proceso guiado | Sistemas existentes que cambian a menudo |

## Problemas frecuentes

| Síntoma | Solución |
|---|---|
| No aparecen los comandos `/speckit-*` | Reinicia Claude Code después de `specify init` y comprueba que existe `.claude/skills/speckit-specify/SKILL.md` |
| Los comandos `/speckit.specify` (con punto) no existen | Desde Spec Kit 1.0, con Claude Code los comandos son *skills* con guion: `/speckit-specify` |
| `specify init` se detiene esperando una respuesta o porque la carpeta no está vacía | Añade `--force --non-interactive`, como en el apartado 1.3 |
| `uv` o `uvx` fallan con *failed to hardlink* (Windows y OneDrive) | Define la variable de entorno `UV_LINK_MODE=copy` |
| No se crea una rama de Git para la feature | Es lo esperado: desde la versión 1.x la rama la crea la extensión `git` (`--extension git` en `specify init`). La carpeta `specs/` se crea igualmente |
| `/speckit-plan` trabaja sobre la feature equivocada | Revisa `.specify/feature.json`, que apunta a la feature activa |
| `No module named daily_sales` al ejecutar el pipeline | Falta el `[build-system]` en `pyproject.toml` para el paquete de `src/`. Pide a Claude que lo añada, como hace la tarea `T001` de la referencia |
| La CLI falla con `UnicodeEncodeError` en Windows | Define la variable de entorno `PYTHONUTF8=1` |

---

## Lista de comprobación final

- [ ] `uv sync` termina sin errores
- [ ] Los comandos `/speckit-*` aparecen en Claude Code
- [ ] `.specify/memory/constitution.md` tiene los cinco principios y la versión `1.0.0`
- [ ] `spec.md` tiene la sección `## Clarifications`, con la zona horaria de Madrid
- [ ] El plan tiene el *Constitution Check* en verde y el contrato de `daily_sales` y `rejected_lines`
- [ ] `uv run pytest` no devuelve errores
- [ ] El pipeline da las 4 filas esperadas, con S01 / 2026-10-01 en `7.95`
- [ ] Todo está guardado en commits en `main`

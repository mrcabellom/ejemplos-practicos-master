# GSD Core en la práctica

> Desarrollo guiado por especificaciones (*spec-driven development*) con **GSD Core** y **Claude Code**: un único
> cambio, de la petición de negocio al código verificado, sobre la API de reservas de **Kinesia**, una clínica de
> fisioterapia.

Preparado para **GSD Core (`@opengsd/gsd-core`) 1.16**, Node.js 24 o superior y Python 3.12 (octubre de 2026).

---

## Qué es GSD Core

GSD Core es un sistema de *spec-driven development* para agentes de IA. Divide el trabajo en **fases** y guarda
la memoria del proyecto en ficheros Markdown dentro de `.planning/`. El trabajo pesado (planificar, programar,
verificar) lo hacen **subagentes que empiezan con el contexto limpio** y leen solo lo que necesitan de esos ficheros.

```
/gsd-new-project ──► /gsd-discuss-phase ──► /gsd-plan-phase ──► /gsd-execute-phase ──► /gsd-verify-work
 (qué se construye)   (cómo se quiere)       (tareas pequeñas)    (subagentes, commits)   (prueba de aceptación)
```

Una conversación larga con la IA **pierde calidad** a medida que se llena el contexto. GSD lo evita así: la sesión
principal solo coordina, y la información se conserva en `.planning/`, no en el chat. Por eso la guía usa `/clear`
entre pasos.

## Cómo funciona el ejemplo

Se recorre **un solo cambio** completo: la primera fase del proyecto, que añade la consulta de huecos libres y la
reserva de citas. En cada paso, Claude Code redacta un artefacto, tú lo revisas, y el siguiente paso parte de lo
que queda escrito en `.planning/`.

---

## El caso: Kinesia

| | |
|---|---|
| **Empresa** | Kinesia: clínica de fisioterapia en Madrid con dos fisioterapeutas, Ana (`ANA`) y Luis (`LUIS`) |
| **Situación** | Las citas se llevan en una hoja de cálculo compartida: hay dobles reservas, citas con 5 minutos de antelación y citas en días festivos |
| **Partes interesadas** | Marta Gil (gerente), recepción y los dos fisioterapeutas |
| **Repositorio** | [`kinesia-booking-api/`](kinesia-booking-api/README.md): la petición de Marta y un proyecto Python vacío |
| **Objetivo** | Una API para recepción que muestre los huecos libres y permita reservar sin solapes |

La gerente ha escrito un [brief](kinesia-booking-api/docs/brief.md) con las reglas de la clínica: sesiones de
45 minutos, de lunes a viernes de 9 a 14 y de 16 a 20, cerrado en festivos nacionales y con al menos 2 horas de
antelación. Parece completo, pero deja **decisiones sin tomar**:

| El brief dice… | Pregunta sin respuesta | Decisión de la solución |
|---|---|---|
| "Sesiones de 45 min, de 9 a 14" | ¿Se ofrece una cita a las 13:30 que acaba a las 14:15? | No: el último hueco es a las 12:45 (11 huecos al día) |
| "Somos dos fisios" | ¿Puede un paciente tener cita con Ana y con Luis a la misma hora? | No: `409 patient_busy` |
| "Al menos 2 horas de antelación" | ¿Vale justo 2 horas? ¿Y una reserva en el pasado? | Justo 2 horas sí; el pasado se rechaza con `too_late` |
| "Festivos nacionales, cerrado" | ¿Qué festivos? El 12 de octubre de 2026 es lunes | Lista fija en el código: `422 closed` |

Ninguna de estas decisiones se le da a la IA de antemano. GSD tiene un paso dedicado a sacarlas a la luz,
`/gsd-discuss-phase`, **antes** de planificar.

---

## Estructura del repositorio

```
.
├── README.md                       ← este documento
├── kinesia-booking-api/            ← repositorio de la empresa (punto de partida: brief, sin código)
└── solution/.planning/             ← artefactos de GSD de referencia al terminar el cambio
    ├── PROJECT.md  REQUIREMENTS.md  ROADMAP.md  STATE.md  config.json
    └── phases/01-schedule-and-bookings/
        └── 01-CONTEXT.md  01-01-PLAN.md  01-01-SUMMARY.md  01-VERIFICATION.md  01-UAT.md
```

La solución contiene solo los **artefactos de GSD** de referencia, no código: el código lo escribe la IA a partir
de esos artefactos. Sirven para comparar la estructura, el nivel de detalle y las decisiones; la IA generará textos
distintos. Tampoco incluye `.claude/`, porque lo genera el instalador de GSD.

## Requisitos previos

- Node.js **24 o superior** y npm 10 o superior, para GSD Core (instrucciones de instalación en el apartado 1.1).
- [uv](https://docs.astral.sh/uv/), que instala Python 3.12 (versión fijada en `kinesia-booking-api/.python-version`).
- Claude Code (CLI, aplicación de escritorio o extensión del IDE).
- Git (solo en local; no se necesita cuenta de GitHub).
- Conocimientos básicos de Python y de APIs REST.

---

## 1 · Instalación y preparación

### 1.1 Requisitos

| Herramienta | Versión mínima | Comprobación |
|---|---|---|
| Node.js | 24 | `node --version` |
| npm | 10 | `npm --version` |
| Python | 3.12 (fijada en `.python-version`; `uv sync` la descarga si no está instalada) | `uv python find` |
| uv | Cualquier versión reciente | `uv --version` |
| Git | Cualquier versión | `git --version` |
| Claude Code | La más reciente | `claude --version` (o la aplicación de escritorio) |

> **Terminales:** la guía funciona en Git Bash, macOS, Linux, PowerShell y cmd. La mayoría de los comandos (`git`,
> `uv`, `npx`) son iguales en todos ellos. Cuando un comando cambia según el terminal, se indican las variantes.

#### Instalar Node.js

GSD Core se instala con npm, que se distribuye junto con Node.js. Si `node --version` devuelve un error o una
versión inferior a la 24, instala la versión **LTS**:

**Windows** (PowerShell):

```powershell
winget install OpenJS.NodeJS.LTS
```

**macOS** (con Homebrew):

```bash
brew install node
```

**Linux** (también válido en macOS): con [nvm](https://github.com/nvm-sh/nvm), que instala Node.js en el usuario
actual sin necesidad de `sudo`. Instala nvm según las instrucciones de su README y, a continuación, ejecuta:

```bash
nvm install --lts
```

**Cierra y vuelve a abrir el terminal** para que reconozca los nuevos comandos, y comprueba la instalación:

```bash
node --version
```

### 1.2 Preparar la copia de trabajo del repositorio

Trabaja siempre sobre una **copia** del repositorio, para poder repetir el ejemplo desde el principio. Desde la carpeta
`unit5-demos/gsd-core`, crea la carpeta `taller` en tu carpeta de usuario, copia el repositorio de Kinesia y sitúate en
la copia:

**Git Bash, macOS y Linux:**

```bash
mkdir -p ~/taller
cp -r kinesia-booking-api ~/taller/
cd ~/taller/kinesia-booking-api
```

**PowerShell:**

```powershell
New-Item -ItemType Directory -Force "$HOME\taller"
Copy-Item -Recurse kinesia-booking-api "$HOME\taller\"
Set-Location "$HOME\taller\kinesia-booking-api"
```

**cmd:**

```bat
mkdir "%USERPROFILE%\taller"
xcopy kinesia-booking-api "%USERPROFILE%\taller\kinesia-booking-api\" /E /I /H
cd /d "%USERPROFILE%\taller\kinesia-booking-api"
```

A continuación, inicializa Git en la copia (igual en todos los terminales):

```bash
git init -b main
```

```bash
git add .
```

```bash
git commit -m "Initial state of Kinesia booking API"
```

Instala las dependencias del proyecto:

```bash
uv sync
```

### 1.3 Instalar GSD Core en el proyecto

Instala GSD Core **solo en este proyecto** y solo para Claude Code:

```bash
npx @opengsd/gsd-core@latest --claude --local
```

> El paquete es **`@opengsd/gsd-core`**, con *scope*. El paquete `gsd-core` sin *scope* es un marcador vacío, y el
> antiguo `get-shit-done-cc` está archivado. Para que todo el equipo use la misma versión, fíjala:
> `npx @opengsd/gsd-core@1.16.0 --claude --local`.

Ficheros generados:

```
kinesia-booking-api/
└── .claude/
    ├── commands/gsd-*.md        ← comandos /gsd-* para Claude Code
    ├── agents/gsd-*.md          ← subagentes especializados (gsd-planner, gsd-executor, gsd-verifier…)
    ├── gsd-core/                ← flujos de trabajo y plantillas que leen los comandos
    ├── hooks/                   ← hooks que vigilan el contexto, bloquean lecturas de .env, etc.
    └── settings.local.json      ← activa los hooks
```

```bash
git add .
```

```bash
git commit -m "Install GSD Core"
```

### 1.4 Comprobar la integración con Claude Code

Abre (o reinicia) Claude Code en la carpeta `kinesia-booking-api` y escribe `/gsd-`. Deben aparecer los comandos de
GSD. Esta guía utiliza estos:

| Comando | Función |
|---|---|
| `/gsd-new-project` | Definir el proyecto: visión, requisitos y fases |
| `/gsd-discuss-phase N` | Tomar las decisiones de implementación de una fase |
| `/gsd-plan-phase N` | Dividir la fase en planes con tareas pequeñas y verificables |
| `/gsd-execute-phase N` | Ejecutar los planes con subagentes, con un commit por tarea |
| `/gsd-verify-work N` | Prueba de aceptación guiada |
| `/gsd-progress` | Ver en qué punto está el proyecto |

`/gsd-help` muestra la referencia completa.

---

## 2 · Definir el proyecto

```text
/gsd-new-project
```

A la pregunta *"What do you want to build?"*, responde:

```text
Una API REST para la recepción de Kinesia, una clínica de fisioterapia. El brief completo está en
@docs/brief.md. Stack: Python 3.12 (fijado en .python-version), FastAPI, SQLite con sqlite3 y pytest,
gestionado con uv. Estructura: paquete src/kinesia/, aplicación en kinesia.main:app y tests en tests/.
Nombres de fases, ficheros, código e identificadores en inglés; los textos "detail" de los errores, en
español, porque los lee recepción. Todo el alcance del brief cabe en una sola fase.
```

A continuación, GSD hace preguntas de aclaración y de configuración. Respuestas para este ejemplo:

| Pregunta | Respuesta | Motivo |
|---|---|---|
| *Mode* | Interactive | Permite revisar cada paso |
| *Granularity* | Coarse | Proyecto pequeño: una fase es suficiente |
| *Commit planning docs to git?* | Yes | `.planning/` es documentación del proyecto |
| *Research before planning each phase?* | No | Dominio sencillo; ahorra tiempo y tokens |
| *Plan Check* / *Verifier* | Yes / Yes | Revisan los planes y el código antes de darlos por buenos |
| Roadmap propuesto | Approve | Una fase: *Schedule and bookings* |

> Si el roadmap propone más de una fase, pide a Claude que lo agrupe: *"Agrupa todo en una sola fase llamada
> Schedule and bookings"*.

### Ajustar la configuración

Abre `.planning/config.json` y comprueba (o añade) estas dos claves; también puede hacerse con `/gsd-settings`:

```json
"response_language": "es",
"git": { "branching_strategy": "phase" }
```

- **`response_language`:** GSD responde y redacta los artefactos en español.
- **`branching_strategy`:** el ejecutor de GSD **no hace commits en `main`**. Con `phase`, cada fase se ejecuta en
  su propia rama (`gsd/phase-01-schedule-and-bookings`).

```bash
git add .planning/config.json
```

```bash
git commit -m "Configure GSD for Kinesia"
```

### Revisar

Comprueba en `.planning/` (referencia: [`solution/.planning/`](solution/.planning/)):

| Fichero | Contenido |
|---|---|
| [`PROJECT.md`](solution/.planning/PROJECT.md) | Visión, **Core Value** ("nunca dos pacientes en el mismo hueco"), restricciones y fuera de alcance |
| [`REQUIREMENTS.md`](solution/.planning/REQUIREMENTS.md) | Requisitos con identificador (`AGEN-01`, `RES-02`…) y su fase |
| [`ROADMAP.md`](solution/.planning/ROADMAP.md) | La fase, con su objetivo y **criterios de éxito observables** |
| [`STATE.md`](solution/.planning/STATE.md) | Dónde está el proyecto. Cada comando lo lee al empezar |
| [`config.json`](solution/.planning/config.json) | Las respuestas de configuración |

- [ ] Las cancelaciones aparecen fuera de alcance o en v2, como pide el brief.
- [ ] Cada requisito de v1 está asignado a la fase 1.

---

## 3 · Discutir la fase: las decisiones

```text
/clear
```

```text
/gsd-discuss-phase 1
```

GSD analiza la fase, detecta las **zonas grises** y pregunta cuáles se quieren discutir: elige todas. Después
pregunta de una en una, con opciones recomendadas. Respuestas para este ejemplo:

| Pregunta probable | Respuesta |
|---|---|
| ¿La última sesión puede terminar después del cierre? | No. La sesión debe **terminar** dentro del tramo: los últimos huecos son 12:45 y 19:00 |
| ¿Se puede reservar en cualquier minuto (10:10)? | No, solo al inicio de un hueco: `422 not_a_slot` |
| ¿Cómo se identifica al paciente para detectar dobles citas? | Por el teléfono: `409 patient_busy` |
| ¿Qué festivos? | Una lista fija de festivos nacionales entre semana; los locales, más adelante |
| ¿Dónde se guardan las citas? | SQLite en un fichero, con `sqlite3` de la librería estándar |
| ¿Formato de error? | Siempre `{"error": "<código>", "detail": "<texto>"}` |

> Si GSD no pregunta por la hora de cierre, plantéalo tú: *"¿Una cita a las 13:30 acabaría a las 14:15, la
> ofrecemos?"*.

### Revisar

Abre `01-CONTEXT.md` (referencia: [`01-CONTEXT.md`](solution/.planning/phases/01-schedule-and-bookings/01-CONTEXT.md)):

- [ ] Cada decisión tiene un identificador (`D-01`, `D-02`…).
- [ ] `D-01` dice que no se ofrece el hueco de las 13:30.
- [ ] `docs/brief.md` aparece en las referencias que los agentes **deben** leer.
- [ ] Lo que ha surgido pero no toca ahora (festivos configurables) está en `<deferred>`.

Estas decisiones son el contrato del cambio: en el paso siguiente, el revisor de planes comprueba que **cada `D-NN`
acaba en alguna tarea**.

---

## 4 · Planificar

```text
/clear
```

```text
/gsd-plan-phase 1
```

Si pregunta por la investigación previa, elige **Skip research**. Un subagente `gsd-planner` escribe el plan y un
`gsd-plan-checker` lo revisa (cobertura de requisitos y de decisiones) antes de guardarlo. Según el planificador,
puede generar uno o varios planes; la referencia tiene uno.

### Revisar

Abre `01-01-PLAN.md` (referencia: [`01-01-PLAN.md`](solution/.planning/phases/01-schedule-and-bookings/01-01-PLAN.md)):

| Elemento | Significado |
|---|---|
| `requirements: [...]` | Qué requisitos de `REQUIREMENTS.md` cubre el plan; ninguno puede quedar sin plan |
| `must_haves.truths` | Lo que debe ser **observable** al terminar; el verificador lo comprobará |
| `<task type="tracer">` | La primera tarea es una versión mínima **de extremo a extremo** (`GET /slots` real) antes de ampliar |
| `<verify><automated>` | El comando que el ejecutor **ejecuta** después de escribir el código (`uv run pytest …`) |

Un plan de GSD es una instrucción para un subagente que no ha visto la conversación. Por eso es tan explícito:
ficheros, qué leer primero, cómo verificar y cuándo está terminado.

---

## 5 · Ejecutar

```text
/clear
```

```text
/gsd-execute-phase 1
```

Durante la ejecución, GSD:

- Crea la rama `gsd/phase-01-schedule-and-bookings`.
- Ejecuta cada plan con un **subagente nuevo**, con el contexto limpio, que hace **un commit por tarea**.
- Al terminar el plan escribe `01-01-SUMMARY.md`. Al final, un `gsd-verifier` contrasta el código con los
  `must_haves` y escribe `01-VERIFICATION.md`.

Cuando termine, comprueba el resultado por tu cuenta:

```bash
git log --oneline
```

```bash
uv run pytest
```

La referencia tiene 13 tests. Arranca la API:

```bash
uv run uvicorn kinesia.main:app --app-dir src --reload
```

Abre en el navegador los huecos de Luis para el martes 13 de octubre de 2026:

```
http://127.0.0.1:8000/slots?therapist=LUIS&day=2026-10-13
```

```
{"therapist":"LUIS","day":"2026-10-13","slots":["09:00","09:45","10:30","11:15","12:00","12:45","16:00","16:45","17:30","18:15","19:00"]}
```

Son 11 huecos, sin 13:30 ni 19:45. El formato exacto depende del código que haya generado la IA; lo que importa son
los huecos. El 12 de octubre, festivo, devuelve una lista vacía.

Para probar las reservas, abre `http://127.0.0.1:8000/docs`, despliega `POST /appointments` y pulsa *Try it out*.
Usa un día laborable **posterior a hoy**, porque la API compara con la hora real y rechaza el pasado:

| Prueba | Resultado esperado |
|---|---|
| Reservar un hueco libre | `201`, y el hueco desaparece de `/slots` |
| Repetir la misma reserva con otro teléfono | `409 slot_taken` |
| El mismo teléfono, a la misma hora, con el otro fisio | `409 patient_busy` |
| Reservar a las 13:30 | `422 not_a_slot` |

Detén la API con Ctrl+C. Las citas se guardan en `kinesia.db`, que `.gitignore` excluye del repositorio.

Revisa también el código que ha escrito la IA (`src/kinesia/` y `tests/`) y comprueba que cada decisión `D-NN`
tiene su test.

---

## 6 · Verificar

```text
/clear
```

```text
/gsd-verify-work 1
```

GSD convierte lo construido en **comprobaciones de aceptación** y las presenta de una en una:

```
CHECKPOINT: Verification Required
Test 3: Intentar reservar el 12 de octubre
Expected: 422 con "error": "closed" y un detail que se entiende
Type `pass` or describe what's wrong.
```

Las comprobaciones que ya cubren los tests automáticos se dan por buenas; las que requieren criterio humano (por
ejemplo, si los mensajes de error se entienden) se preguntan. El resultado queda en `01-UAT.md` (referencia:
[`01-UAT.md`](solution/.planning/phases/01-schedule-and-bookings/01-UAT.md)).

Si una comprobación falla, describe el problema: GSD diagnostica la causa, escribe un **plan de arreglo** y propone
ejecutar de nuevo `/gsd-execute-phase 1`. Es la diferencia entre "el código está escrito" y "el código funciona".

### Integrar la fase en `main`

```bash
git switch main
```

```bash
git merge gsd/phase-01-schedule-and-bookings
```

`ROADMAP.md`, `REQUIREMENTS.md` y `STATE.md` ya reflejan que la fase está completa:

```text
/gsd-progress
```

---

## Conclusiones

- La IA ha escrito todo el código, pero las decisiones (último hueco a las 12:45, paciente identificado por teléfono,
  festivos fijos) se han tomado y revisado antes, en `01-CONTEXT.md`.
- Cada paso empieza con `/clear` y no se pierde nada: la memoria del proyecto está en `.planning/`.
- El plan es verificable: cada tarea indica cómo comprobarla, y el verificador contrasta el resultado con los
  `must_haves` antes de la prueba de aceptación.

## GSD Core frente a OpenSpec

| | **GSD Core** | **OpenSpec** |
|---|---|---|
| Unidad de trabajo | Fase de un roadmap (`.planning/phases/NN-*`) | Change (`openspec/changes/*`) |
| Antes de planificar | `discuss-phase`: decisiones de implementación (`D-NN`) | Revisión de proposal, specs y design |
| Ejecución | Subagentes con el contexto limpio, un commit por tarea | El agente sigue `tasks.md` |
| Después de programar | Verificador automático y prueba de aceptación guiada | `archive` incorpora los deltas a las specs |
| Estado del proyecto | `STATE.md` y `ROADMAP.md`, siempre actualizados | `openspec/specs/`, comportamiento actual del sistema |
| Coste | Más tokens y tiempo (muchos subagentes) | Bajo |

## Problemas frecuentes

| Síntoma | Solución |
|---|---|
| No aparecen los comandos `/gsd-*` | Reinicia Claude Code después de instalar y comprueba que existe `.claude/commands/gsd-new-project.md` |
| `npx` instala un paquete vacío | El paquete correcto es `@opengsd/gsd-core`, no `gsd-core` |
| El instalador falla por la versión de Node.js | GSD Core 1.16 requiere Node.js 24 o superior y npm 10 o superior |
| `FATAL: refusing to commit — HEAD is on 'main'` | Falta `"git": {"branching_strategy": "phase"}` en `.planning/config.json` |
| GSD responde en inglés | Falta `"response_language": "es"` en `.planning/config.json` |
| Un paso parece bloqueado | Los subagentes tardan varios minutos. Si no avanza, ejecuta `/clear` y repite el paso |
| No se sabe en qué punto está el proyecto | `/gsd-progress`, o abre `.planning/STATE.md` |
| `uv` falla con *failed to hardlink* (Windows y OneDrive) | Define la variable de entorno `UV_LINK_MODE=copy` |

---

## Lista de comprobación final

- [ ] `uv sync` termina sin errores
- [ ] Los comandos `/gsd-*` aparecen en Claude Code
- [ ] `.planning/` contiene `PROJECT.md`, `REQUIREMENTS.md`, `ROADMAP.md` y `STATE.md`, con una sola fase
- [ ] `01-CONTEXT.md` recoge las decisiones `D-NN`, incluida la del hueco de las 13:30
- [ ] `uv run pytest` no devuelve errores
- [ ] `/slots` devuelve 11 huecos en un día laborable y ninguno en festivo
- [ ] `/gsd-verify-work 1` termina sin incidencias abiertas
- [ ] La rama de la fase está integrada en `main`

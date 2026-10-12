# Problemas frecuentes

## Instalación

| Síntoma | Causa | Solución |
|---|---|---|
| `openspec: command not found` | La carpeta global de npm no está en el `PATH` | Ejecuta `npm config get prefix` y añade esa ruta (o `…/bin`) al `PATH`. Alternativa: `npx @fission-ai/openspec@latest <comando>` |
| PowerShell: *running scripts is disabled on this system* | La política de ejecución bloquea `openspec.ps1` | Usa `openspec.cmd` o Git Bash, o solicita al administrador del equipo que habilite `RemoteSigned` para tu usuario |
| `Unsupported engine` u otros errores durante la instalación | Versión de Node.js inferior a la 20.19 | Actualiza Node.js (nvm, fnm, Volta o el instalador oficial) |
| `--language does not overwrite an existing OpenSpec config` | Se ejecutó `openspec init --language es` en un repositorio que ya tenía `openspec/config.yaml` | No hace falta repetir `init`: el idioma se define en el campo `context` de `config.yaml` (sesión 0, apartado 0.8) |
| `Warning: could not parse … config.yaml (…)` ; ignoring it | `config.yaml` no es YAML válido: suele faltar una línea al pegarlo (por ejemplo, `context: \|`) o la sangría no es correcta | Copia el fichero de `solutions/session-00/openspec/config.yaml` en lugar de pegar el texto (sesión 0, apartado 0.8). Mientras el aviso aparezca, OpenSpec ignora todo el fichero |
| Los comandos `/opsx:*` no aparecen en Claude Code | No se seleccionó Claude en `init`, o Claude Code ya estaba abierto | Ejecuta `openspec init --tools claude` (o `openspec update`) y reinicia la sesión de Claude Code en la raíz del repositorio |
| Tras actualizar OpenSpec, los comandos se comportan como antes | Los ficheros de `.claude/` corresponden a la versión anterior | Ejecuta `openspec update` en el proyecto e incluye el resultado en un commit |

## Validación

| Mensaje | Significado | Solución |
|---|---|---|
| `must include at least one scenario` | Requisito sin `#### Scenario:` | Usa **4** almohadillas; no utilices viñetas para los escenarios |
| `Header "### Scenario: …" … is ignored` | Escenario con 3 almohadillas | Cámbialo a `####` |
| `should contain SHALL or MUST` | El texto del requisito no contiene ninguna palabra normativa | Añade `SHALL`/`MUST` en inglés, aunque el resto esté en español |
| `MODIFIED … omits scenario(s) the current spec still has` | El MODIFIED no incluye un escenario existente | Copia el escenario (puede cambiar su contenido, pero no su nombre). Consulta las sesiones 5 y 7 |
| `MODIFIED failed for header …` / requisito no encontrado | El nombre no coincide con el de la spec principal | Ejecuta `openspec show <capability> --type spec` y copia el encabezado exacto |
| Aviso de descripción de más de 500 caracteres | El requisito describe varios comportamientos | Divídelo en varios requisitos; los ejemplos deben ir en los escenarios |
| `Purpose` demasiado breve / `TBD` tras archivar | Capability nueva sin `## Purpose` en el delta | Añade una o dos frases (50 caracteres como mínimo). Si ya se archivó, edita la spec principal |
| Change sin deltas rechazado | El change no declara ninguna capability | Si realmente no cambia el comportamiento: `skip_specs: true` en `.openspec.yaml` |
| `Unknown item '<x>'` / ambigüedad | Un change y una spec tienen el mismo nombre, o el change ya está archivado | Usa `--type change` o `--type spec`; consulta `openspec list --archived` |

> Para analizar cómo interpreta OpenSpec los deltas: `openspec show <change> --json --deltas-only`.

## Flujo de trabajo

| Síntoma | Causa probable | Solución |
|---|---|---|
| `openspec list` no muestra ningún change | Se ejecuta fuera de la copia de trabajo (por ejemplo, en la raíz de este taller, que no es un proyecto de OpenSpec), o todos los changes ya están archivados | Sitúate en la copia de trabajo (`~/taller/mercaluz-data-platform`). `openspec list` solo muestra changes activos: usa `openspec list --specs` para las specs y `openspec list --archived` para los changes archivados |
| Al archivar, Claude pregunta si sincronizar (*Sync now* / *Archive without syncing*) | El delta crea o modifica una spec principal | Elige siempre **Sync now**. Si archivaste sin sincronizar, `openspec/specs/` queda incompleto: copia el `spec.md` del change archivado como spec principal o repite el change |
| La spec tiene muchos más requisitos de los pedidos | La IA divide cada detalle en un requisito o añade comportamientos que no se pidieron | Pide a Claude que los agrupe o elimine con `/opsx:update`. La regla de `config.yaml` "incluye solo los requisitos que pide la propuesta" lo reduce |
| `/opsx:propose` empieza a escribir código | No es el comportamiento esperado: el workflow está limitado a la planificación | Detén la ejecución e indica que solo debe planificar; comprueba que los comandos estén actualizados (`openspec update`) |
| `apply` implementa funcionalidades que no figuran en las specs | El contexto incluye la conversación de planificación | Ejecuta `/clear` antes de `/opsx:apply` |
| `apply` marca tareas como completadas con tests fallidos | Falta la regla de verificación | Añade en `config.yaml` → `operations.apply.guidance` la indicación "no marques la tarea si falla" |
| La IA no respeta las convenciones del equipo | Las convenciones no están documentadas en `config.yaml` | Añádelas a `context` o a `rules.<artefacto>` y compruébalo con `openspec instructions` |
| Al archivar se pierde un cambio de otra persona del equipo | Dos changes con MODIFIED sobre el mismo requisito | Actualiza el change con `/opsx:update` antes de archivar (anexo [OpenSpec en equipo](openspec-in-teams.md#changes-en-paralelo)) |
| `archive` advierte de tareas incompletas | `tasks.md` tiene casillas sin marcar | Completa las tareas o, si no son necesarias, elimínalas de `tasks.md` y justifica el motivo |

## Retomar el taller desde una sesión intermedia

Cada sesión parte del estado final de la anterior. Las soluciones de las sesiones 1 a 6 contienen **los artefactos de OpenSpec (proposal, specs, design y tasks), no código**. Para ponerte al día, copia los changes de las sesiones que te falten y deja que la IA los implemente.

Antes de empezar, completa la sesión 0 en tu copia de trabajo (`openspec init` y `config.yaml`). Después, guarda la ruta de la copia de trabajo en una variable; los comandos siguientes la utilizan y se ejecutan desde la raíz de este taller:

**Git Bash, macOS y Linux:**

```bash
REPO=~/taller/mercaluz-data-platform
```

**PowerShell:**

```powershell
$REPO = "$HOME\taller\mercaluz-data-platform"
```

**cmd:**

```bat
set REPO=%USERPROFILE%\taller\mercaluz-data-platform
```

Para cada sesión pendiente, en orden, copia su change. Por ejemplo, para la sesión 1:

**Git Bash, macOS y Linux:**

```bash
cp -r solutions/session-01/openspec/changes/add-orders-ingestion "$REPO/openspec/changes/"
```

**PowerShell:**

```powershell
Copy-Item -Recurse solutions\session-01\openspec\changes\add-orders-ingestion "$REPO\openspec\changes\"
```

**cmd:**

```bat
xcopy solutions\session-01\openspec\changes\add-orders-ingestion "%REPO%\openspec\changes\add-orders-ingestion\" /E /I /H /Y
```

Después, en Claude Code (abierto en la copia de trabajo), implementa y archiva el change:

```text
/opsx:apply add-orders-ingestion
/opsx:archive add-orders-ingestion
```

Repite el proceso con cada sesión, sustituyendo el número de sesión y el nombre del change:

| Sesión | Change |
|---|---|
| 1 | `add-orders-ingestion` |
| 2 | `add-order-lines` |
| 3 | `add-daily-sales` |
| 4 | `add-finance-export` |
| 5 | `add-data-quality-quarantine` |
| 6 | `make-orders-ingestion-idempotent` |

> Si tienes un change a medias en `openspec/changes/` de la sesión en la que te quedaste, elimínalo antes de copiar el de referencia.

## Empezar las sesiones avanzadas desde el código de referencia

Las sesiones 7 y 8 pueden hacerse sin haber completado el núcleo. [`solutions/advanced-start/`](../solutions/advanced-start/) contiene el repositorio completo al final de la sesión 6: código, tests, `config.yaml` y las specs principales. Cópialo en una carpeta nueva, desde la raíz de este taller:

**Git Bash, macOS y Linux:**

```bash
mkdir -p ~/taller
cp -r solutions/advanced-start ~/taller/mercaluz-advanced
cd ~/taller/mercaluz-advanced
```

**PowerShell:**

```powershell
New-Item -ItemType Directory -Force "$HOME\taller"
Copy-Item -Recurse solutions\advanced-start "$HOME\taller\mercaluz-advanced"
Set-Location "$HOME\taller\mercaluz-advanced"
```

**cmd:**

```bat
mkdir "%USERPROFILE%\taller"
xcopy solutions\advanced-start "%USERPROFILE%\taller\mercaluz-advanced\" /E /I /H
cd /d "%USERPROFILE%\taller\mercaluz-advanced"
```

A continuación, igual en todos los terminales, inicializa Git, comprueba que todo funciona y genera los comandos de OpenSpec para Claude Code (el idioma ya está definido en `openspec/config.yaml`):

```bash
git init
```

```bash
git add .
```

```bash
git commit -m "Start from the end of session 6"
```

```bash
uv sync
```

```bash
uv run pytest
```

```bash
openspec init --tools claude
```

## Reiniciar el taller desde el principio

Elimina la copia de trabajo y vuelve a copiar el repositorio original, desde la raíz de este taller:

**Git Bash, macOS y Linux:**

```bash
rm -rf ~/taller/mercaluz-data-platform
cp -r mercaluz-data-platform ~/taller/
```

**PowerShell:**

```powershell
Remove-Item -Recurse -Force "$HOME\taller\mercaluz-data-platform"
Copy-Item -Recurse mercaluz-data-platform "$HOME\taller\"
```

**cmd:**

```bat
rmdir /s /q "%USERPROFILE%\taller\mercaluz-data-platform"
xcopy mercaluz-data-platform "%USERPROFILE%\taller\mercaluz-data-platform\" /E /I /H
```

A continuación, repite la [sesión 0](../sessions/00-installation-and-setup.md#03-preparar-la-copia-de-trabajo-del-repositorio).

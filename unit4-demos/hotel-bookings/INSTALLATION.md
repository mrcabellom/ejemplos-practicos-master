# Instalación

Esta guía explica qué hay que instalar para trabajar en el proyecto y cómo
hacerlo en Windows, macOS y Linux. Los comandos se han contrastado con la
documentación oficial de cada herramienta en octubre de 2026; si alguno
falla, la referencia es la documentación enlazada.

## Qué hace falta

| | Obligatorio | Para qué |
| --- | --- | --- |
| Python 3.9 o superior | Sí; uv puede descargarlo | Todo el proyecto |
| uv | Recomendado, no obligatorio | Instalar Python y crear el entorno virtual |
| Git | Sí | Clonar el proyecto, crear ramas y worktrees y revisar cambios |
| Claude Code | Sí | El agente de código principal del equipo |
| Cuenta de GitHub y GitHub CLI (`gh`) | No; solo para el bloque opcional de la fase 6 | Instalar la app de Claude en GitHub con `/install-github-app` |
| GitHub Copilot, Cursor u OpenCode | No | Trabajar con otra herramienta de agentes |
| Node.js 22 o superior | Solo si se instala algo con npm | Copilot CLI u OpenCode por npm |

El proyecto no necesita paquetes de Python de terceros. `uv` tampoco es una
dependencia del proyecto: se usa solo para preparar el entorno.

---

## 1. Python y uv

La opción recomendada es instalar [uv](https://docs.astral.sh/uv/), que puede
descargar Python y crear el entorno virtual. Si no quieres usarlo, instala
Python por separado con las instrucciones de abajo.

**Windows (PowerShell)**

```powershell
winget install --id=astral-sh.uv -e
```

Si no tienes WinGet, usa el instalador oficial:

```powershell
irm https://astral.sh/uv/install.ps1 | iex
```

**macOS y Linux**

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

Abre un terminal nuevo después de instalarlo. **Comprobar:** `uv --version`.
Documentación: [instalación de uv](https://docs.astral.sh/uv/getting-started/installation/).

### Instalar Python sin uv

Sigue estos pasos solo si prefieres no usar uv:

**Windows**

```powershell
winget install Python.Python.3.12
```

O el instalador de [python.org](https://www.python.org/downloads/), marcando
*Add python.exe to PATH*.

> En un Windows recién instalado, escribir `python` puede abrir la Microsoft
> Store en lugar de ejecutar Python. Se desactiva en *Configuración ›
> Aplicaciones › Alias de ejecución de aplicaciones*, apagando los de
> `python.exe` y `python3.exe`. También funciona el lanzador `py`:
> `py -m venv .venv`.

**macOS**

```bash
brew install python@3.12
```

O el instalador de [python.org](https://www.python.org/downloads/macos/).

**Linux**

```bash
# Debian y Ubuntu
sudo apt install python3 python3-venv

# Fedora
sudo dnf install python3
```

> En Debian y Ubuntu, `venv` viene en un paquete aparte. Sin `python3-venv`,
> crear el entorno virtual falla con un mensaje sobre `ensurepip`.

**Comprobar:** `python3 --version` en macOS y Linux, `python --version` en
Windows.

---

## 2. Git

**Windows**

```powershell
winget install Git.Git
```

O el instalador de [git-scm.com](https://git-scm.com/downloads/win).

> En Windows, Git for Windows es **obligatorio** para este proyecto, no
> solo para Git. Instala también Git Bash, que Claude Code usa para ejecutar
> comandos. Sin él, Claude Code recurre a PowerShell, y los hooks del
> proyecto, escritos con sintaxis de Bash, no se ejecutarían correctamente.

**macOS**

```bash
xcode-select --install
```

O `brew install git`.

**Linux**

```bash
# Debian y Ubuntu
sudo apt install git

# Fedora
sudo dnf install git
```

**Comprobar:** `git --version`.

---

## 3. Claude Code

Requiere una suscripción de pago: el plan gratuito de Claude.ai no incluye
Claude Code. Funciona en macOS 13 o superior, Windows 10 versión 1809 o
superior y las distribuciones de Linux habituales.

**Windows (PowerShell)**

```powershell
irm https://claude.ai/install.ps1 | iex
```

Desde `cmd`:

```cmd
curl -fsSL https://claude.ai/install.cmd -o install.cmd && install.cmd && del install.cmd
```

**macOS y Linux**

```bash
curl -fsSL https://claude.ai/install.sh | bash
```

En macOS también con Homebrew: `brew install --cask claude-code`.

**Comprobar:**

```bash
claude --version
claude doctor
```

`claude doctor` revisa la instalación y la configuración. La primera vez que
se ejecuta `claude` pide iniciar sesión.

El plan de trabajo usa `/goal`, `claude agents` y `claude --bg`, que
necesitan **Claude Code v2.1.257 o posterior**. Si tu versión es anterior,
actualiza con `claude update`.

Abre `claude` una vez en la carpeta del repositorio y **acepta el diálogo
de confianza**. Sin él, Claude Code ignora los permisos y los hooks del
proyecto, y `/goal` no está disponible. Afecta sobre todo a `claude -p`,
que no muestra el diálogo.

Documentación: [code.claude.com/docs/en/setup](https://code.claude.com/docs/en/setup)

---

## 4. Herramientas opcionales

### GitHub Copilot

Requiere una suscripción a Copilot, incluido el plan gratuito.

**En VS Code**, que es como se usa en este proyecto:

| Sistema | Instalar VS Code |
| --- | --- |
| Windows | `winget install Microsoft.VisualStudioCode` |
| macOS | `brew install --cask visual-studio-code` |
| Linux | Paquete `.deb` o `.rpm` desde [code.visualstudio.com](https://code.visualstudio.com/download) |

Después, instalar la extensión *GitHub Copilot* desde el panel de extensiones
e iniciar sesión con la cuenta de GitHub. VS Code detecta `.vscode/mcp.json`
al abrir el repositorio.

**En el terminal (Copilot CLI)**, opcional:

| Sistema | Comando |
| --- | --- |
| Windows | `winget install GitHub.Copilot` |
| macOS y Linux | `brew install --cask copilot-cli` |
| Cualquiera, con Node.js 22+ | `npm install -g @github/copilot` |

En Windows, Copilot CLI requiere PowerShell 6 o superior.

Documentación: [docs.github.com/copilot](https://docs.github.com/en/copilot/how-tos/copilot-cli/set-up-copilot-cli/install-copilot-cli)

### Cursor

Se descarga desde [cursor.com/download](https://cursor.com/download), con
instalador para Windows, `.dmg` para macOS y paquete para Linux. Al abrir la
carpeta del repositorio, lee `.cursor/rules/`, `.cursor/mcp.json` y
`.cursor/hooks.json`.

### OpenCode

Necesita además una clave de API de algún proveedor de modelos, o
autenticarse con `/connect` dentro de la propia herramienta.

| Sistema | Comando |
| --- | --- |
| macOS y Linux | `curl -fsSL https://opencode.ai/install \| bash` |
| macOS y Linux, con Homebrew | `brew install anomalyco/tap/opencode` |
| Windows | `scoop install opencode` o `choco install opencode` |
| Cualquiera, con Node.js | `npm install -g opencode-ai` |

**Comprobar:** `opencode --version`.

Documentación: [opencode.ai/docs](https://opencode.ai/docs/)

### Node.js

Solo hace falta para las instalaciones por npm.

| Sistema | Comando |
| --- | --- |
| Windows | `winget install OpenJS.NodeJS.LTS` |
| macOS | `brew install node` |
| Linux | Desde [nodejs.org](https://nodejs.org/en/download) o el gestor de la distribución |

**Comprobar:** `node --version`.

---

## 5. Preparar el repositorio

Desde la carpeta del repositorio, usa una de estas opciones:

**Recomendada: uv**

Windows (PowerShell):

```powershell
uv venv
.venv\Scripts\Activate.ps1
```

macOS y Linux:

```bash
uv venv
source .venv/bin/activate
```

`uv venv` lee `.python-version` (3.12) y descarga esa versión si no está
instalada.

**Alternativa sin uv**

Windows (PowerShell):

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

macOS y Linux:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Con PowerShell, si la activación está bloqueada por la política de ejecución:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
```

Desde `cmd`, usa `.venv\Scripts\activate.bat`. Con `fish`, usa
`.venv/bin/activate.fish`.

Con el entorno activado, los comandos son los mismos en ambos casos:

```bash
python tasks.py setup
python tasks.py test
```

**Resultado esperado:** `setup` muestra la versión de Python y confirma que
no hacen falta paquetes externos; `test` ejecuta los tests del proyecto.

A partir de este punto, cualquier herramienta de agentes debe abrirse
**desde ese mismo terminal**, con el entorno activado.

---

## Problemas frecuentes

| Síntoma | Causa | Solución |
| --- | --- | --- |
| `python` abre la Microsoft Store | Alias de ejecución de Windows | Desactivarlos, o usar `py` |
| `uv` no se reconoce como comando | El terminal estaba abierto durante la instalación | Abrir un terminal nuevo o usar la alternativa sin uv |
| `ensurepip is not available` al crear el venv | Falta `python3-venv` en Debian o Ubuntu | `sudo apt install python3-venv` |
| `Activate.ps1 cannot be loaded` | Política de ejecución de PowerShell | `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass` |
| `python: command not found` en macOS o Linux | El entorno no está activado | `source .venv/bin/activate` |
| El servidor MCP no aparece en `/mcp` | La herramienta se abrió sin el entorno activado | Cerrarla, activar el entorno y volver a abrirla desde ese terminal |
| Los hooks no se ejecutan en Windows | Falta Git for Windows | `winget install Git.Git` y reiniciar el terminal |
| `claude: command not found` | El instalador no actualizó el `PATH` de la sesión | Cerrar y abrir el terminal |

# Demos de la Unidad 4

Dos proyectos de datos completos para trabajar con **Claude Code**. Cada uno tiene un plan de trabajo por fases en
`playbook/`.

| Carpeta | Caso | Qué se practica |
|---|---|---|
| [hotel-bookings](hotel-bookings/README.md) | **Hoteles Brisa**: el cuadro de dirección marca una ocupación del 112 % y el sistema de precios sube la tarifa | Modo plan, `/goal`, sesiones en paralelo con worktrees, permisos, skills, hooks, revisión automática y ejecución sin terminal |
| [data-transformation](data-transformation/README.md) | **Pedalia**: las entregas semanales de viajes de bicicleta compartida llegan con incidencias | Instrucciones y contexto, skills y subagentes, hooks y permisos, MCP y especificación, vigilancia con `/loop` |

## Antes de empezar

Los planes de trabajo crean ramas, commits y worktrees, y parten de la rama `main`. Por eso cada proyecto debe ser
**su propio repositorio Git**. Copia la carpeta del ejemplo fuera de este repositorio e inicializa Git en la copia.

**Git Bash, macOS y Linux** (con Hoteles Brisa como ejemplo):

```bash
mkdir -p ~/taller
cp -r hotel-bookings ~/taller/
cd ~/taller/hotel-bookings
```

**PowerShell:**

```powershell
New-Item -ItemType Directory -Force "$HOME\taller"
Copy-Item -Recurse hotel-bookings "$HOME\taller\"
Set-Location "$HOME\taller\hotel-bookings"
```

Después, en cualquier terminal:

```bash
git init -b main
```

```bash
git add -A
```

```bash
git commit -m "Initial commit"
```

A partir de aquí, sigue el README del proyecto. Para Pedalia, sustituye `hotel-bookings` por `data-transformation`.

La instalación de Git, uv y el editor está en el [README principal](../README.md#instalación). Hoteles Brisa tiene
además una guía propia, [INSTALLATION.md](hotel-bookings/INSTALLATION.md), con Claude Code y las herramientas
opcionales.

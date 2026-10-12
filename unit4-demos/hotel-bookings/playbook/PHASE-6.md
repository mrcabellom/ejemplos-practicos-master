# Fase 6 — Ejecución sin terminal y cierre de INC-0142

**Objetivo:** ejecutar Claude Code desde scripts y de forma programada, y
cerrar la incidencia: integrar el arreglo, reprocesar el almacén con
autorización y responder a Revenue. Por último, ver cómo se comprueba el
cambio en GitHub.

**Punto de partida:** el bloque común del [índice](README.md).

---

## Bloque 0 · Confianza de la carpeta

Sin terminal no aparece el diálogo de confianza. Si la carpeta no es de
confianza, Claude Code **ignora las reglas `allow` de
`.claude/settings.json`**, los hooks y `/goal`, y el agente no puede
ejecutar ni siquiera los tests.

Basta con abrir `claude` una vez en el repositorio y aceptar el diálogo.

---

## Bloque 1 · `claude -p` desde un script

```powershell
$r = claude -p "/validate-pipeline" --output-format json | ConvertFrom-Json
$r.result
"{0} turnos, {1:N2} USD" -f $r.num_turns, $r.total_cost_usd
```

En macOS y Linux, con `jq`:

```bash
claude -p "/validate-pipeline" --output-format json | jq -r '.result, .total_cost_usd'
```

Es el mismo skill de siempre, ahora como un paso más de un script. Dos
opciones habituales:

| Opción | Para qué sirve |
| --- | --- |
| `--max-turns 5` | Limitar el trabajo del agente |
| `--permission-mode acceptEdits` | Permitir ediciones; los permisos `ask` siguen sin concederse |

Sin nadie que apruebe, todo lo que está en `ask` **se deniega**:

```powershell
claude -p "Ejecuta python tasks.py run-all" --output-format json | ConvertFrom-Json | Select-Object -ExpandProperty result
```

Resultado esperado: el agente indica que no ha podido ejecutarlo. Sin una
persona que lo autorice, el almacén no se carga.

---

## Bloque 2 · Ejecución programada

| | Dónde se ejecuta | Cuándo | Uso |
| --- | --- | --- | --- |
| `/loop` | En la sesión, en la máquina local | En cada intervalo, mientras la sesión siga abierta | Vigilancia durante un periodo concreto |
| `/schedule` | En la nube | Según un horario, aunque la máquina esté apagada | Tareas recurrentes del equipo |
| Workflow con `schedule:` | En GitHub Actions | Según una expresión `cron` | Informes en el repositorio |

Las dos últimas opciones se ejecutan fuera de la máquina local, así que
necesitan el repositorio en un servicio accesible, normalmente GitHub.
`/loop` solo necesita la sesión.

Sin prompt, `/loop` usa [`.claude/loop.md`](../.claude/loop.md), que
reconcilia el almacén y se limita a informar:

```text
/loop 10m
```

`Esc` lo detiene. Como reflexión: ¿cuál de las tres opciones serviría
para avisar cada mañana de que el almacén ha perdido el grain, y quién
debería recibir el aviso?

---

## Bloque 3 · Cierre de INC-0142

### Preparar el arreglo

Un agente genera el arreglo de la carga con la condición completa de la
fase 2:

```powershell
git switch -c fix/inc-0142
claude -p "/goal python tasks.py acceptance termina con código 0 y python tasks.py test pasa entero, con al menos un test nuevo en tests/. Solo cambian src/pipeline/load.py y tests/. Sin lanzar run, run-all ni reset. Para tras 15 turnos." --permission-mode acceptEdits
git add src tests
git commit -m "Fix INC-0142: one row per booking, latest updated_at wins"
```

Antes de continuar, se revisa el diff. Si se conservó una rama de la fase 2
o de la 5, puede usarse en su lugar.

### Integrar el arreglo

```powershell
git switch main
git merge --no-ff fix/inc-0142
python tasks.py acceptance
```

Resultado esperado: los cinco criterios en verde. Sin embargo:

```powershell
python tasks.py check
```

La comprobación sigue fallando, porque el almacén se construyó con el
código anterior.

### Reprocesar con autorización

```text
Según docs/runbooks/backfill.md, ¿qué hay que hacer para que el almacén refleje el código nuevo? No lo ejecutes.
```

```text
Autorizado. Ejecuta el procedimiento del runbook y verifica el resultado.
```

Claude pide confirmación para `reset` y para cada carga, porque están en
`ask`. Ningún objetivo, skill ni script del plan de trabajo se ha saltado
esa confirmación.

```powershell
python tasks.py check
python tasks.py occupancy
```

Resultado esperado: `check` en verde por primera vez y Málaga al 88 % la
noche del 2 de marzo.

### Responder a Revenue

```text
Añade a docs/tickets/INC-0142.md una sección "Cierre" con los comandos que hemos ejecutado y su resultado, y después una respuesta para Marta, de Revenue, en menos de diez líneas y sin jerga técnica: qué pasaba, qué cifras estaban mal (con el valor erróneo y el correcto) y qué se ha cambiado.
```

Si el skill `close-ticket` de la fase 4 está disponible,
`/close-ticket INC-0142` puede generar la sección "Cierre".

La respuesta debe incluir, como mínimo: Málaga el 2 de marzo, del 112 % al
88 %; Málaga el 3 de marzo, del 100 % al 75 %; y Madrid el 2 de marzo, del
70 % al 40 %.

---

## Bloque 4 · Comprobación en GitHub

Todo lo anterior se ha hecho en local. En el flujo habitual del equipo, el
cambio llega a GitHub y allí se vuelve a comprobar.

### Integración continua

El repositorio incluye un workflow en
[`.github/workflows/ci.yml`](../.github/workflows/ci.yml), que se ejecuta
en GitHub Actions cuando los cambios llegan al repositorio remoto. No forma
parte del trabajo local.

Antes de ver su resultado:

1. ¿Qué pasos ejecuta y en qué orden?
2. Con `main` antes del arreglo, ¿qué paso falla primero?
3. Con el arreglo integrado, ¿se completan todos los pasos?

El workflow **no usa ningún agente**: ejecuta los mismos comandos que se
usan en local. Las comprobaciones importantes no dependen de que un agente
decida hacerlas.

### Opcional · Claude Code en GitHub

Requiere una cuenta de GitHub, una copia propia del repositorio, permisos
de administración y la [GitHub CLI](https://cli.github.com) autenticada con
`gh auth login`.

```text
/install-github-app
```

Este comando instala la app de Claude en el repositorio, guarda la
credencial como secreto y prepara un pull request con el workflow, que
después se integra. A continuación, en GitHub:

1. Se abre una issue con el texto de [BRI-204](../docs/tickets/BRI-204.md).
2. Se añade el comentario `@claude resuelve esta issue y abre un pull request`.
3. Claude responde en la issue, trabaja en el runner y abre el pull request.
4. La integración continua se ejecuta sobre ese pull request.

> Cada ejecución consume minutos de GitHub Actions y tokens. Para
> limitarla, se puede añadir `claude_args: "--max-turns 10"` al workflow.

---

## Ampliaciones opcionales

Ninguna es necesaria para cerrar la incidencia.

| Ampliación | Pista |
| --- | --- |
| La cuarentena crece con cada recarga | ¿Qué grain debería tener? Hay que definirlo primero en el contrato. |
| La reserva `B-3011` está en dólares | Es una reserva real que no cuenta en la ocupación. La decisión corresponde a negocio. |
| El informe no muestra las noches vacías | Una consulta con una fila por hotel y noche, haya reservas o no: 15 filas del 1 al 5 de marzo. |

Para cualquiera de ellas, el camino es el mismo: un criterio nuevo en el
oráculo, un `/goal` y la revisión de la fase 5.

---

## Resumen del plan de trabajo

| Fase | Qué se delega | Qué decide una persona |
| --- | --- | --- |
| 2 | El arreglo, hasta cumplir una condición | La condición y el oráculo |
| 3 | Cuatro tickets a la vez | El reparto, los permisos y la integración |
| 4 | Parte de la configuración | Qué se incorpora a la del equipo |
| 5 | La revisión | Qué hallazgos son reales y si el cambio se integra |
| 6 | La ejecución sin terminal | Las autorizaciones |

---

## Qué hacer si se desvía

| Situación | Respuesta |
| --- | --- |
| `claude -p` no puede ejecutar nada | La carpeta no es de confianza: ver el bloque 0. |
| `check` sigue en rojo tras integrar | Falta el reproceso: el código está corregido, pero los datos no. |
| El agente lanza el reproceso sin preguntar | No es posible: `reset` y las cargas están en `ask`. Si se aceptó, conviene revisarlo. |
| `/install-github-app` no encuentra el repositorio | Solo funciona con remotos de github.com y necesita `gh` autenticado. |
| `@claude` no responde | Comprobar que el workflow está en `main`, que existe el secreto y que se tiene permiso de escritura. |

# Fase 2 — `/goal` y el oráculo

**Objetivo:** que Claude Code resuelva INC-0142 sin intervención,
encadenando turnos hasta cumplir una condición comprobable, y entender qué
garantiza esa condición y qué no.

**Punto de partida:** el bloque común del [índice](README.md).

---

## Bloque 0 · El oráculo

```powershell
python tasks.py acceptance
```

```
Acceptance check for INC-0142
-----------------------------
  [FAIL] One row per booking after loading the three extracts
  [FAIL] Loading an extract again leaves fct_bookings unchanged
  [FAIL] An older version loaded last does not overwrite a newer one
  [FAIL] No night exceeds the hotel capacity
  [FAIL] Occupancy on 2 March matches the contract
```

El oráculo comprueba cinco criterios del contrato sobre almacenes
temporales. Como no modifica `warehouse.db`, puede ejecutarse tantas veces
como haga falta, y está incluido en `allow`, así que el agente no pide
permiso para lanzarlo.

Para usarlo no es necesario conocer el negocio: **si está en verde, la
incidencia está resuelta en el código**.

En Claude Code:

```text
Cambia src/pipeline/acceptance.py para que el criterio de ocupación acepte 9/8.
```

Resultado esperado: el hook `protect_source.py` bloquea el cambio. Si el
agente pudiera editar el oráculo, podría poner el objetivo en verde sin
corregir nada. **Un objetivo solo es tan fiable como su comprobación.**

---

## Bloque 1 · Las partes de una condición

`/goal` fija una condición. Al terminar cada turno, otro modelo, el
evaluador, lee la conversación y emite un veredicto: **no cumplida**
(Claude continúa), **cumplida** (termina) o **imposible** (abandona).

El evaluador **no ejecuta comandos ni abre archivos**: solo juzga lo que
aparece en la conversación. Por eso, la condición debe indicar cómo se
demuestra que se cumple.

| Parte | En este caso |
| --- | --- |
| Estado final medible | `python tasks.py acceptance` termina con código 0 |
| Forma de comprobarlo | La salida del oráculo y de los tests aparece en la conversación |
| Lo que no puede cambiar | `data/`, `acceptance.py`, `reconcile.py` y `occupancy.py`; tampoco se reprocesa el almacén |
| Límite | 15 turnos |

Antes de continuar, conviene redactar la condición en una línea para
compararla después con la del bloque 2.

---

## Bloque 2 · El objetivo

```powershell
git switch -c fix/inc-0142
claude --permission-mode acceptEdits
```

Con `acceptEdits`, Claude edita archivos y ejecuta lo que está en `allow`
sin pedir confirmación. El resto, como `run-all` o `reset`, sigue
requiriéndola. Si la cuenta dispone del modo auto, también sirve.

```text
/goal Pasa python tasks.py acceptance y python tasks.py test. No cambies data/ ni src/pipeline/acceptance.py, src/pipeline/reconcile.py o src/pipeline/occupancy.py. No ejecutes run, run-all ni reset. Máximo: 15 turnos.
```

Al fijar el objetivo empieza el primer turno, sin necesidad de otro
prompt. Mientras se ejecuta:

- El indicador `◎ /goal active` muestra el tiempo transcurrido.
- Cada veredicto del evaluador aparece en la conversación; **Ctrl+O**
  muestra su justificación.
- `/goal` sin argumentos muestra la condición, los turnos, los tokens
  consumidos y la última justificación.

Resultado de referencia: **un turno, menos de un minuto y unos 0,20 $**,
con cambios únicamente en `src/pipeline/load.py`. Otras ejecuciones pueden
necesitar más turnos; si se alcanza el límite, `/goal` muestra el estado.

Lo que el evaluador ha dado por bueno se comprueba en el terminal:

```powershell
python tasks.py acceptance
python tasks.py test
git diff --stat
```

---

## Bloque 3 · Lo que la condición no especificaba

Con el diff completo a la vista (`/diff` o `git diff`):

1. ¿Se ha añadido algún test? La condición no lo exigía, y el resultado
   cambia de una ejecución a otra: unas veces se añaden tests y otras no.
2. ¿Ha cambiado algo más que la carga de `fct_bookings`? En algunas
   ejecuciones también se modifica la cuarentena para no repetir rechazos,
   algo que nadie había pedido.
3. ¿El docstring de `load()` explica qué ocurre al cargar dos veces el
   mismo extracto? Lo exige `.claude/rules/pipeline.md`.

**`/goal` garantiza la condición escrita, no la intención de quien la
escribe.** Lo que no se especifica queda a criterio del agente.

Se descarta el cambio y se repite con una condición más precisa:

```powershell
git restore src tests
```

```text
/goal Pasa python tasks.py acceptance y python tasks.py test. Añade un test que falle con load.py de main y pase con el nuevo. Cambia solo src/pipeline/load.py y tests/; conserva el registro de cada rechazo en cuarentena. No ejecutes run, run-all ni reset. Máximo: 15 turnos.
```

Se comparan los dos diffs y se hace commit del segundo.

---

## Bloque 4 · Lo que `/goal` no hace

```powershell
python tasks.py reconcile
```

Con el almacén cargado, la reconciliación sigue fallando: 11 filas para 8
reservas. El código está corregido, pero los datos no. Reprocesar el
almacén es una decisión distinta, con su propio runbook y su propia
autorización, y la condición la excluía de forma expresa.

Para comprobarlo:

```text
/goal Pasa python tasks.py check. Máximo: 5 turnos.
```

Para que `check` pase hacen falta `reset` y `run-all`, que están en `ask`,
así que Claude pide permiso: **un objetivo no amplía los permisos**.
Concederlo o no es una decisión de la persona, y conviene observar cómo
reacciona el evaluador.

---

## Bloque 5 · Del objetivo a una regla permanente

`/goal` solo dura una sesión. Su equivalente permanente es un hook `Stop`,
que se ejecuta cada vez que Claude va a terminar un turno.

| | `/goal` | Hook `Stop` de tipo `command` |
| --- | --- | --- |
| Quién decide | Un modelo que lee la conversación | Un script que ejecuta el oráculo |
| Qué puede engañarlo | Una salida que parece correcta sin serlo | Nada: solo cuenta que el oráculo pase |
| Duración | La sesión | Mientras siga en la configuración |

El hook se crea en la configuración local, no en la del equipo:

```text
Crea un hook Stop en .claude/settings.local.json que ejecute python tasks.py acceptance y, si falla, devuelva código 2 con la salida en stderr para que sigas trabajando. Comprueba stop_hook_active para no entrar en un bucle.
```

El script se revisa antes de aceptarlo y se comprueba en `/hooks`. Después
se **elimina**: mientras el oráculo esté en rojo, bloquearía cualquier
sesión que no trabaje en INC-0142.

---

## Opcional · Sin terminal

`/goal` también funciona en modo no interactivo:

```powershell
claude -p "/goal Pasa python tasks.py acceptance. Máximo: 15 turnos." --permission-mode acceptEdits
```

Si la carpeta no es de confianza, Claude Code ignora las reglas `allow` de
`.claude/settings.json` y no puede ejecutar ni siquiera los tests. Basta
con abrir `claude` una vez en la carpeta y aceptar el diálogo de confianza.
Este punto se retoma en la fase 6.

---

## Cierre

| Pregunta | Respuesta |
| --- | --- |
| ¿Quién decide que se ha terminado? | Un evaluador distinto del agente, a partir de la conversación |
| ¿Qué garantiza? | Lo que dice la condición, y nada más |
| ¿Cómo se impide que el agente altere la comprobación? | Protegiendo el oráculo con un hook |
| ¿Amplía los permisos? | No: lo que está en `ask` sigue pidiendo confirmación |

---

## Qué hacer si se desvía

| Situación | Respuesta |
| --- | --- |
| `/goal` no está disponible | La carpeta no es de confianza o los hooks están desactivados. Abrir `claude` y aceptar el diálogo. |
| Claude intenta editar `acceptance.py` | El hook lo bloquea. Es el comportamiento esperado. |
| Pide permiso para `run-all` o `reset` | Rechazarlo: la condición los excluía. El arreglo se comprueba con el oráculo. |
| Se detiene con el objetivo activo | Llevaba varios turnos sin usar herramientas. Un mensaje lo reanuda; `/goal clear` lo elimina. |
| El evaluador da el objetivo por cumplido, pero el oráculo falla | La conversación mostraba algo que parecía correcto. Ejecutar el oráculo en el terminal y precisar la condición. |
| Usa `DISTINCT` o filtra el informe | `AGENTS.md` lo prohíbe y el oráculo lo detecta: la tabla sigue teniendo duplicados. |

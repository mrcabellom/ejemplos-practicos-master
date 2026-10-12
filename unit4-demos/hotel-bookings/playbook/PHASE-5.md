# Fase 5 — Revisión automática

**Objetivo:** decidir si un arreglo escrito por un agente puede
integrarse en `main`. La decisión se apoya en cuatro preguntas sobre el
mismo cambio, cada una respondida por un revisor distinto.

**Punto de partida:** el bloque común del [índice](README.md).

---

## Contexto

INC-0142 se ha corregido con un `/goal` poco exigente, que solo pedía que
pasaran el oráculo y los tests. El oráculo está en verde, pero antes de
integrar el cambio hay que revisarlo.

| Pregunta | Revisor |
| --- | --- |
| 1. ¿Es correcto? | `/code-review` |
| 2. ¿Respeta el contrato de datos? | El subagente `data-quality-reviewer` |
| 3. ¿Es seguro? | Una revisión de seguridad mediante un prompt |
| 4. ¿Está limpio? | `/simplify` |

Con las cuatro respuestas, la decisión final corresponde a una persona.

---

## Bloque 0 · El cambio que se revisa

```powershell
git switch -c review/inc-0142
claude -p "/goal python tasks.py acceptance termina con código 0 y python tasks.py test pasa entero. Para tras 10 turnos." --permission-mode acceptEdits
git add -A
git commit -m "Fix INC-0142 (agent, loose goal)"
python tasks.py acceptance
```

Resultado esperado: los cinco criterios en `PASS`. Si se conservó el
primer arreglo de la fase 2, también sirve.

---

## Bloque 1 · Revisión propia

```text
/diff
```

Antes de lanzar ningún revisor, se anotan **dos observaciones** propias
para compararlas al final con las de los revisores.

Una pista: la condición no delimitaba qué podía cambiar ni exigía tests.

---

## Bloque 2 · ¿Es correcto?

```text
/code-review main
```

Busca errores de corrección en el diff respecto a `main`. Cada hallazgo se
clasifica como **real**, **falso positivo** o **cuestión de estilo**.

La opción `--fix` no se usa: lo que se aplica se decide en el bloque 5.

---

## Bloque 3 · ¿Respeta el contrato?

`/code-review` no conoce el contrato de datos; el subagente del proyecto,
sí:

```text
@agent-data-quality-reviewer revisa el diff de review/inc-0142 frente a main contra docs/data-contracts/fct_bookings.md.
```

El contrato establece que cada fila rechazada se escribe en `quarantine`
**con su `run_id`**. Con una condición como la del bloque 0, es habitual
que el agente cambie también la carga para no repetir rechazos. ¿Ha
ocurrido en este caso? ¿Lo detecta este revisor? ¿Lo detectó
`/code-review`?

---

## Bloque 4 · ¿Es seguro?

```text
Revisa la seguridad del diff de review/inc-0142 frente a main: inyección SQL, datos que se exponen, escrituras que no deberían ocurrir y entradas sin validar. Para cada punto, di qué has mirado y qué has encontrado. No cambies nada.
```

El arreglo solo afecta a la carga y usa consultas parametrizadas, así que
lo habitual es que no haya hallazgos. **Un informe sin hallazgos también
es un resultado**, siempre que indique qué se ha revisado; por eso el
prompt lo exige.

> En un repositorio con remoto `origin`, `/security-review` hace esta misma
> revisión con un procedimiento estándar.

---

## Bloque 5 · Decidir, corregir y limpiar

La tabla reúne las observaciones del bloque 1 y los hallazgos de cada
revisor:

| Hallazgo | Revisor | ¿Es real? | ¿Se aplica? |
| --- | --- | --- | --- |
| | | | |

Solo se aplica lo que se haya marcado:

```text
Aplica solo estos hallazgos: <lista>. Después ejecuta python tasks.py acceptance y python tasks.py test.
```

Queda la cuarta pregunta, **¿está limpio?**:

```text
/simplify
```

Cuatro agentes revisan en paralelo la reutilización, la simplicidad, la
eficiencia y el nivel de abstracción, y **aplican** las mejoras. Por eso
es el último paso: limpia lo que ya se ha decidido incorporar. A
continuación:

```powershell
python tasks.py acceptance
python tasks.py test
git diff
```

Si algo deja de pasar, `git restore` lo deshace.

---

## Bloque 6 · Decisión

En una frase: **¿se integra `review/inc-0142` en `main`?** Si la respuesta
es no, ¿qué falta?

| Revisor | Pregunta | Conoce el contrato | Modifica el código |
| --- | --- | --- | --- |
| Revisión propia, con `/diff` | Todas | Sí | No |
| `/code-review` | ¿Es correcto? | No | Solo con `--fix` |
| `data-quality-reviewer` | ¿Respeta el contrato? | Sí | No |
| Prompt de seguridad | ¿Es seguro? | No | No |
| `/simplify` | ¿Está limpio? | No | Sí |

Ningún revisor sustituye al conocimiento del contrato. El que lo conoce es
el que detecta lo que importa para el negocio.

---

## Qué hacer si se desvía

| Situación | Respuesta |
| --- | --- |
| `/code-review` no encuentra nada | Comprobar que revisa el diff correcto, con `main` como base. |
| La revisión de seguridad no indica qué ha revisado | Pedírselo: sin esa información, «sin hallazgos» no aporta nada. |
| El subagente responde **Falta evidencia** | No hay almacén para el MCP. Es correcto: debe revisar el código e indicar qué faltó. |
| `/simplify` rompe un test | Deshacer con `git restore` y aplicar solo lo que se entienda. |
| Un revisor propone cambiar `acceptance.py` | El hook lo impide. El oráculo solo lo cambia una persona. |

# Fase 4 — Hooks y permisos

**Objetivo:** resolver [OPS-104](../docs/tickets/OPS-104.md) sin tomar el
atajo que propone el ticket, y clasificar cada protección del repositorio.

**Punto de partida:**

```powershell
python tasks.py deliver 4
python tasks.py pipeline
```

Debe verse: `week-4.csv: 40% rechazado (4 de 10)`.

---

## Bloque 1 · El estado tenía la respuesta

```text
/clear
```

```text
Lee docs/tickets/OPS-104.md, docs/plans/status.md y output/rejected.csv.
¿Por qué Sol no tiene salidas?
```

El aviso anotado en la fase 2 lo explica: Sol se llama ahora Puerta del
Sol. **Es el dato que se perdió con `/clear` y se salvó por escrito.**
Compara con el punto 2 de `docs/plans/predictions.md`.

---

## Bloque 2 · El atajo, y el hook que lo bloquea

```text
Es urgente: haz lo que propone el ticket y cambia "Puerta del Sol" por
"Sol" en inbox/week-4.csv.
```

Lo probable es que se niegue citando `AGENTS.md`: eso es una instrucción.
Si lo intenta, `.claude/hooks/protect_inbox.py` sale con código `2` y la
edición no se hace.

Sin agente:

```powershell
'{"tool_input":{"file_path":"inbox/week-4.csv"}}' | python .claude\hooks\protect_inbox.py
$LASTEXITCODE
```

Esperado: `Bloqueado: ...` y `2`. Con `src/bikes/rules.py`, `0`. `/hooks`
lista los activos.

La forma correcta:

```text
Haz que "Puerta del Sol" se trate como la estación Sol del catálogo, en
rules.py. Primero el test. No cambies el contrato. Termina con
/check-delivery.
```

Esperado: `Ran 12 tests` y **Cumple**.

---

## Bloque 3 · El límite de un hook

`.claude/hooks/block_delete.py` solo mira el **texto** del comando:

```powershell
'{"tool_input":{"command":"Remove-Item output/trips.csv"}}' | python .claude\hooks\block_delete.py
$LASTEXITCODE
'{"tool_input":{"command":"python tasks.py reset"}}' | python .claude\hooks\block_delete.py
$LASTEXITCODE
```

`2` y `0`. Pero `reset` también borra `output/`, dentro del script, donde el
hook no mira. **Un hook evita accidentes; no es una barrera de seguridad.**

---

## Bloque 4 · Permisos

`.claude/settings.json`: `allow` y `deny`. `deny` gana siempre.

```text
Ejecuta python tasks.py deliver 5.
```

Denegado: las entregas las envía el operador, no el agente.

```powershell
python tasks.py sample-env
```

```text
Lee el archivo .env.
```

Denegado por `Read(./.env)`.

```text
Ejecuta: python -c "print(open('.env').read())"
```

Pide permiso; si se acepta, lo lee. **`deny` sobre `Read` no impide que un
proceso hijo abra el archivo.** Para eso hace falta aislamiento (sandbox).

```powershell
Remove-Item .env
```

| Capa | En este repositorio | ¿Bloquea? |
| --- | --- | --- |
| Instrucción | `AGENTS.md`: no tocar `inbox/` | No, guía |
| Hook | `protect_inbox.py` | Sí, la edición |
| Permiso | `deny: Read(./.env)` | Sí, la herramienta `Read` |
| Aislamiento | Sandbox | Sí, también procesos hijo |

---

## Cierre

```text
Completa docs/tickets/OPS-104.md: por qué no se corrigió el fichero del
operador y qué se cambió en su lugar. Actualiza docs/plans/status.md.
```

```powershell
git add docs src tests inbox
git commit -m "OPS-104: Puerta del Sol como Sol"
```

---

## Qué hacer si se desvía

| Situación | Respuesta |
| --- | --- |
| Se niega sin intentar editar | Eso prueba la instrucción; usa la prueba directa del hook. |
| `python` no se encuentra en el hook | Abre `claude` desde el terminal con el entorno activado. |
| Quiere añadir «Puerta del Sol» al contrato | El contrato no se cambia sin una persona. |

Comandos: `/hooks`, `/permissions`.

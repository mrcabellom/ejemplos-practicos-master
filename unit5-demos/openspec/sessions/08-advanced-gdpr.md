# Sesión 8 (avanzada) · Explorar antes de proponer: datos personales y RGPD

**Resultado:** uso de `/opsx:explore` para decidir *qué* hacer cuando la solución no está clara, conversión del análisis en un change e identificación de un impacto entre capabilities que no se había detectado.

**Conceptos nuevos:** `/opsx:explore`, paso de la exploración a la propuesta, revisión por perfiles no técnicos (DPO) y un change que modifica varias capabilities.

**Punto de partida:** el repositorio al final de la sesión 6 (o de la 7), o el código de referencia de [`solutions/advanced-start/`](../solutions/advanced-start/).

---

## 8.1 La auditoría

> **De:** Andrés (DPO)
> **Asunto:** Hallazgo RGPD: emails de clientes en silver
>
> En la revisión interna hemos detectado que `silver.order_lines` contiene `customer_email` en claro y que
> unas 40 personas de BI tienen acceso a esa tabla sin necesitarlo para su trabajo. Esta situación es contraria
> al principio de minimización. Necesito una propuesta antes de la auditoría externa de diciembre.
>
> Importante: el informe "Clientes recurrentes" debe seguir funcionando.

En este caso **todavía no está claro qué hay que construir**: ¿eliminar el email?, ¿aplicarle un hash?, ¿cifrarlo?, ¿qué ocurre con bronze? Es el momento de utilizar `/opsx:explore`.

## 8.2 `/opsx:explore`: análisis sin compromiso

Explore es un **modo de trabajo**, no un flujo: la IA lee el código y las specs, compara opciones y elabora diagramas, pero **no escribe código**. Si se le pide que implemente, remite a `/opsx:propose`.

```text
/clear
/opsx:explore

La DPO nos pide quitar customer_email en claro de silver (RGPD, minimización). El informe de
"Clientes recurrentes" de BI necesita seguir contando clientes distintos y su recurrencia.
¿Qué opciones tenemos? Revisa las specs actuales y dime qué capabilities se verían afectadas.
```

### Conceptos básicos sobre hashes

- **Minimización (RGPD):** solo deben tratarse los datos personales imprescindibles. BI necesita saber si dos pedidos pertenecen al **mismo** cliente, no **quién** es.
- **Seudonimización:** sustituir el email por un código que permita distinguir clientes sin revelar su identidad.
- **Hash (SHA-256):** función que transforma un texto en un código de longitud fija. El mismo email produce siempre el mismo código, y el proceso no puede invertirse mediante una fórmula. Sin embargo, es posible calcular el hash de millones de emails habituales (`nombre.apellido@...`) y buscar coincidencias: es lo que se conoce como **ataque por diccionario**.
- **HMAC:** hash que utiliza además una **clave secreta**. Sin la clave no es posible calcular los códigos, por lo que el ataque por diccionario deja de ser viable. Puede entenderse como un hash protegido con contraseña.

### Ejemplo de conversación (ilustrativo)

> **IA:** He revisado `openspec/specs/`. El email aparece de forma explícita en `order-lines` (columna `customer_email`).
> Hay además otra ubicación menos evidente: `data-quality` → "Tabla de cuarentena" guarda **"todas sus columnas
> de bronze"**, por lo que la cuarentena también contiene emails en claro.
>
> Opciones:
>
> | Opción | ¿Permite medir recurrencia? | ¿Reversible? | Infraestructura nueva |
> |---|---|---|---|
> | Eliminar la columna | No | — | No |
> | SHA-256 sin clave | Sí | **Sí, mediante diccionario** (los emails son predecibles) | No |
> | HMAC-SHA256 con clave secreta | Sí | No, sin la clave | Un secreto |
> | Tokenización con bóveda | Sí | Sí, de forma controlada | Un servicio |
>
> **Tú:** La DPO descarta SHA-256 sin clave, y la bóveda es desproporcionada para este caso. ¿Qué hacemos con bronze?
>
> **IA:** Bronze es una copia literal que necesitáis para reprocesar (sesión 6). Una opción es conservar el
> email en bronze solo durante N días y después ponerlo a NULL. ¿Qué margen de reprocesamiento necesitáis?
>
> **Tú:** Un mes como máximo.
>
> **IA:** Entonces, 30 días. Riesgo: reprocesar datos de más de 30 días dejará `customer_key` a NULL. Además,
> si la clave se pierde o se rota, cambiarán todos los `customer_key`, por lo que necesitáis una copia de
> seguridad de la clave y un procedimiento de rotación documentado. ¿Lo convierto en un change?

Qué ha ocurrido en esta conversación:

- **La spec de una sesión anterior ha revelado un impacto oculto**: la cuarentena (sesión 5) también almacena datos personales. Una búsqueda como `grep customer_email openspec/specs` **no lo detecta**, porque la spec indica "todas sus columnas de bronze". Las specs deben **leerse**, no solo consultarse mediante búsquedas.
- Las decisiones (HMAC, 30 días, clave de al menos 32 caracteres) se han tomado **durante el análisis**, antes de redactar ningún artefacto.

## 8.3 De la exploración al change

Cuando las decisiones estén acordadas:

```text
Sí, captúralo como un change: pseudonymize-customer-email.
```

O, si se prefiere empezar desde cero con un resumen:

```text
/opsx:propose pseudonymize-customer-email

Basado en la exploración: sustituir customer_email por customer_key (HMAC-SHA256 con clave en
MERCALUZ_PII_KEY, mínimo 32 caracteres; fallar si falta). Aplicarlo en silver.order_lines y en la
cuarentena. En bronze, poner a NULL customer_email con más de 30 días. La clave nunca en logs.
Capability nueva pii-protection + MODIFIED en order-lines y data-quality.
En design.md, documenta las 4 alternativas analizadas y por qué se descartan.
```

Estructura esperada:

```
openspec/changes/pseudonymize-customer-email/
├── proposal.md
├── specs/
│   ├── pii-protection/spec.md   ← NUEVA: seudonimización, clave obligatoria, retención en bronze
│   ├── order-lines/spec.md      ← MODIFIED: customer_email → customer_key
│   └── data-quality/spec.md     ← MODIFIED: la cuarentena tampoco guarda el email
├── design.md                    ← las 4 alternativas y la justificación de HMAC
└── tasks.md
```

> Este change modifica requisitos creados en las sesiones 2 y 5. Las specs evolucionan con cada change, igual que el código.

## 8.4 Revisión por parte de la DPO

Andrés no revisa código Python. Se le envían **tres ficheros**:

| Fichero | Qué valida la DPO |
|---|---|
| `proposal.md` | Que el apartado *Why* describe correctamente el hallazgo y que *Impact* incluye todas las tablas con datos personales |
| `specs/pii-protection/spec.md` | Que "ninguna columna de silver o gold contiene un email en claro" figura como requisito, con su escenario |
| `design.md` → Decisions y Risks | Que se descartó SHA-256 sin clave y que el rollback **no recupera** los emails eliminados de bronze |

Lista de comprobación técnica para el equipo:

- [ ] ¿Hay un escenario que compruebe que la clave **no aparece en la salida**?
- [ ] ¿Se normaliza el email (minúsculas, sin espacios) **antes** de calcular el HMAC? De lo contrario, `Ana@x.com` y `ana@x.com` se tratarían como clientes distintos.
- [ ] ¿La retención se calcula con `_ingested_at` (fecha de llegada) y no con `order_ts`?
- [ ] ¿Los escenarios de 29 y 31 días permiten un test determinista? (El test debe controlar la fecha actual.)
- [ ] En `.env.example`, ¿la clave de prueba es claramente **ficticia**?

```bash
openspec validate pseudonymize-customer-email --strict
```

Compara con [`solutions/session-08/`](../solutions/session-08/openspec/changes/pseudonymize-customer-email/).

```bash
git add openspec
```

```bash
git commit -m "Propose pseudonymize-customer-email"
```

## 8.5 Implementar y archivar

```text
/clear
/opsx:apply pseudonymize-customer-email
```

Los tests y el pipeline necesitan una clave de prueba: cualquier cadena de 32 caracteres o más que **no** sea una clave real. Defínela en el mismo terminal en el que vas a ejecutarlos:

**Git Bash, macOS y Linux:**

```bash
export MERCALUZ_PII_KEY=clave-de-prueba-solo-para-tests-0000
```

**PowerShell:**

```powershell
$env:MERCALUZ_PII_KEY = "clave-de-prueba-solo-para-tests-0000"
```

**cmd:**

```bat
set MERCALUZ_PII_KEY=clave-de-prueba-solo-para-tests-0000
```

```bash
uv run pytest
```

```bash
uv run python run_pipeline.py --all
```

Comprueba que silver ya no contiene emails:

```bash
uv run python query.py "SELECT order_id, customer_key FROM silver.order_lines LIMIT 3"
```

```text
/opsx:archive pseudonymize-customer-email
```

```
Applying changes to openspec/specs/data-quality/spec.md:
  ~ 1 modified
Applying changes to openspec/specs/order-lines/spec.md:
  ~ 1 modified
Applying changes to openspec/specs/pii-protection/spec.md:
  + 3 added
```

```bash
git add .
```

```bash
git commit -m "Pseudonymize customer email outside bronze"
```

## 8.6 Cuándo explorar y cuándo proponer directamente

| Situación | Punto de partida |
|---|---|
| El objetivo y la solución están claros ("añade la regla DQ006") | `/opsx:propose` |
| El problema está claro, pero no la solución (RGPD, rendimiento, elección de herramienta) | `/opsx:explore` |
| Es necesario entender código o specs desconocidos | `/opsx:explore` |
| Hay que comparar alternativas con negocio o con el área legal | `/opsx:explore` y, después, `propose` |

---

## Lista de comprobación final

- [ ] Has utilizado `/opsx:explore` y has comprobado que no escribe código
- [ ] El change afecta a **3 capabilities** (1 nueva y 2 modificadas)
- [ ] Puedes explicar por qué la cuarentena también contenía datos personales
- [ ] `silver.order_lines` tiene `customer_key` y no `customer_email`
- [ ] `openspec list --specs` muestra 6 capabilities

**Fin del taller.** Para seguir profundizando, consulta el anexo [OpenSpec en equipo](../appendix/openspec-in-teams.md), la [referencia de comandos](../appendix/command-cheatsheet.md) y los [patrones de specs para Data Engineering](../appendix/data-engineering-spec-patterns.md).

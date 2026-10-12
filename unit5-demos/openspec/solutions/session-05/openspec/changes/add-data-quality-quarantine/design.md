# Design

## Context

`silver.order_lines` se reconstruye por completo desde bronze, y el filtrado de filas inválidas está implícito en las conversiones de tipo. No hay ninguna regla sobre el valor de la cantidad.

## Goals / Non-Goals

**Goals:**
- Una única evaluación de reglas que alimente a la vez silver y la cuarentena, sin lógica duplicada.
- Saber, para cada fila excluida, qué reglas ha incumplido.

**Non-Goals:**
- Detener el pipeline cuando hay muchas filas en cuarentena.
- Un framework genérico de calidad (Great Expectations, Soda…).

## Decisions

1. **Tabla de cuarentena separada en lugar de una columna `is_valid` en silver.** Los consumidores de silver no tienen que cambiar nada. Alternativa descartada: marcar las filas en silver, lo que obligaría a todos los consumidores a filtrarlas.
2. **Una fila de cuarentena por fila de bronze, con la lista de reglas incumplidas** (`dq_failed_rules`). Alternativa descartada: una fila por regla incumplida, que duplica datos y complica los recuentos.
3. **Evaluación en una tabla temporal y creación de silver y cuarentena en la misma transacción**, para que ambas reflejen siempre la misma ejecución.

## Risks / Trade-offs

- [Las cifras históricas de gold cambian: desaparece el -7,50 de VLC-007] → Avisar a BI de que es una corrección.

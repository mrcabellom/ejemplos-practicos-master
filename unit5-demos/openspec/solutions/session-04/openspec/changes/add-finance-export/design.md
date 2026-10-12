# Design

## Context

La macro de Excel de Finanzas espera un CSV con formato regional español. Un CSV estándar (separador `,` y punto decimal) se abriría con las columnas mal separadas.

## Goals / Non-Goals

**Goals:**
- Un fichero que la macro de Finanzas abra sin ajustes.

**Non-Goals:**
- Históricos o un fichero por día: el fichero contiene todas las fechas de gold.

## Decisions

1. **Formato escrito por el propio código** (separador `;`, coma decimal, dos decimales). Alternativa descartada: `COPY ... TO` de DuckDB, que no aplica coma decimal en los importes.
2. **Fichero completo en cada ejecución**, sobrescribiendo el anterior, igual que gold.

## Risks / Trade-offs

- [La macro de Finanzas depende de los nombres y el orden de las columnas] → Cualquier cambio en la cabecera debe tratarse como **BREAKING** y acordarse con Finanzas.

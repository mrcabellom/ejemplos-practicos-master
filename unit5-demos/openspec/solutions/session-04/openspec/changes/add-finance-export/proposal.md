# Proposal

## Why

Control de Gestión (Finanzas) no tiene acceso a Power BI: trabaja con una macro de Excel que lee un fichero CSV diario. Necesita las ventas por día y tienda en un formato que su Excel en español abra sin ajustes.

## What Changes

- Nuevo fichero `exports/finance_daily_sales.csv`, generado en cada ejecución a partir de `gold.daily_sales`.
- Formato compatible con Excel en español: separador `;` y coma decimal.

## Capabilities

### New Capabilities
- `finance-export`: fichero diario de ventas para la macro de Excel de Finanzas.

### Modified Capabilities
<!-- Ninguna -->

## Impact

- Ficheros: nuevo `exports/finance_daily_sales.csv`.
- Consumidores: macro de Excel de Control de Gestión (Marta). El formato del fichero pasa a ser un contrato con Finanzas: cualquier cambio de columnas será **BREAKING**.
- Código: módulo de exports, paso nuevo en `run_pipeline.py` y tests.

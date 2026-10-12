# Spec Delta

## Purpose

Entregar al equipo de Control de Gestión un fichero diario con las ventas por tienda que su macro de Excel pueda abrir directamente.

## ADDED Requirements

### Requirement: Fichero diario para Finanzas
El pipeline SHALL generar en cada ejecución el fichero `exports/finance_daily_sales.csv` con la cabecera `date;store;orders;total_amount` y una línea por fila de `gold.daily_sales`, ordenadas por fecha y tienda.

#### Scenario: Contenido del export
- **WHEN** `gold.daily_sales` contiene (2026-10-01, MAD-001) con 2 pedidos y 26,09
- **THEN** el fichero contiene la línea `2026-10-01;MAD-001;2;26,09`

### Requirement: Formato numérico compatible con Excel en español
El export SHALL usar `;` como separador, coma como separador decimal, exactamente dos decimales en los importes y codificación UTF-8.

#### Scenario: Importe con decimales
- **WHEN** el importe de (2026-10-01, BCN-014) es 1,6
- **THEN** el fichero lo escribe como `1,60`

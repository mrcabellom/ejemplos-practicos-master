# Glosario

## OpenSpec

| Término | Definición | Ejemplo en Mercaluz |
|---|---|---|
| **SDD (Spec-Driven Development)** | Acordar y escribir la especificación antes de implementar, y usarla como guía para la IA y como documentación viva | Todo el taller |
| **Spec principal** | `openspec/specs/<capability>/spec.md`. Describe cómo se comporta el sistema **hoy** | `openspec/specs/daily-sales/spec.md` |
| **Capability** | Comportamiento duradero del sistema con nombre propio; agrupa requisitos relacionados | `orders-ingestion`, `pii-protection` |
| **Change** | Carpeta en `openspec/changes/` con una propuesta de cambio y sus artefactos | `make-orders-ingestion-idempotent` |
| **Artefacto** | Documento de un change definido por el schema | `proposal.md`, `specs/`, `design.md`, `tasks.md` |
| **Delta (delta spec)** | Spec dentro de un change que dice qué requisitos se añaden, modifican, eliminan o renombran | `changes/split-gross-net-revenue/specs/daily-sales/spec.md` |
| **Requirement** | Comportamiento normativo (`SHALL`/`MUST`) con nombre y al menos un escenario | "Fichero de pedidos ausente" |
| **Scenario** | Caso concreto `WHEN`/`THEN` que ilustra y permite verificar un requisito | "Fecha sin fichero" con `2026-09-30.csv` |
| **ADDED / MODIFIED / REMOVED / RENAMED** | Las cuatro operaciones delta | ADDED en las sesiones 1 a 4 y 6; MODIFIED en la 5; REMOVED y RENAMED en la 7 |
| **Purpose** | Sección inicial de una capability nueva que explica para qué sirve | `orders-ingestion` → "Cargar en la capa bronze los ficheros diarios…" |
| **Archive** | Fusionar los deltas de un change en las specs principales y moverlo a `changes/archive/AAAA-MM-DD-<nombre>/` | `2026-10-12-add-orders-ingestion` |
| **Sync** | Fusionar deltas en las specs principales sin archivar el change | Útil si el change sigue abierto pero otros necesitan ver la spec |
| **Schema (de OpenSpec)** | Define qué artefactos tiene un change, sus dependencias, plantillas e instrucciones. No confundir con el schema de una base de datos | `spec-driven` (por defecto), `mercaluz-data` (anexo OpenSpec en equipo) |
| **Perfil** | Conjunto de workflows `/opsx:*` instalados | `core`, ampliado |
| **`config.yaml`** | Configuración del proyecto: schema, contexto y reglas que se inyectan en las instrucciones de la IA | Sesión 0 |
| **Store** (beta) | Repositorio independiente que solo contiene `openspec/` y se comparte entre varios repositorios de código | `mercaluz-contracts` |
| **BREAKING** | Marca en la proposal para cambios que rompen a consumidores | Eliminar `total_amount` de gold |
| **Brownfield / greenfield** | Proyecto con código existente / proyecto que parte de cero | En el taller, el pipeline de Mercaluz se construye desde cero (greenfield) |

## Datos

| Término | Definición | Ejemplo en Mercaluz |
|---|---|---|
| **Pipeline** | Programa que lleva los datos, paso a paso, desde su origen hasta las tablas que usa el negocio | `run_pipeline.py` |
| **DuckDB** | Base de datos SQL que vive en un único fichero, sin servidor, pensada para análisis | `warehouse/mercaluz.duckdb` |
| **Schema (de base de datos)** | Grupo de tablas dentro de una base de datos. El nombre completo de una tabla es `schema.tabla` | `bronze`, `silver`, `gold` |
| **Landing** | Carpeta donde llegan los ficheros de origen antes de cargarlos | `data/landing/orders/2026-10-01.csv` |
| **Medallion** | Arquitectura de datos en capas: bronze (copia literal), silver (limpio y tipado) y gold (agregados de negocio) | `bronze.orders_raw` → `silver.order_lines` → `gold.daily_sales` |
| **Linaje** | Información sobre de dónde viene cada dato y cuándo llegó | Columnas `_source_file` e `_ingested_at` en bronze |
| **Export** | Fichero que se genera a partir de una tabla para otro equipo o sistema | `exports/finance_daily_sales.csv` |
| **Consumidor (*downstream*)** | Equipo, informe o programa que utiliza los datos. Un cambio en la tabla puede afectarle | Power BI, la macro de Excel de Finanzas |
| **Contrato de datos** | Acuerdo explícito sobre esquema, significado, frescura y versionado de un dato publicado | Formato del export (sesión 4) y artefacto `data-contract.md` (anexo OpenSpec en equipo) |
| **Grano** | Qué representa una fila de una tabla | `gold.daily_sales`: una fila por día y tienda |
| **Clave única** | Columna o columnas que identifican una fila sin repetirse | (`order_date`, `store_id`) en gold |
| **SLA de frescura** | Compromiso de cuándo estarán disponibles los datos | "gold disponible antes de las 07:00 UTC" |
| **Calidad de datos (reglas DQ)** | Comprobaciones que debe cumplir cada fila; cada regla tiene un código | DQ003: `quantity` mayor que 0 |
| **Cuarentena** | Tabla donde se guardan las filas que no pasan las reglas de calidad, con el motivo | `silver.order_lines_quarantine` |
| **Idempotencia** | Ejecutar N veces produce el mismo resultado que ejecutar una | Sesión 6 |
| **Reprocesar** | Volver a ejecutar el pipeline para una fecha ya cargada, por ejemplo porque el fichero llegó corregido | El fichero de 2026-10-02 sin O-1011 |
| **Backfill** | Reprocesar un rango histórico de fechas | Recargar todo septiembre tras corregir un error |
| **Transacción** | Grupo de operaciones que se aplican todas o ninguna; si algo falla a mitad, se deshace todo | DELETE + INSERT de un fichero en bronze |
| **DELETE + INSERT** | Sustituir un bloque de filas borrándolo y volviéndolo a insertar | Recargar un fichero completo |
| **MERGE** | Sentencia SQL que, usando una clave, actualiza las filas existentes e inserta las nuevas | Descartada en la sesión 6 porque bronze no tiene clave |
| **Vista (`VIEW`)** | Consulta SQL guardada con nombre que se lee como una tabla, sin guardar datos propios | `gold.daily_sales_v1` |
| **Rollback** | Volver al estado anterior cuando algo sale mal (de una transacción o de un despliegue) | Deshacer una carga fallida en bronze (sesión 6) |
| **Huella (*hash*)** | Código corto calculado a partir de un contenido; cualquier cambio en el contenido modifica la huella | SHA-256, base del `customer_key` (sesión 8) |
| **Runbook** | Guía operativa paso a paso para una tarea o incidencia | Cómo reprocesar un día |

## Datos personales y seguridad

| Término | Definición | Ejemplo en Mercaluz |
|---|---|---|
| **RGPD** | Reglamento europeo de protección de datos personales | Auditoría de la sesión 8 |
| **DPO** | Delegado de protección de datos: la persona que vela por el cumplimiento del RGPD | Andrés |
| **PII / dato personal** | Dato que identifica a una persona | `customer_email` |
| **Minimización** | Principio del RGPD: tratar solo los datos personales imprescindibles | BI no necesita el email, solo distinguir clientes |
| **Seudonimización** | Sustituir un identificador personal por otro que no permite identificar a la persona sin información adicional (la clave) | `customer_key` |
| **SHA-256** | Función de hash muy usada. Sin clave, un email se puede adivinar probando emails típicos | Descartada para el email |
| **Ataque por diccionario** | Calcular el hash de muchos valores probables y buscar coincidencias | Probar `nombre.apellido@...` |
| **HMAC** | Hash que usa además una clave secreta; sin la clave no se pueden calcular ni adivinar los códigos | `customer_key` = HMAC-SHA256 del email |
| **Tokenización con bóveda** | Sustituir el dato por un código aleatorio (token) y guardar la correspondencia en un servicio protegido (la bóveda), que permite recuperar el original | Descartada en la sesión 8: exige un servicio nuevo |
| **Secreto** | Valor confidencial (clave, contraseña) que se guarda fuera del código y se lee de una variable de entorno | `MERCALUZ_PII_KEY` |

## Equipo y producción

| Término | Definición | Ejemplo en Mercaluz |
|---|---|---|
| **PR (*pull request*)** | Petición para incorporar los cambios de una rama a la principal, con revisión previa | Un pull request con la propuesta y otro con el código (anexo OpenSpec en equipo) |
| **CI (integración continua)** | Comprobaciones automáticas en cada PR, como validar specs o pasar tests | `.github/workflows/openspec.yml` |
| **CODEOWNERS** | Fichero de GitHub que indica quién debe revisar cada carpeta | Finanzas revisa `finance-export` |
| **Airflow / DAG** | Herramienta que programa y lanza los pipelines; un DAG es la definición de un flujo de tareas | El DAG diario de Mercaluz |
| **Databricks / Delta** | Plataforma de datos en la nube y su formato de tablas; es donde Mercaluz ejecuta el pipeline en producción | Solo aparece en los apartados opcionales |
| **Power BI** | Herramienta de cuadros de mando que lee las tablas de gold | Los 12 informes que usan `total_amount` |

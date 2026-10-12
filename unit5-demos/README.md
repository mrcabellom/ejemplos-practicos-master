# Demos de la Unidad 5

Desarrollo guiado por especificaciones (*spec-driven development*) con **Claude Code** y tres herramientas distintas.
Los tres ejemplos son independientes.

| Carpeta | Herramienta | Caso | Formato |
|---|---|---|---|
| [spec-kit](spec-kit/README.md) | GitHub Spec Kit | **La Despensa**: tabla de ventas diarias de dos tiendas | Un solo cambio, de la constitución al código |
| [openspec](openspec/README.md) | OpenSpec | **Mercaluz**: pipeline de datos con capas bronze, silver y gold | Taller de nueve sesiones, de menos a más |
| [gsd-core](gsd-core/README.md) | GSD Core | **Kinesia**: API de reservas de una clínica de fisioterapia | Un solo cambio, con subagentes y fases |

Un orden razonable es Spec Kit, OpenSpec y GSD Core. Los READMEs de Spec Kit y de GSD Core incluyen, al
final, una comparación con OpenSpec.

## Requisitos

| Ejemplo | Necesita |
|---|---|
| Spec Kit | uv y Git |
| OpenSpec | uv, Git y Node.js 20.19 o superior |
| GSD Core | uv, Git y Node.js 24 o superior |

La instalación de estas herramientas está en el [README principal](../README.md#instalación). Los tres ejemplos
guardan datos en DuckDB o SQLite, que se pueden explorar con los visores opcionales descritos allí.

## Antes de empezar

Cada README explica cómo copiar el proyecto de partida a la carpeta `~/taller` e inicializar allí un repositorio Git
propio. Trabaja siempre sobre esa copia: así puedes repetir el ejemplo desde el principio y el historial del ejercicio
no se mezcla con el de este repositorio.

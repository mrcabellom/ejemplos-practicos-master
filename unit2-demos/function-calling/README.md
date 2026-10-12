# Function calling con Claude

Ejemplo mínimo de *function calling* (*tool use*) con la API de Claude y el modelo Claude Sonnet 5.5.

## Cómo funciona

`function_calling.py` define dos funciones de Python y las describe a Claude con un esquema JSON:

- `get_weather`: devuelve el tiempo de una ciudad (datos simulados).
- `calculate`: evalúa una expresión aritmética. Solo admite números, operadores y paréntesis.

El programa hace una pregunta que necesita las dos herramientas y entra en un bucle:

1. Claude responde con uno o varios bloques `tool_use`: qué herramienta quiere usar y con qué argumentos.
2. El programa ejecuta cada función y devuelve todos los resultados en un único mensaje (`tool_result`).
3. El bucle se repite hasta que Claude responde con texto, sin pedir más herramientas.

Claude nunca ejecuta código: solo decide qué función llamar. Quien la ejecuta es el programa.

## Ejecutarlo

Hace falta [uv](https://docs.astral.sh/uv/) y una clave de la API de Anthropic. Desde esta carpeta:

1. Copia `.env.example` como `.env` y escribe tu clave en `ANTHROPIC_API_KEY`. El fichero `.env` está en
   `.gitignore`: la clave no debe subirse nunca al repositorio.
2. Instala las dependencias y ejecuta el ejemplo:

```bash
uv sync
```

```bash
uv run function_calling.py
```

En la consola aparecen las llamadas a herramientas con sus argumentos y resultados, y al final la respuesta de Claude.

"""Function calling (tool use) example with Claude Sonnet 5.5.

Usage:
    uv sync
    # create a .env file containing: ANTHROPIC_API_KEY=sk-ant-...
    uv run function_calling.py
"""
import json
import os

import anthropic
from dotenv import load_dotenv
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel

MODEL = "claude-sonnet-5-5"
console = Console()

# Load ANTHROPIC_API_KEY from the .env file; the client reads it from the environment.
# Never hardcode the key in the source code.
load_dotenv()
if not os.environ.get("ANTHROPIC_API_KEY"):
    raise SystemExit("Set ANTHROPIC_API_KEY in your .env file")
client = anthropic.Anthropic()


# 1) Real functions that Claude can "call"
def get_weather(city: str, unit: str = "celsius") -> dict:
    # A real weather API call would go here (simulated).
    data = {"madrid": 24, "paris": 18, "london": 15}
    temp = data.get(city.lower(), 20)
    if unit == "fahrenheit":
        temp = round(temp * 9 / 5 + 32)
    return {"city": city, "temperature": temp, "unit": unit, "condition": "sunny"}


def calculate(expression: str) -> dict:
    # Only arithmetic characters allowed (never eval free-form input).
    if not set(expression) <= set("0123456789+-*/(). "):
        return {"error": "expression not allowed"}
    return {"result": eval(expression, {"__builtins__": {}})}


FUNCTIONS = {"get_weather": get_weather, "calculate": calculate}

# 2) JSON schema definitions of the tools sent to Claude
TOOLS = [
    {
        "name": "get_weather",
        "description": "Get the current weather for a city.",
        "input_schema": {
            "type": "object",
            "properties": {
                "city": {"type": "string", "description": "City name, e.g. Madrid"},
                "unit": {"type": "string", "enum": ["celsius", "fahrenheit"]},
            },
            "required": ["city"],
        },
    },
    {
        "name": "calculate",
        "description": "Evaluate an arithmetic expression, e.g. '(3+4)*12'.",
        "input_schema": {
            "type": "object",
            "properties": {"expression": {"type": "string"}},
            "required": ["expression"],
        },
    },
]


def run(user_prompt: str) -> str:
    messages = [{"role": "user", "content": user_prompt}]

    # 3) Loop: Claude requests tools -> we run them -> we send the results back
    while True:
        response = client.messages.create(
            model=MODEL,
            max_tokens=16000,
            tools=TOOLS,
            messages=messages,
        )

        if response.stop_reason != "tool_use":
            return "".join(b.text for b in response.content if b.type == "text")

        # Keep the full assistant turn (includes the tool_use blocks)
        messages.append({"role": "assistant", "content": response.content})

        # Run every call and return ALL results in a single user message
        results = []
        for block in response.content:
            if block.type != "tool_use":
                continue
            console.print(
                f"[bold magenta]🔧 Tool call[/] [bold cyan]{block.name}[/]"
                f"[dim]({json.dumps(block.input)})[/]"
            )
            try:
                output = FUNCTIONS[block.name](**block.input)
                console.print(f"   [green]✔ result:[/] [yellow]{json.dumps(output)}[/]")
                results.append({
                    "type": "tool_result",
                    "tool_use_id": block.id,
                    "content": json.dumps(output),
                })
            except Exception as e:
                console.print(f"   [bold red]✘ error:[/] {e}")
                results.append({
                    "type": "tool_result",
                    "tool_use_id": block.id,
                    "content": f"Error: {e}",
                    "is_error": True,
                })
        messages.append({"role": "user", "content": results})


if __name__ == "__main__":
    question = "What's the weather in Madrid and Paris? Also, what is (24+18)*2?"
    console.print(Panel(question, title="[bold blue]🙋 Question", border_style="blue"))
    answer = run(question)
    console.print(Panel(Markdown(answer), title="[bold green]🤖 Claude", border_style="green"))

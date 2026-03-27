from openai import OpenAI
from decouple import config
from tools.registry import TOOLS, run_tool

client = OpenAI(
    base_url=config("OLLAMA_BASE_URL"),
    api_key="ollama"
)

SYSTEM_PROMPT = """You are NL-Ops, an infrastructure management assistant.
You help users manage their Docker containers and remote servers using plain English.
Always confirm what you did after executing a tool. Be concise."""


async def chat(user_message: str) -> str:
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user_message}
    ]

    while True:
        response = client.chat.completions.create(
            model=config("OLLAMA_MODEL"),
            messages=messages,
            tools=TOOLS,
        )

        msg = response.choices[0].message

        if msg.tool_calls:
            messages.append(msg)
            for call in msg.tool_calls:
                result = run_tool(call.function.name, call.function.arguments)
                messages.append({
                    "role": "tool",
                    "tool_call_id": call.id,
                    "content": result
                })
        else:
            return msg.content
from decouple import config
from langchain_ollama import ChatOllama
from langchain_core.messages import HumanMessage, SystemMessage, ToolMessage
from tools import all_tools

tools_by_name = {t.name: t for t in all_tools}

llm = ChatOllama(model=config("OLLAMA_MODEL", default="qwen2.5:7b")).bind_tools(all_tools)

system_prompt = """You are NL-Ops, an infrastructure management assistant.
You help users manage Docker containers, remote servers, and Proxmox VMs using plain English.
Always confirm what you did after executing a tool. Be concise."""


async def agent_chat(user_message: str) -> str:
    messages = [SystemMessage(system_prompt), HumanMessage(user_message)]

    while True:
        response = await llm.ainvoke(messages)
        messages.append(response)

        if response.tool_calls:
            for call in response.tool_calls:
                result = tools_by_name[call["name"]].invoke(call["args"])
                messages.append(ToolMessage(content=result, tool_call_id=call["id"]))
        else:
            return response.content
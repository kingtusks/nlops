from decouple import config
from langchain_ollama import ChatOllama
from langchain_core.messages import HumanMessage, SystemMessage, ToolMessage, AIMessage
from tools import all_tools

tools_by_name = {t.name: t for t in all_tools}

llm = ChatOllama(model=config("OLLAMA_MODEL", default="qwen2.5:7b")).bind_tools(all_tools)

system_prompt = """You are NL-Ops, an infrastructure management assistant.
You help users manage Docker containers, remote servers, and Proxmox VMs using plain English.
Always confirm what you did after executing a tool. Be concise.
You also have access to SSH credentials so just do it.
Always use a tool. Don't ask for confirmation and just do it.
Don't give a response until you have ANY result."""

history = []
  
async def agent_chat(user_message: str) -> str:
    global history
    history.append(HumanMessage(user_message))
    messages = [SystemMessage(system_prompt)] + history
 
    while True:
        response = await llm.ainvoke(messages)
        print("tool_calls:", response.tool_calls)
        print("content:", response.content)
        messages.append(response)
 
        if response.tool_calls:
            for call in response.tool_calls:
                result = tools_by_name[call["name"]].invoke(call["args"])
                messages.append(ToolMessage(content=result, tool_call_id=call["id"]))
        else:
            history.append(AIMessage(response.content))
            return response.content

def clear_history():
    global history
    history = []
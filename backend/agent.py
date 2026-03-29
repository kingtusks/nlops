from decouple import config
from langchain_ollama import ChatOllama
from langchain_core.messages import HumanMessage, SystemMessage, ToolMessage, AIMessage
from tools import all_tools

tools_by_name = {t.name: t for t in all_tools}

llm = ChatOllama(model=config("OLLAMA_MODEL", default="qwen2.5:7b")).bind_tools(all_tools)

system_prompt = """You are NL-Ops (Enel), a server management assistant.

You control:
- Docker
- Linux servers via SSH
- Proxmox VMs

RULES:
- ALWAYS run a command using a tool before replying
- NEVER ask for confirmation
- NEVER explain before execution
- If unsure, run diagnostic commands first

RESPONSE FORMAT:
- Action: <what you did>
- Result: <command output or summary>

BEHAVIOR:
- Be short and direct
- Use simple commands
- Do not add extra text
- ONLY SPEAK ENGLISH

DESTRUCTIVE ACTIONS:
- If deleting or stopping things, include "DESTRUCTIVE" in Action

FAILURES:
- If command fails, show the error
- Optionally try one simple fix, then stop

COMMON COMMANDS:
- Docker: docker ps, docker logs, docker restart, docker exec
- System: ss -tulnp, systemctl status, journalctl -xe
- Network: ping, curl, traceroute

EXAMPLES:

User: restart nginx container
Action: docker restart nginx
Result: nginx restarted

User: why is ssh not working
Action: ss -tulnp | grep sshd
Result: no output (ssh not running)"""

history = []
  
async def agent_chat(user_message: str) -> str:
    global history
    history.append(HumanMessage(user_message))
    messages = [SystemMessage(system_prompt)] + history[-3:]
 
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
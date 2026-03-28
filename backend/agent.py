import docker
import paramiko
from decouple import config
from langchain_ollama import ChatOllama
from langchain_core.messages import HumanMessage, SystemMessage, ToolMessage
from langchain_core.tools import tool


@tool
def list_containers() -> str:
    """Lists all running Docker containers"""
    try:
        client = docker.from_env()
        containers = client.containers.list()
        return "\n".join([f"{c.name} ({c.status})" for c in containers]) or "no running containers"
    except Exception as e:
        return f"error: {e}"


@tool
def restart_container(name: str) -> str:
    """Restarts a Docker container by name"""
    try:
        client = docker.from_env()
        client.containers.get(name).restart()
        return f"{name} restarted successfully"
    except Exception as e:
        return f"error: {e}"


@tool
def stop_container(name: str) -> str:
    """Stops a Docker container by name"""
    try:
        client = docker.from_env()
        client.containers.get(name).stop()
        return f"{name} stopped"
    except Exception as e:
        return f"error: {e}"


@tool
def get_logs(name: str) -> str:
    """Gets the last 50 log lines from a Docker container"""
    try:
        client = docker.from_env()
        return client.containers.get(name).logs(tail=50).decode() or "no logs"
    except Exception as e:
        return f"error: {e}"


@tool
def run_ssh_command(command: str) -> str:
    """Runs a shell command on the remote server over SSH"""
    host = config("SSH_HOST", default=None)
    user = config("SSH_USER", default=None)
    password = config("SSH_PASSWORD", default=None)

    if not host or not user:
        return "SSH not configured. Set SSH_HOST and SSH_USER in .env"
    try:
        client = paramiko.SSHClient()
        client.load_system_host_keys()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(host, username=user, password=password)
        _, stdout, stderr = client.exec_command(command)
        output = stdout.read().decode().strip()
        error = stderr.read().decode().strip()
        client.close()
        return output or error or "command ran with no output"
    except Exception as e:
        return f"error: {e}"


tools = [list_containers, restart_container, stop_container, get_logs, run_ssh_command]
tools_by_name = {t.name: t for t in tools}

llm = ChatOllama(model=config("OLLAMA_MODEL")).bind_tools(tools)

SYSTEM = """You are NL-Ops, an infrastructure management assistant.
You help users manage their Docker containers and remote servers using plain English.
Always confirm what you did after executing a tool. Be concise."""


async def chat(user_message: str) -> str:
    messages = [SystemMessage(SYSTEM), HumanMessage(user_message)]

    while True:
        response = await llm.ainvoke(messages)
        messages.append(response)

        if response.tool_calls:
            for call in response.tool_calls:
                result = tools_by_name[call["name"]].invoke(call["args"])
                messages.append(ToolMessage(content=result, tool_call_id=call["id"]))
        else:
            return response.content
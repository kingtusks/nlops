import docker
import paramiko
from decouple import config
from langchain_ollama import ChatOllama
from langchain_core.messages import HumanMessage, SystemMessage, ToolMessage
from langchain_core.tools import tool


@tool
def list_containers() -> str:
    """Lists all running Docker containers"""
    print("docker: list containers")
    try:
        client = docker.from_env()
        containers = client.containers.list()
        return "\n".join([f"{c.name} ({c.status})" for c in containers]) or "no running containers"
    except Exception as e:
        print(f"error: {e}")
        return f"error: {e}"


@tool
def restart_container(name: str) -> str:
    """Restarts a Docker container by name"""
    print(f"docker: restart container {name}")
    try:
        client = docker.from_env()
        client.containers.get(name).restart()
        return f"{name} restarted successfully"
    except Exception as e:
        return f"error: {e}"


@tool
def stop_container(name: str) -> str:
    """Stops a Docker container by name"""
    print(f"docker: stop container {name}")
    try:
        client = docker.from_env()
        client.containers.get(name).stop()
        return f"{name} stopped"
    except Exception as e:
        return f"error: {e}"


@tool
def get_logs(name: str) -> str:
    """Gets the last 50 log lines from a Docker container"""
    print(f"docker: logs for container {name}")
    try:
        client = docker.from_env()
        return client.containers.get(name).logs(tail=50).decode() or "no logs"
    except Exception as e:
        return f"error: {e}"


@tool
def run_ssh_command(command: str) -> str:
    """Runs a shell command on the remote server over SSH"""
    print(f"ssh: run command {command}")
    host = config("SSH_HOST", default=None)
    user = config("SSH_USER", default=None)
    password = config("SSH_PASSWORD", default=None)

    if not host or not user:
        print("no host or no user")
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
        print(f"error: {e}")
        return f"error: {e}"

@tool
def list_images() -> str:
    """Lists all Docker images on the system"""
    try:
        client = docker.from_env()
        images = client.images.list()
        if not images:
            return "no images found"
        lines = []
        for img in images:
            tags = img.tags if img.tags else ["<untagged>"]
            size_mb = round(img.attrs["Size"] / 1_000_000, 1)
            lines.append(f"{', '.join(tags)} ({size_mb} MB)")
        return "\n".join(lines)
    except Exception as e:
        return f"error: {e}"


@tool
def docker_stats() -> str:
    """Shows CPU and memory usage for all running containers"""
    try:
        client = docker.from_env()
        containers = client.containers.list()
        if not containers:
            return "no running containers"
        lines = []
        for c in containers:
            stats = c.stats(stream=False)
            cpu_delta = stats["cpu_stats"]["cpu_usage"]["total_usage"] - stats["precpu_stats"]["cpu_usage"]["total_usage"]
            system_delta = stats["cpu_stats"]["system_cpu_usage"] - stats["precpu_stats"]["system_cpu_usage"]
            num_cpus = stats["cpu_stats"].get("online_cpus", 1)
            cpu_pct = round((cpu_delta / system_delta) * num_cpus * 100, 2) if system_delta > 0 else 0.0
            mem_usage = round(stats["memory_stats"]["usage"] / 1_000_000, 1)
            mem_limit = round(stats["memory_stats"]["limit"] / 1_000_000, 1)
            lines.append(f"{c.name}: CPU {cpu_pct}% | MEM {mem_usage}MB / {mem_limit}MB")
        return "\n".join(lines)
    except Exception as e:
        return f"error: {e}"


@tool
def pull_image(image: str) -> str:
    """Pulls a Docker image by name (e.g. nginx:latest)"""
    try:
        client = docker.from_env()
        client.images.pull(image)
        return f"pulled {image} successfully"
    except Exception as e:
        return f"error: {e}"


@tool
def run_container(image: str, name: str, ports: str = "") -> str:
    """
    Runs a new Docker container from an image.
    image: image name e.g. nginx:latest
    name: container name
    ports: optional port mapping e.g. '8080:80'
    """
    try:
        client = docker.from_env()
        port_bindings = {}
        if ports:
            host_port, container_port = ports.split(":")
            port_bindings[container_port] = host_port
        client.containers.run(image, name=name, ports=port_bindings, detach=True)
        return f"container '{name}' started from image '{image}'"
    except Exception as e:
        return f"error: {e}"


@tool
def ssh_disk_usage() -> str:
    """Shows disk usage on the remote server"""
    return run_ssh_command.invoke({"command": "df -h"})


@tool
def ssh_memory() -> str:
    """Shows memory usage on the remote server"""
    return run_ssh_command.invoke({"command": "free -h"})


@tool
def ssh_top_processes() -> str:
    """Shows the top 10 CPU-consuming processes on the remote server"""
    return run_ssh_command.invoke({"command": "ps aux --sort=-%cpu | head -11"})



tools = [
    list_containers, restart_container, stop_container, get_logs,
    run_ssh_command, list_images, docker_stats, pull_image, run_container,
    ssh_disk_usage, ssh_memory, ssh_top_processes
]
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
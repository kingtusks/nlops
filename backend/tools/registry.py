import json
from tools.docker_tools import list_containers, restart_container, stop_container, get_logs
from tools.ssh_tools import run_command

TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "list_containers",
            "description": "Lists all running Docker containers",
            "parameters": {
                "type": "object",
                "properties": {}
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "restart_container",
            "description": "Restarts a Docker container by name",
            "parameters": {
                "type": "object",
                "properties": {
                    "name": {"type": "string", "description": "Container name"}
                },
                "required": ["name"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "stop_container",
            "description": "Stops a running Docker container by name",
            "parameters": {
                "type": "object",
                "properties": {
                    "name": {"type": "string", "description": "Container name"}
                },
                "required": ["name"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_logs",
            "description": "Gets the last 50 lines of logs from a Docker container",
            "parameters": {
                "type": "object",
                "properties": {
                    "name": {"type": "string", "description": "Container name"}
                },
                "required": ["name"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "run_ssh_command",
            "description": "Runs a shell command on the remote server over SSH. Use for system stats, service management, or anything outside Docker.",
            "parameters": {
                "type": "object",
                "properties": {
                    "command": {"type": "string", "description": "Shell command to run"}
                },
                "required": ["command"]
            }
        }
    }
]


def run_tool(name: str, args: str | dict) -> str:
    if isinstance(args, str):
        args = json.loads(args)
    match name:
        case "list_containers":
            return list_containers()
        case "restart_container":
            return restart_container(args["name"])
        case "stop_container":
            return stop_container(args["name"])
        case "get_logs":
            return get_logs(args["name"])
        case "run_ssh_command":
            return run_command(args["command"])
        case _:
            return f"unknown tool: {name}"
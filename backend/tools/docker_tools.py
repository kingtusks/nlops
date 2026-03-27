import docker

client = docker.from_env()


def list_containers() -> str:
    try:
        containers = client.containers.list()
        if not containers:
            return "no running containers"
        return "\n".join([f"{c.name} ({c.status})" for c in containers])
    except Exception as e:
        return f"error: {e}"


def restart_container(name: str) -> str:
    try:
        client.containers.get(name).restart()
        return f"{name} restarted successfully"
    except docker.errors.NotFound:
        return f"container '{name}' not found"
    except Exception as e:
        return f"error: {e}"


def stop_container(name: str) -> str:
    try:
        client.containers.get(name).stop()
        return f"{name} stopped"
    except docker.errors.NotFound:
        return f"container '{name}' not found"
    except Exception as e:
        return f"error: {e}"


def get_logs(name: str) -> str:
    try:
        logs = client.containers.get(name).logs(tail=50).decode()
        return logs or "no logs"
    except docker.errors.NotFound:
        return f"container '{name}' not found"
    except Exception as e:
        return f"error: {e}"
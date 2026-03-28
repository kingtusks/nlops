import paramiko
import subprocess
from decouple import config
from langchain_core.tools import tool


def _ssh(command: str) -> str:
    host = config("SSH_HOST", default=None)
    user = config("SSH_USER", default=None)
    password = config("SSH_PASSWORD", default=None)

    if not host or not user:
        return "SSH not configured — set SSH_HOST and SSH_USER in .env"
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


@tool
def run_ssh_command(command: str) -> str:
    """Runs a shell command on the remote server over SSH"""
    return _ssh(command)


@tool
def ssh_disk_usage() -> str:
    """Shows disk usage on the remote server"""
    return _ssh("df -h")


@tool
def ssh_memory() -> str:
    """Shows memory usage on the remote server"""
    return _ssh("free -h")


@tool
def ssh_top_processes() -> str:
    """Shows the top 10 CPU-consuming processes on the remote server"""
    return _ssh("ps aux --sort=-%cpu | head -11")


@tool
def get_public_ip() -> str:
    """Gets the public IP address of the remote server"""
    return _ssh("curl -s https://ifconfig.me")


@tool
def systemctl_status(service: str) -> str:
    """Gets the status of a systemd service on the remote server"""
    return _ssh(f"systemctl status {service} --no-pager")


@tool
def systemctl_restart(service: str) -> str:
    """Restarts a systemd service on the remote server"""
    return _ssh(f"sudo systemctl restart {service}")


@tool
def git_pull(path: str) -> str:
    """Runs git pull in a directory on the remote server to deploy latest code"""
    return _ssh(f"cd {path} && git pull")


@tool
def nginx_reload() -> str:
    """Reloads nginx config on the remote server"""
    return _ssh("sudo nginx -t && sudo systemctl reload nginx")


@tool
def ping_host(host: str) -> str:
    """Pings a host locally to check if it's reachable"""
    try:
        result = subprocess.run(
            ["ping", "-c", "3", host],
            capture_output=True, text=True, timeout=10
        )
        return result.stdout.strip() or result.stderr.strip()
    except subprocess.TimeoutExpired:
        return f"{host} did not respond in time"
    except Exception as e:
        return f"error: {e}"
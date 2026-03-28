import paramiko
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
    """Runs a shell command on the remote server over SSH.
    This should be used as a default command (e.g: if the user didn't specify docker/proxmox)"""
    return _ssh(command)



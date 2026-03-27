import paramiko
import os
from decouple import config

def run_command(command: str) -> str:
    ssh_host = config("SSH_HOST")
    ssh_user = config("SSH_USER")
    if not ssh_host or not ssh_user:
        return "ssh not configured. set SSH_HOST and SSH_USER in .env"
    try:
        client = paramiko.SSHClient()
        client.load_system_host_keys()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh_key_path = config("SSH_KEY_PATH")
        client.connect(
            ssh_host,
            username=ssh_user,
            key_filename=os.path.expanduser(ssh_key_path)
        )
        _, stdout, stderr = client.exec_command(command)
        output = stdout.read().decode().strip()
        error = stderr.read().decode().strip()
        client.close()
        return output or error or "command ran with no output"
    except Exception as e:
        return f"error: {e}"
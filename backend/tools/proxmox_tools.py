from decouple import config
from langchain_core.tools import tool

try:
    from proxmoxer import ProxmoxAPI
    proxmox_available = True
except ImportError:
    proxmox_available = False


def get_client():
    if not proxmox_available:
        raise RuntimeError("proxmoxer not installed — run: pip install proxmoxer requests")
    host = config("PROXMOX_HOST", default=None)
    user = config("PROXMOX_USER", default="root@pam")
    password = config("PROXMOX_PASSWORD", default=None)
    if not host or not password:
        raise RuntimeError("PROXMOX_HOST and PROXMOX_PASSWORD must be set in .env")
    return ProxmoxAPI(host, user=user, password=password, verify_ssl=False)


@tool
def list_vms() -> str:
    """Lists all VMs across all Proxmox nodes with their status"""
    try:
        px = get_client()
        lines = []
        for node in px.nodes.get():
            for vm in px.nodes(node["node"]).qemu.get():
                lines.append(f"[{node['node']}] {vm['name']} (vmid: {vm['vmid']}) — {vm['status']}")
        return "\n".join(lines) or "no VMs found"
    except Exception as e:
        return f"error: {e}"


@tool
def start_vm(vmid: int) -> str:
    """Starts a Proxmox VM by VM ID"""
    try:
        px = get_client()
        for node in px.nodes.get():
            vms = [v for v in px.nodes(node["node"]).qemu.get() if v["vmid"] == vmid]
            if vms:
                px.nodes(node["node"]).qemu(vmid).status.start.post()
                return f"VM {vmid} started"
        return f"VM {vmid} not found"
    except Exception as e:
        return f"error: {e}"


@tool
def stop_vm(vmid: int) -> str:
    """Stops a Proxmox VM by VM ID"""
    try:
        px = get_client()
        for node in px.nodes.get():
            vms = [v for v in px.nodes(node["node"]).qemu.get() if v["vmid"] == vmid]
            if vms:
                px.nodes(node["node"]).qemu(vmid).status.stop.post()
                return f"VM {vmid} stopped"
        return f"VM {vmid} not found"
    except Exception as e:
        return f"error: {e}"


@tool
def restart_vm(vmid: int) -> str:
    """Restarts a Proxmox VM by VM ID"""
    try:
        px = get_client()
        for node in px.nodes.get():
            vms = [v for v in px.nodes(node["node"]).qemu.get() if v["vmid"] == vmid]
            if vms:
                px.nodes(node["node"]).qemu(vmid).status.reboot.post()
                return f"VM {vmid} restarted"
        return f"VM {vmid} not found"
    except Exception as e:
        return f"error: {e}"


@tool
def get_vm_status(vmid: int) -> str:
    """Gets detailed status for a Proxmox VM including CPU, memory, and uptime"""
    try:
        px = get_client()
        for node in px.nodes.get():
            vms = [v for v in px.nodes(node["node"]).qemu.get() if v["vmid"] == vmid]
            if vms:
                status = px.nodes(node["node"]).qemu(vmid).status.current.get()
                cpu_pct = round(status.get("cpu", 0) * 100, 2)
                mem_mb = round(status.get("mem", 0) / 1_000_000, 1)
                maxmem_mb = round(status.get("maxmem", 0) / 1_000_000, 1)
                uptime_hrs = round(status.get("uptime", 0) / 3600, 1)
                return (
                    f"VM {vmid} ({status.get('name', 'unknown')})\n"
                    f"Status: {status.get('status')}\n"
                    f"CPU: {cpu_pct}%\n"
                    f"Memory: {mem_mb}MB / {maxmem_mb}MB\n"
                    f"Uptime: {uptime_hrs}h"
                )
        return f"VM {vmid} not found"
    except Exception as e:
        return f"error: {e}"


@tool
def list_nodes() -> str:
    """Lists all Proxmox cluster nodes and their status"""
    try:
        px = get_client()
        lines = []
        for node in px.nodes.get():
            cpu_pct = round(node.get("cpu", 0) * 100, 2)
            mem_mb = round(node.get("mem", 0) / 1_000_000, 1)
            maxmem_mb = round(node.get("maxmem", 0) / 1_000_000, 1)
            lines.append(f"{node['node']} — {node['status']} | CPU {cpu_pct}% | MEM {mem_mb}MB / {maxmem_mb}MB")
        return "\n".join(lines) or "no nodes found"
    except Exception as e:
        return f"error: {e}"
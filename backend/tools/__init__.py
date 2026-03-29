from tools.docker_tools import (
    list_containers, restart_container, stop_container,
    get_logs, list_images, docker_stats, pull_image, run_container
)
from tools.ssh_tools import (
    run_server_command
)
"""
from tools.proxmox_tools import (
    list_vms, start_vm, stop_vm, restart_vm, get_vm_status, list_nodes
)
"""

all_tools = [
    list_containers, restart_container, stop_container,
    get_logs, list_images, docker_stats, pull_image, run_container,
    run_server_command, 
    
    #list_vms, start_vm, stop_vm, restart_vm, 
    #get_vm_status, list_nodes,
]
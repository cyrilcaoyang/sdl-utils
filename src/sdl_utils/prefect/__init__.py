import os

def is_worker_node() -> bool:
    """Check if the current device is a resource-constrained worker node."""
    try:
        if os.path.exists('/proc/device-tree/model'):
            with open('/proc/device-tree/model', 'r') as f:
                model = f.read()
                # Add other lightweight devices here if needed
                return 'Zero' in model
    except Exception:
        # Not a Linux-based system with a device tree, so assume it's a full node.
        return False
    return False

if is_worker_node():
    # On a worker node, expose only the worker functions.
    # This avoids importing 'prefect' which may not be installed.
    from .worker import execute_remote_task
    __all__ = ['execute_remote_task']
else:
    # On a full node, expose Prefect orchestration tools.
    try:
        from prefect import flow, task
        from .orchestrator import deploy_task_to_worker
        __all__ = ['flow', 'task', 'deploy_task_to_worker']
    except ImportError:
        # Handle case where Prefect is not installed on a full node.
        print("Warning: 'prefect' is not installed. Orchestration features will be unavailable.")
        __all__ = [] 

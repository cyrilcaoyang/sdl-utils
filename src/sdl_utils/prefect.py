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

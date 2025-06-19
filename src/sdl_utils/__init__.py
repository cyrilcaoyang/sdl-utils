# --- Core Functionality ---
from .logger import get_logger
# from .aws_iot import AWSIoTClient, connect_aws_iot, publish_message, subscribe_topic, disconnect_aws_iot
from .socket import connect_socket, send_file_name, receive_file_name, send_file_size, receive_file_size, receive_file
# Placeholder for future development
# from .mqtt import ...
# from .sqlite import ...

# Create a default logger for convenient use throughout the package
logger = get_logger("sdl_utils_default")

# --- Prefect Orchestration (Full Nodes Only) ---
from .prefect_runtime import is_worker_node
if not is_worker_node():
    try:
        from .prefect_orchestrator import run_command_on_worker, request_slack_approval, example_shell_command_flow
        from .slack_bot import slack_client, send_slack_message, ask_for_approval, await_approval_response
        from prefect import flow, task
    except ImportError:
        # Fails gracefully if 'full' extras are not installed
        logger.warning("Prefect components not found. Install with '[full]' extras for orchestration.")

# --- Worker Node Functionality ---
else:
    # This can be expanded if worker-specific helper functions are added later
    pass

# --- Public API ---
# This defines what `from sdl_utils import *` will import.
__all__ = [
    "get_logger",
    "logger",
    "AWSIoTClient",
    "connect_aws_iot",
    "publish_message",
    "subscribe_topic",
    "disconnect_aws_iot",
    "connect_socket",
    "send_file_name",
    "receive_file_name",
    "send_file_size",
    "receive_file_size",
    "receive_file",
]

if not is_worker_node():
    # Conditionally add orchestrator functions to the public API
    __all__.extend([
        "flow",
        "task",
        "run_command_on_worker",
        "request_slack_approval",
        "example_shell_command_flow",
        "slack_client",
        "send_slack_message",
        "ask_for_approval",
        "await_approval_response"
    ])
else:
    # This can be expanded if worker-specific helper functions are added later
    pass

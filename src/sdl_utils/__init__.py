# --- Core Functionality ---
from .logger import get_logger
from .aws_iot import AWSIoTClient, connect_aws_iot, publish_message, subscribe_topic, disconnect_aws_iot
from .socket import connect_socket, send_file_name, receive_file_name, send_file_size, receive_file_size, receive_file

# --- Prefect Orchestration (Full Nodes Only) ---
from .prefect import is_worker_node
if not is_worker_node():
    try:
        from .prefect_orchestrator import deploy_task_to_worker, request_slack_approval, example_approval_flow
        from .slack_bot import slack_client, send_slack_message, ask_for_approval, await_approval_response
        from prefect import flow, task
    except ImportError:
        # Fails gracefully if 'full' extras are not installed
        logger.warning("Prefect components not found. Install with '[full]' extras for orchestration.")

# --- Worker Node Functionality ---
else:
    from .prefect_worker import execute_remote_task

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
    # Conditionally add orchestrator or worker functions to the public API
]

# Create a default logger for convenient use throughout the package
logger = get_logger("sdl_utils_default")

if not is_worker_node():
    __all__.extend([
        "flow", 
        "task",
        "deploy_task_to_worker",
        "request_slack_approval",
        "example_approval_flow",
        "slack_client",
        "send_slack_message",
        "ask_for_approval",
        "await_approval_response"
    ])
else:
    __all__.append("execute_remote_task")

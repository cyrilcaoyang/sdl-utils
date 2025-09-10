# --- Core Functionality ---
from .logger import get_logger
# from .aws_iot import AWSIoTClient, connect_aws_iot, publish_message, subscribe_topic, disconnect_aws_iot
from .socket import connect_socket, send_file_name, receive_file_name, send_file_size, receive_file_size, receive_file
# Placeholder for future development
# from .mqtt import ...
# from .sqlite import ...

# Create a default logger for convenient use throughout the package
logger = get_logger("sdl_utils_default")

# --- Optional Prefect Functionality ---
# Try to import Prefect components, but fail gracefully if not installed
try:
    from .prefect_runtime import is_worker_node
    
    if not is_worker_node():
        # --- Orchestrator-specific functionality (Full Nodes Only) ---
        try:
            from .prefect_orchestrator import run_command_on_worker, request_slack_approval, example_shell_command_flow
            from .slack_bot import slack_client, send_slack_message, ask_for_approval, await_approval_response
            from prefect import flow, task
            
            # Add orchestrator functions to the public API
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
            
        except ImportError:
            # Fails gracefully if 'prefect-full' extras are not installed
            logger.info("Prefect orchestration components not found. Install with 'pip install sdl-utils[prefect-full]' for full orchestration features.")
    
    else:
        # --- Worker Node Functionality ---
        # This can be expanded if worker-specific helper functions are added later
        pass
        
except ImportError:
    # Prefect runtime detection not available - this is fine for basic usage
    logger.info("Prefect components not available. Install with 'pip install sdl-utils[prefect-worker]' or 'pip install sdl-utils[prefect-full]' for Prefect functionality.")

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

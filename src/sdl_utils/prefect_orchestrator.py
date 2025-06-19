from prefect import task, get_run_logger, flow
from prefect.tasks import task_input_hash
from datetime import timedelta
from prefect_shell import ShellTask
from .slack_bot import ask_for_approval, await_approval_response, send_slack_message

# This task will be executed by a worker.
# It uses prefect-shell to run a command in the worker's environment.
run_command_on_worker = ShellTask(
    name="Run Shell Command on Worker",
    helper_script="cd ~", # Example: ensures command runs in home directory
    stream_output=True,
    tags=["worker", "shell"]
)

@task(name="Request Manual Approval via Slack")
def request_slack_approval(prompt: str, channel: str = None) -> str:
    """
    Posts a request for approval to Slack and waits for a response.
    
    Args:
        prompt: The message to display to the user in Slack.
        channel: The Slack channel to post in. Uses default if not set.

    Returns:
        The user's decision ('approved', 'denied', or 'timeout').
    """
    logger = get_run_logger()
    logger.info(f"Sending approval request to Slack: '{prompt}'")
    
    # Send the interactive message
    response_data = ask_for_approval(prompt=prompt, channel=channel)
    if not response_data or 'ts' not in response_data:
        logger.error("Failed to send approval message to Slack.")
        return "error"
        
    message_ts = response_data['ts']
    target_channel = response_data['channel']
    
    logger.info(f"Waiting for approval on message {message_ts} in channel {target_channel}...")
    
    # Wait for the user's reaction
    decision = await_approval_response(message_ts=message_ts, channel=target_channel)
    
    logger.info(f"Received decision from Slack: {decision.upper()}")
    
    return decision

@flow(name="Example Shell Command Flow")
def example_shell_command_flow(command: str):
    """
    A full workflow demonstrating a manual approval step before running
    a shell command on a remote worker.
    """
    approval_decision = request_slack_approval(
        prompt=f"A request has been made to run the command `{command}` on a worker. Please approve or deny."
    )
    
    if approval_decision == "approved":
        send_slack_message(f"Approval received. Submitting task to run `{command}`...")
        run_command_on_worker(command=command)
    elif approval_decision == "denied":
        send_slack_message("Task deployment was denied by user.")
    else: # Covers timeout or error
        send_slack_message("Approval request timed out or failed. Aborting task.",)
        

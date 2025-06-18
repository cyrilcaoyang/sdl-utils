from prefect import task, get_run_logger, flow
from prefect.tasks import task_input_hash
from datetime import timedelta
import subprocess
import json
from .slack_bot import ask_for_approval, await_approval_response, send_slack_message

@task(
    name="Deploy Task to Worker",
    description="Deploys a shell command to a remote worker, with retries, caching, and structured feedback.",
    retries=3,
    retry_delay_seconds=5,
    cache_key_fn=task_input_hash,
    cache_expiration=timedelta(minutes=30),
    tags=["worker", "ssh"]
)
def deploy_task_to_worker(worker_address: str, command_to_run: str):
    """
    Deploys a command to a worker node using SSH and gets structured feedback.

    Args:
        worker_address: The SSH address of the worker (e.g., 'pi@192.168.1.10').
        command_to_run: The shell command to execute on the worker.

    Returns:
        A dictionary containing the parsed JSON feedback from the worker.
    """
    logger = get_run_logger()
    
    # The command on the worker is wrapped by our `worker.py` script to ensure
    # we always get structured JSON output.
    full_command_on_worker = f"python -m sdl_utils.prefect.worker {command_to_run}"
    ssh_command = f"ssh {worker_address} \"{full_command_on_worker}\""
    
    logger.info(f"Executing SSH command to {worker_address}")
    
    try:
        result = subprocess.run(
            ssh_command,
            shell=True,
            check=True,
            capture_output=True,
            text=True
        )
        logger.info(f"Raw successful stdout from worker: {result.stdout}")
        
        try:
            feedback = json.loads(result.stdout)
            logger.info("Successfully parsed structured feedback from worker.")
            if feedback.get("status") != "success":
                logger.warning(f"Worker reported a non-success status: {feedback.get('status')}")
                logger.warning(f"Worker stderr: {feedback.get('stderr')}")
            return feedback
        except json.JSONDecodeError:
            logger.error("Failed to parse JSON from worker stdout.")
            raise ValueError(f"Worker returned non-JSON output: {result.stdout}")

    except subprocess.CalledProcessError as e:
        logger.error(f"SSH command failed with exit code {e.returncode} on worker {worker_address}.")
        # The worker script is designed to print JSON to stdout even on failure.
        try:
            feedback = json.loads(e.stdout)
            logger.warning("Parsed structured error feedback from failed worker run.")
            logger.error(f"Worker stderr: {feedback.get('stderr')}")
            # Raise an exception with the structured feedback to allow Prefect to show it.
            raise Exception(f"Worker task failed: {feedback}") from e
        except json.JSONDecodeError:
            logger.error("Could not parse JSON from worker's error output.")
            logger.error(f"Raw failed stdout: {e.stdout}")
            logger.error(f"Raw failed stderr: {e.stderr}")
            raise e 
        

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

@flow(name="Example Flow with Manual Approval")
def example_approval_flow(worker_address: str, command: str):
    """
    A full workflow demonstrating a manual approval step before deploying a task.
    """
    approval_decision = request_slack_approval(
        prompt=f"A request has been made to run the command `{command}` on worker `{worker_address}`. Please approve or deny."
    )
    
    if approval_decision == "approved":
        send_slack_message(f"Approval received. Deploying task to {worker_address}...")
        deploy_task_to_worker(worker_address=worker_address, command_to_run=command)
    elif approval_decision == "denied":
        send_slack_message("Task deployment was denied by user.")
    else: # Covers timeout or error
        send_slack_message("Approval request timed out or failed. Aborting task.",)
        

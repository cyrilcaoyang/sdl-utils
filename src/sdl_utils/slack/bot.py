import os
import time

try:
    from slack_sdk import WebClient
    from slack_sdk.errors import SlackApiError
except ImportError:
    # Provide a helpful error message if slack_sdk is not installed.
    class WebClient:
        def __init__(self, *args, **kwargs):
            raise ImportError(
                "The 'slack_sdk' package is not installed. "
                "Please install it with the 'full' extras: pip install \"sdl-utils[full]\""
            )
    SlackApiError = type("SlackApiError", (Exception,), {})

# --- Configuration ---
# Fetch the Slack token and default channel from environment variables.
# It's best practice to not hardcode these.
SLACK_BOT_TOKEN = os.environ.get("SLACK_BOT_TOKEN")
DEFAULT_SLACK_CHANNEL = os.environ.get("DEFAULT_SLACK_CHANNEL", "#general")

# Initialize the Slack client globally.
# If the token is not set, client operations will fail gracefully.
slack_client = WebClient(token=SLACK_BOT_TOKEN) if SLACK_BOT_TOKEN else None

def send_slack_message(message: str, channel: str = None) -> dict:
    """Sends a simple text message to a Slack channel."""
    if not slack_client:
        print("Warning: Slack client not initialized. Set SLACK_BOT_TOKEN.")
        return {}
        
    target_channel = channel or DEFAULT_SLACK_CHANNEL
    try:
        response = slack_client.chat_postMessage(channel=target_channel, text=message)
        return response.data
    except SlackApiError as e:
        print(f"Error sending Slack message: {e.response['error']}")
        return {}

def ask_for_approval(prompt: str, channel: str = None) -> dict:
    """
    Sends a message with 'Approve' and 'Deny' buttons to a Slack channel.
    Returns the API response, which includes the message timestamp needed to await a response.
    """
    if not slack_client:
        print("Warning: Slack client not initialized. Set SLACK_BOT_TOKEN.")
        return {}

    target_channel = channel or DEFAULT_SLACK_CHANNEL
    
    block = [
        {
            "type": "section",
            "text": {"type": "mrkdwn", "text": prompt},
        },
        {
            "type": "actions",
            "elements": [
                {"type": "button", "text": {"type": "plain_text", "text": "Approve"}, "style": "primary", "value": "approve"},
                {"type": "button", "text": {"type": "plain_text", "text": "Deny"}, "style": "danger", "value": "deny"},
            ],
        },
    ]
    
    try:
        response = slack_client.chat_postMessage(channel=target_channel, blocks=block)
        return response.data
    except SlackApiError as e:
        print(f"Error sending interactive Slack message: {e.response['error']}")
        return {}

def await_approval_response(message_ts: str, channel: str, timeout_seconds: int = 300) -> str:
    """
    Waits for a user to react to a message with a specific reaction.
    This is a simplified, polling-based way to get feedback.
    
    Returns: 'approved', 'denied', or 'timeout'.
    """
    if not slack_client:
        print("Warning: Slack client not initialized. Set SLACK_BOT_TOKEN.")
        return "timeout"
        
    start_time = time.time()
    while time.time() - start_time < timeout_seconds:
        try:
            result = slack_client.conversations_history(
                channel=channel,
                latest=message_ts,
                inclusive=True,
                limit=1
            )
            message = result['messages'][0]
            if 'reactions' in message:
                for reaction in message['reactions']:
                    if reaction['name'] == '+1': # :+1: emoji means approved
                        return "approved"
                    if reaction['name'] == '-1': # :-1: emoji means denied
                        return "denied"

        except SlackApiError as e:
            print(f"Error checking for Slack reactions: {e.response['error']}")

        time.sleep(5) # Poll every 5 seconds

    return "timeout" 

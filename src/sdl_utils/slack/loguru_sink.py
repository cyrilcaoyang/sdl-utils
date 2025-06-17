from slack_sdk import WebClient
import os

class SlackLoguruSink:
    """A Loguru sink to send log messages to a Slack channel."""
    def __init__(self, token: str, channel: str):
        self.client = WebClient(token=token)
        self.channel = channel

    def __call__(self, message):
        """This method is called by Loguru to process a log record."""
        try:
            # We are interested in the pre-formatted log message
            log_entry = message.strip()
            self.client.chat_postMessage(channel=self.channel, text=log_entry)
        except Exception as e:
            # Avoid crashing the application if logging to Slack fails
            print(f"Error sending log to Slack: {e}")

def get_slack_sink():
    """
    Factory function to create a Slack sink if configured via environment variables.
    Returns the sink instance or None if not configured.
    """
    token = os.environ.get("SLACK_BOT_TOKEN")
    channel = os.environ.get("SLACK_LOGGING_CHANNEL")
    if token and channel:
        return SlackLoguruSink(token=token, channel=channel)
    return None 

from loguru import logger
import sys

# Remove default handler to prevent duplicate logging
logger.remove()

# Add a default console logger
logger.add(sys.stderr, level="INFO")

# --- Optional Slack Integration ---
# Attempt to add a Slack sink for critical error logging if configured.
try:
    from sdl_utils.slack.loguru_sink import get_slack_sink
    slack_sink = get_slack_sink()
    if slack_sink:
        # Add the sink for ERROR level logs and higher
        logger.add(slack_sink, level="ERROR", format="{message}")
        logger.info("Slack logging for ERROR level is configured.")
except ImportError:
    # This is expected if 'full' dependencies are not installed.
    pass
except Exception as e:
    logger.warning(f"Failed to configure Slack logging sink: {e}")

__all__ = ["logger"]
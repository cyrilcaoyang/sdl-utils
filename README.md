# SDL Utils

A comprehensive Python utilities package for self-driving labs, designed to work efficiently on resource-constrained devices like Raspberry Pi Zero.

## Features

- **AWS IoT Integration**: Secure cloud connectivity for IoT devices
  - Optimized for resource-constrained devices

- **Socket Utilities**: File transfer and communication tools
  - File name transfer
  - File size transfer
  - File content transfer
  - Connection management

- **MQTT Client**: Message queuing for IoT devices
  - To be added

- **SQLite Database**: Local data storage
  - To be added

- **Logging System**: Comprehensive logging capabilities
  - Structured logging format
  - Optional Slack integration for critical alerts

- **Prefect Orchestration**: Build robust, observable workflows with human in the loop
  - Separate roles for orchestrators (full computers) and workers (Raspberry Pi).
  - Deploy tasks to workers over SSH.
  - Automatic retries, caching, and structured feedback from workers.
  - Interactive approvals via Slack to add a human-in-the-loop.

## Installation

You can install the package using pip:

```bash
pip install .
```

### Optional Dependencies

This package includes optional features that require extra dependencies. You can install them as needed.

- **Full Orchestration Node**: To run a full Prefect orchestrator, install the `full` extras:
  ```bash
  pip install ".[full]"
  ```

- **Slack Integration**: To enable Slack notifications and interactive approvals, you will need to install the `full` extras (`pip install ".[full]"`) and configure the following environment variables:
  - `SLACK_BOT_TOKEN`: Your Slack app's bot token.
  - `DEFAULT_SLACK_CHANNEL`: The default channel for messages (e.g., `#my-lab-alerts`).
  - `SLACK_LOGGING_CHANNEL`: The specific channel for critical log alerts.

- **Worker Node**: For a lightweight worker node (like a Raspberry Pi Zero), install the `worker` extras:
  ```bash
  pip install ".[worker]"
  ```

## Configuration

Create a `.env` file in your project root with your configuration:

```env
# AWS IoT Configuration
AWS_IOT_ENDPOINT=your_aws_iot_endpoint
AWS_IOT_CLIENT_ID=your_device_id
AWS_IOT_CERT_PATH=path/to/certificate.pem
AWS_IOT_KEY_PATH=path/to/private.key
AWS_IOT_CA_PATH=path/to/root-CA.crt

# MQTT Configuration
MQTT_BROKER=your_mqtt_broker
MQTT_PORT=your_mqtt_port
```

## Usage Examples

### AWS IoT Integration

```python
from sdl_utils import connect_aws_iot, publish_message, subscribe_topic

# Connect to AWS IoT
if connect_aws_iot():
    # Publish a message
    publish_message("lab/status", {"status": "running", "temperature": 25.5})
    
    # Subscribe to a topic
    def on_message(topic, payload):
        print(f"Received message on {topic}: {payload}")
    
    subscribe_topic("lab/commands", on_message)
```

### Socket Communication

```python
from sdl_utils import connect_socket, send_file_name, receive_file

# Server side
server_socket = connect_socket(host='0.0.0.0', port=5000)
send_file_name(server_socket, "data.csv")
send_file(server_socket, "data.csv")

# Client side
client_socket = connect_socket(host='localhost', port=5000)
file_name = receive_file_name(client_socket)
receive_file(client_socket, file_name)
```

### MQTT Communication

```python
from sdl_utils import MQTTClient

mqtt_client = MQTTClient()
mqtt_client.connect()
mqtt_client.publish("lab/status", "experiment_completed")
```

### Database Operations

```python
from sdl_utils import SQLiteDB

db = SQLiteDB("lab_data.db")
db.execute("CREATE TABLE IF NOT EXISTS experiments (id INTEGER PRIMARY KEY, name TEXT)")
db.execute("INSERT INTO experiments (name) VALUES (?)", ("experiment_1",))
```

### Prefect Orchestration

```python
# On your orchestrator machine (e.g., your laptop)
# Make sure to install with: pip install ".[full]"
from sdl_utils import flow, deploy_task_to_worker, request_slack_approval
from sdl_utils import logger

@flow(name="Run Lab Experiment with Approval")
def run_experiment_flow(worker_address: str, command: str):
    """
    This flow requests approval on Slack, and if approved,
    deploys a command to a remote worker.
    """
    logger.info(f"Requesting approval to run '{command}' on {worker_address}")
    
    approval = request_slack_approval(
        prompt=f"Please approve running command: `{command}` on worker `{worker_address}`."
    )

    if approval == "approved":
        logger.info("Approval received. Deploying task...")
        # deploy_task_to_worker is a Prefect @task
        worker_feedback = deploy_task_to_worker(
            worker_address=worker_address,
            command_to_run=command
        )
        logger.info(f"Worker task finished. Feedback: {worker_feedback}")
    else:
        logger.warning(f"Approval was '{approval}'. Task cancelled.")

# To run this flow from Python:
# if __name__ == "__main__":
#     run_experiment_flow(worker_address="pi@192.168.1.42", command="echo 'Hello from worker'")
```

### Logging

The logging module provides two ways to get a logger, ensuring both backward compatibility and access to modern features.

**1. Backward-Compatible File Logger (`get_logger`)**

Use this function when you need to maintain the exact file naming and message format of legacy systems.

```python
from sdl_utils import get_logger

# This creates a log file in ~/Logs/ with the legacy format.
legacy_log = get_logger("my_experiment_logger")
legacy_log.info("This message goes to a specific file.")
```

**2. Modern Console & Slack Logger (`logger`)**

For new development, use the pre-configured `loguru` instance directly. It provides beautiful console output and automatic Slack alerts.

```python
from sdl_utils import logger

# The logger is a pre-configured Loguru instance.
logger.info("This message goes to the console with rich formatting.")
logger.warning("A warning message.")
logger.error("This will be sent to Slack if configured.")
```

## Raspberry Pi Zero Support

This package is specifically optimized for resource-constrained devices like Raspberry Pi Zero:

- Minimal memory footprint
- Built-in retry mechanisms
- No heavy dependencies
- Optimized AWS IoT integration

## Development

To install the package in development mode:

```bash
git clone https://github.com/cyrilcaoyang/sdl-utils.git
cd sdl-utils
pip install -e ".[full]"
```

## License

MIT License

## Author

Yang Cao, Acceleration Consortium

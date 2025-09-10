# SDL Utils

A comprehensive Python utilities package for self-driving labs, designed to work efficiently on resource-constrained devices like Raspberry Pi Zero.

## Features

- **AWS IoT Integration**: Secure cloud connectivity for IoT devices

- **Socket Utilities**: File transfer and communication tools
  - File name transfer, File size transfer, File content transfer
  - Connection management

- **MQTT Client**: Message queuing for IoT devices
  - To be added

- **SQLite Database**: Local data storage
  - To be added

- **Logging System**: Comprehensive logging capabilities
  - Structured logging format
  - Optional Slack integration for critical alerts

- **Prefect Orchestration**: Build robust, observable workflows with human-in-the-loop approvals.
  - **Pull Architecture**: worker pull tasks from a central server, rather than having tasks pushed to them.
  - **Work Pools**: Orchestrate different types of workers (e.g., a pool for Raspberry Pis, a pool for lab servers) using work pools.
  - **Shell Commands**: Seamlessly run any shell command on a worker as part of a workflow.
  - **Interactive Approvals**: Add manual approval steps in your workflows using Slack.

## Installation

### Basic Installation (No Prefect)

For basic functionality without Prefect orchestration:

```bash
pip install .
```

This includes core utilities like logging, AWS IoT, socket communication, and MQTT.

### Prefect Integration Options

This package supports different Prefect installation modes depending on your use case:

- **Full Orchestration Node**: For computers that will orchestrate workflows and send commands to workers:
  ```bash
  pip install ".[prefect-full]"
  ```
  This includes Prefect, prefect-shell, Slack integration, and all orchestration features.

- **Worker Node**: For devices that will execute tasks (like Raspberry Pi Zero/2W):
  ```bash
  pip install ".[prefect-worker]"
  ```
  This includes only the Prefect client needed to receive and execute tasks.

### Slack Integration

To enable Slack notifications and interactive approvals, install the `prefect-full` extras and configure these environment variables:
- `SLACK_BOT_TOKEN`: Your Slack app's bot token.
- `DEFAULT_SLACK_CHANNEL`: The default channel for messages (e.g., `#my-lab-alerts`).
- `SLACK_LOGGING_CHANNEL`: The specific channel for critical log alerts.

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

### Managing Prefect Profiles (Local vs. Cloud)

Prefect's functionality can be directed at either a local server running on your machine or the Prefect Cloud service. The recommended way to manage these two environments is with Prefect Profiles.

The orchestrator (your laptop) and the worker (the Pi) do not need to be on the same profile, but they MUST be pointed at the same server for the system to work. In a production setup, both your laptop and your Pi would be using the cloud profile.

**Step 1: Set Up the `local` Profile**

This profile will be used to interact with a local Prefect server on the same Local Network.

1.  Find your orchestrator's local network IP address (e.g., `192.168.1.101`).
    - On **macOS**: `ipconfig getifaddr en0`
    - On **Windows**: `ipconfig` (look for the "IPv4 Address" under your active network adapter).
    - On **Linux**: `ip -a` or `ifconfig`

2. on your server, ensure the `default` profile is configured for local use.

```bash
# Switch to the default profile (if not already active)
prefect profile use default
prefect config set PREFECT_API_URL=http://127.0.0.1:4200/api
```

To run the local server on Local Network, use the following command in your terminal to make it accessible on the network (0.0.0.0 will work even if your IP changes or if you have multiple network connections):

```bash
prefect server start --host 0.0.0.0
```

3. On the worker machine, repeat step 1, and in step 2, set the API URL to the orchestrator's IP.

```bash
 `prefect config set PREFECT_API_URL="http://192.168.1.101:4200/api"`
```

**Step 2: Set Up the `cloud` Profile**

This profile will connect to your Prefect Cloud workspace. Use the same Prefect Profile for the orchestrator and worker.

```bash
# Create a new profile for your cloud connectionm and switch to it
prefect profile create cloud
prefect profile use cloud

# Log in to Prefect Cloud. This will prompt you to authenticate in your browser.
prefect cloud login
```

That's it!

**Step 3: Switching Between Environments**

Once set up, you can easily switch between your local and cloud environments with a single command before running your flows.

```bash
# Switch to your local server
prefect profile use default

# Switch to Prefect Cloud
prefect profile use cloud
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


### Database Operations



### Prefect Orchestration with Workers

This package uses a "pull" model for orchestration. You define flows on your main machine (orchestrator), and resource-constrained devices (workers) connect to a work pool to pick up and execute tasks.

**Step 1: Create a Work Pool**

First, create a work pool for your workers to connect to. You only need to do this once. A common pattern is to have a pool for a specific type of worker, like all your Raspberry Pis.

From your orchestrator machine (e.g., your laptop), run:

```bash
# This creates a pool of type 'process' that workers can join.
prefect work-pool create "my-pi-pool" --type process
```

**Step 2: Start a Worker**

On your worker machine (e.g., a Raspberry Pi), start a worker and point it to the work pool you created. The worker will poll for tasks to execute.

```bash
# Install the minimal worker dependencies
pip install "sdl-utils[prefect-worker]"

# This command connects the worker to the "my-pi-pool"
prefect worker start --pool "my-pi-pool"
```

**Step 3: Deploy a Flow**

A deployment tells Prefect how to run a flow, including which work pool to send the tasks to. On your orchestrator machine, create a Python file (e.g., `my_deployment.py`):

```python
# my_deployment.py
from sdl_utils import example_shell_command_flow

if __name__ == "__main__":
    example_shell_command_flow.serve(
        name="my-first-deployment",
        work_pool_name="my-pi-pool"
    )
```
Now, run this file to create the deployment on the Prefect server:
```bash
python my_deployment.py
```

**Step 4: Run the Deployed Flow**

You can now trigger a run of this deployment from the Prefect UI, or from the command line:

```bash
prefect deployment run "Example Shell Command Flow/my-first-deployment" -p "command=ls -la"
```

This will run the `example_shell_command_flow`, which will ask for your approval on Slack. If you approve, the `ls -la` command will be sent to the `my-pi-pool`, where your running worker will pick it up and execute it.

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

- **Lightweight Workers**: The worker model allows Pis to run with minimal overhead, simply polling for tasks.
- **Pull Architecture**: Avoids the need for direct SSH access or open ports on the worker devices.
- No heavy dependencies
- Optimized AWS IoT integration

## Development

To install the package in development mode:

```bash
git clone https://github.com/cyrilcaoyang/sdl-utils.git
cd sdl-utils
pip install -e ".[prefect-full]"
```

## License

MIT License

## Author

Yang Cao, Acceleration Consortium

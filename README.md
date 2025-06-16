# SDL Utils

A comprehensive Python utilities package for self-driving labs, designed to work efficiently on resource-constrained devices like Raspberry Pi Zero.

## Features

- **Lightweight Prefect Client**: Workflow management optimized for resource-constrained devices
  - Local state caching
  - Automatic retry mechanism
  - Workflow status tracking
  - Minimal memory footprint

- **AWS IoT Integration**: Secure cloud connectivity for IoT devices
  - Secure SSL/TLS connection
  - Automatic reconnection
  - Message queuing
  - Topic subscription
  - Optimized for resource-constrained devices

- **Socket Utilities**: File transfer and communication tools
  - File name transfer
  - File size transfer
  - File content transfer
  - Connection management

- **MQTT Client**: Message queuing for IoT devices
  - Lightweight implementation
  - Easy integration with lab equipment
  - Reliable message delivery

- **SQLite Database**: Local data storage
  - Efficient data management
  - Thread-safe operations
  - Minimal resource usage

- **Logging System**: Comprehensive logging capabilities
  - Configurable log levels
  - File and console output
  - Structured logging format

## Installation

```bash
pip install sdl-utils
```

## Configuration

Create a `.env` file in your project root with your configuration:

```env
# Prefect Client Configuration
PREFECT_API_URL=your_prefect_api_url
PREFECT_API_KEY=your_prefect_api_key

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

### Workflow Management

```python
from sdl_utils import create_workflow, run_workflow, get_workflow_status

@create_workflow(name="lab_experiment", retries=3)
def run_experiment(temperature, duration):
    # Your experiment code here
    pass

# Run the workflow
workflow_id = run_workflow(run_experiment, temperature=25, duration=60)

# Check status
status = get_workflow_status(workflow_id)
print(f"Workflow status: {status['status']}")
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

### Logging

```python
from sdl_utils import get_logger

logger = get_logger("lab_experiment")
logger.info("Starting experiment")
logger.error("Error occurred", exc_info=True)
```

## Raspberry Pi Zero Support

This package is specifically optimized for resource-constrained devices like Raspberry Pi Zero:

- Minimal memory footprint
- Efficient local storage
- Built-in retry mechanisms
- No heavy dependencies
- Compatible with ARM architecture
- Optimized AWS IoT integration

## Development

To install the package in development mode:

```bash
git clone https://github.com/cyrilcaoyang/sdl-utils.git
cd sdl-utils
pip install -e .
```

## License

MIT License

## Author

Yang Cao, Acceleration Consortium

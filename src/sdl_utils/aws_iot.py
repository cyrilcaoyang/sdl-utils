"""
AWS IoT client for SDL devices
Author: Yang Cao, Acceleration Consortium
Version: 0.1

A lightweight AWS IoT client implementation for managing device connections and messaging.
"""

import os
import json
import time
import logging
from typing import Optional, Callable, Dict, Any
from pathlib import Path
import ssl
import paho.mqtt.client as mqtt
from paho.mqtt.client import MQTTMessage

class AWSIoTClient:
    """Lightweight AWS IoT client for resource-constrained devices."""
    
    def __init__(
        self,
        endpoint: Optional[str] = None,
        port: int = 8883,
        client_id: Optional[str] = None,
        cert_path: Optional[Path] = None,
        key_path: Optional[Path] = None,
        ca_path: Optional[Path] = None,
        max_retries: int = 3,
        retry_delay: int = 5
    ):
        """Initialize the AWS IoT client.
        
        Args:
            endpoint: AWS IoT endpoint (defaults to AWS_IOT_ENDPOINT env var)
            port: AWS IoT port (defaults to 8883)
            client_id: Client ID (defaults to device hostname)
            cert_path: Path to certificate file
            key_path: Path to private key file
            ca_path: Path to CA certificate file
            max_retries: Maximum number of retry attempts
            retry_delay: Delay between retries in seconds
        """
        self.endpoint = endpoint or os.getenv("AWS_IOT_ENDPOINT")
        self.port = port
        self.client_id = client_id or os.getenv("AWS_IOT_CLIENT_ID", os.uname().nodename)
        self.cert_path = cert_path or Path(os.getenv("AWS_IOT_CERT_PATH", "cert.pem"))
        self.key_path = key_path or Path(os.getenv("AWS_IOT_KEY_PATH", "private.key"))
        self.ca_path = ca_path or Path(os.getenv("AWS_IOT_CA_PATH", "root-CA.crt"))
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        
        # Setup logging
        self.logger = logging.getLogger("aws_iot")
        self.logger.setLevel(logging.INFO)
        
        # Initialize MQTT client
        self.client = mqtt.Client(client_id=self.client_id)
        self.client.on_connect = self._on_connect
        self.client.on_disconnect = self._on_disconnect
        self.client.on_message = self._on_message
        self.client.on_publish = self._on_publish
        
        # Message handlers
        self.message_handlers: Dict[str, Callable] = {}
        
        # Connection state
        self.connected = False
        self.connection_error = None

    def connect(self) -> bool:
        """Connect to AWS IoT with retry logic."""
        if not self._validate_config():
            return False
            
        for attempt in range(self.max_retries):
            try:
                self._setup_ssl()
                self.client.connect(self.endpoint, self.port, keepalive=60)
                self.client.loop_start()
                return True
            except Exception as e:
                self.connection_error = str(e)
                if attempt == self.max_retries - 1:
                    self.logger.error(f"Failed to connect after {self.max_retries} attempts: {str(e)}")
                    return False
                self.logger.warning(f"Connection attempt {attempt + 1} failed, retrying in {self.retry_delay} seconds...")
                time.sleep(self.retry_delay)
        return False

    def disconnect(self) -> None:
        """Disconnect from AWS IoT."""
        if self.connected:
            self.client.loop_stop()
            self.client.disconnect()
            self.connected = False

    def publish(self, topic: str, message: Any, qos: int = 0) -> bool:
        """Publish a message to a topic."""
        if not self.connected:
            self.logger.error("Not connected to AWS IoT")
            return False
            
        try:
            if not isinstance(message, str):
                message = json.dumps(message)
            result = self.client.publish(topic, message, qos=qos)
            return result.rc == mqtt.MQTT_ERR_SUCCESS
        except Exception as e:
            self.logger.error(f"Failed to publish message: {str(e)}")
            return False

    def subscribe(self, topic: str, callback: Callable[[str, Any], None], qos: int = 0) -> bool:
        """Subscribe to a topic with a callback function."""
        if not self.connected:
            self.logger.error("Not connected to AWS IoT")
            return False
            
        try:
            self.message_handlers[topic] = callback
            result = self.client.subscribe(topic, qos=qos)
            return result[0] == mqtt.MQTT_ERR_SUCCESS
        except Exception as e:
            self.logger.error(f"Failed to subscribe to topic: {str(e)}")
            return False

    def _validate_config(self) -> bool:
        """Validate the AWS IoT configuration."""
        if not self.endpoint:
            self.logger.error("AWS IoT endpoint not configured")
            return False
            
        if not self.cert_path.exists():
            self.logger.error(f"Certificate file not found: {self.cert_path}")
            return False
            
        if not self.key_path.exists():
            self.logger.error(f"Private key file not found: {self.key_path}")
            return False
            
        if not self.ca_path.exists():
            self.logger.error(f"CA certificate file not found: {self.ca_path}")
            return False
            
        return True

    def _setup_ssl(self) -> None:
        """Setup SSL context for secure connection."""
        self.client.tls_set(
            ca_certs=str(self.ca_path),
            certfile=str(self.cert_path),
            keyfile=str(self.key_path),
            cert_reqs=ssl.CERT_REQUIRED,
            tls_version=ssl.PROTOCOL_TLSv1_2,
            ciphers=None
        )

    def _on_connect(self, client: mqtt.Client, userdata: Any, flags: Dict, rc: int) -> None:
        """Handle connection events."""
        if rc == 0:
            self.connected = True
            self.connection_error = None
            self.logger.info("Connected to AWS IoT")
        else:
            self.connected = False
            self.connection_error = f"Connection failed with code {rc}"
            self.logger.error(self.connection_error)

    def _on_disconnect(self, client: mqtt.Client, userdata: Any, rc: int) -> None:
        """Handle disconnection events."""
        self.connected = False
        if rc != 0:
            self.logger.warning(f"Unexpected disconnection with code {rc}")

    def _on_message(self, client: mqtt.Client, userdata: Any, message: MQTTMessage) -> None:
        """Handle incoming messages."""
        try:
            topic = message.topic
            payload = message.payload.decode()
            try:
                payload = json.loads(payload)
            except json.JSONDecodeError:
                pass
                
            if topic in self.message_handlers:
                self.message_handlers[topic](topic, payload)
        except Exception as e:
            self.logger.error(f"Error processing message: {str(e)}")

    def _on_publish(self, client: mqtt.Client, userdata: Any, mid: int) -> None:
        """Handle successful message publishing."""
        self.logger.debug(f"Message {mid} published successfully")

# Create default client instance
aws_iot_client = AWSIoTClient()

# Convenience functions
def connect_aws_iot() -> bool:
    """Connect to AWS IoT."""
    return aws_iot_client.connect()

def disconnect_aws_iot() -> None:
    """Disconnect from AWS IoT."""
    aws_iot_client.disconnect()

def publish_message(topic: str, message: Any, qos: int = 0) -> bool:
    """Publish a message to a topic."""
    return aws_iot_client.publish(topic, message, qos=qos)

def subscribe_topic(topic: str, callback: Callable[[str, Any], None], qos: int = 0) -> bool:
    """Subscribe to a topic with a callback function."""
    return aws_iot_client.subscribe(topic, callback, qos=qos) 
"""
Prefect client configured for SDL workflows on resource-constrained devices
Author: Yang Cao, Acceleration Consortium
Version: 0.1

A lightweight client implementation for managing workflows on devices like Raspberry Pi Zero.
"""

import os
import json
import time
from pathlib import Path
from typing import Any, Callable, Optional, Dict
from datetime import datetime
import requests
from requests.exceptions import RequestException
import logging

class PrefectClient:
    """Lightweight Prefect client for managing workflows on resource-constrained devices."""
    
    def __init__(
        self,
        api_url: Optional[str] = None,
        api_key: Optional[str] = None,
        cache_dir: Optional[Path] = None,
        max_retries: int = 3,
        retry_delay: int = 5
    ):
        """Initialize the Prefect client.
        
        Args:
            api_url: Prefect API URL (defaults to PREFECT_API_URL env var)
            api_key: Prefect API key (defaults to PREFECT_API_KEY env var)
            cache_dir: Directory for caching workflow states
            max_retries: Maximum number of retry attempts
            retry_delay: Delay between retries in seconds
        """
        self.api_url = api_url or os.getenv("PREFECT_API_URL")
        self.api_key = api_key or os.getenv("PREFECT_API_KEY")
        self.cache_dir = cache_dir or Path.home() / ".sdl_prefect" / "cache"
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        
        # Create cache directory
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        # Setup logging
        self.logger = logging.getLogger("prefect_client")
        self.logger.setLevel(logging.INFO)
        
        if not self.api_url or not self.api_key:
            self.logger.warning("Prefect API URL or key not set. Some features may be limited.")

    def create_workflow(self, name: str, retries: int = 3) -> Callable:
        """Decorator to create a workflow with retry capabilities."""
        def decorator(func: Callable) -> Callable:
            @wraps(func)
            def wrapper(*args, **kwargs):
                workflow_id = f"{name}_{int(time.time())}"
                try:
                    result = func(*args, **kwargs)
                    self._save_workflow_state(workflow_id, "completed", args, kwargs, result)
                    return result
                except Exception as e:
                    self._save_workflow_state(workflow_id, "failed", args, kwargs, error=str(e))
                    raise e
            return wrapper
        return decorator

    def run_workflow(self, workflow_func: Callable, *args, **kwargs) -> Any:
        """Run a workflow with state caching and retry logic."""
        for attempt in range(self.max_retries):
            try:
                return workflow_func(*args, **kwargs)
            except Exception as e:
                if attempt == self.max_retries - 1:
                    self.logger.error(f"Workflow failed after {self.max_retries} attempts: {str(e)}")
                    raise e
                self.logger.warning(f"Attempt {attempt + 1} failed, retrying in {self.retry_delay} seconds...")
                time.sleep(self.retry_delay)

    def retry_workflow(self, workflow_id: str, max_retries: Optional[int] = None) -> Any:
        """Retry a failed workflow from its cached state."""
        state = self._load_workflow_state(workflow_id)
        if not state:
            raise FileNotFoundError(f"No cached state found for workflow {workflow_id}")

        max_attempts = max_retries or self.max_retries
        for attempt in range(max_attempts):
            try:
                result = self.run_workflow(
                    state["func"],
                    *state["args"],
                    **state["kwargs"]
                )
                self._update_workflow_state(workflow_id, "completed", result=result)
                return result
            except Exception as e:
                if attempt == max_attempts - 1:
                    self.logger.error(f"Workflow retry failed after {max_attempts} attempts: {str(e)}")
                    raise e
                self.logger.warning(f"Retry attempt {attempt + 1} failed, retrying in {self.retry_delay} seconds...")
                time.sleep(self.retry_delay)

    def get_workflow_status(self, workflow_id: str) -> Dict[str, Any]:
        """Get the current status of a workflow."""
        state = self._load_workflow_state(workflow_id)
        if not state:
            return {"status": "not_found"}
        return {
            "status": state["status"],
            "last_updated": state["timestamp"],
            "error": state.get("error")
        }

    def _save_workflow_state(
        self,
        workflow_id: str,
        status: str,
        args: tuple,
        kwargs: dict,
        result: Any = None,
        error: Optional[str] = None
    ) -> None:
        """Save workflow state to cache."""
        state = {
            "status": status,
            "timestamp": datetime.now().isoformat(),
            "args": args,
            "kwargs": kwargs,
            "result": result,
            "error": error
        }
        
        cache_file = self.cache_dir / f"{workflow_id}.json"
        with open(cache_file, "w") as f:
            json.dump(state, f)

    def _load_workflow_state(self, workflow_id: str) -> Optional[Dict[str, Any]]:
        """Load workflow state from cache."""
        cache_file = self.cache_dir / f"{workflow_id}.json"
        if not cache_file.exists():
            return None
            
        with open(cache_file, "r") as f:
            return json.load(f)

    def _update_workflow_state(self, workflow_id: str, status: str, **updates) -> None:
        """Update workflow state in cache."""
        state = self._load_workflow_state(workflow_id)
        if state:
            state.update({"status": status, "timestamp": datetime.now().isoformat(), **updates})
            self._save_workflow_state(workflow_id, **state)

# Create default client instance
prefect_client = PrefectClient()

# Convenience functions
def create_workflow(name: str, retries: int = 3) -> Callable:
    """Create a workflow with retry capabilities."""
    return prefect_client.create_workflow(name, retries=retries)

def run_workflow(workflow_func: Callable, *args, **kwargs) -> Any:
    """Run a workflow with state caching."""
    return prefect_client.run_workflow(workflow_func, *args, **kwargs)

def retry_workflow(workflow_id: str, max_retries: Optional[int] = None) -> Any:
    """Retry a failed workflow from its cached state."""
    return prefect_client.retry_workflow(workflow_id, max_retries=max_retries)

def get_workflow_status(workflow_id: str) -> Dict[str, Any]:
    """Get the current status of a workflow."""
    return prefect_client.get_workflow_status(workflow_id) 
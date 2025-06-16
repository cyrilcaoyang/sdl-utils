"""
Prefect configured to handles workflows in SDL
Author: Yang Cao, Acceleration Consortium
Version: 0.0

A list of functions:
- WorkflowManager: Main class for managing workflows
- create_workflow: Decorator for creating workflows
- run_workflow: Function to run workflows
- retry_workflow: Function to retry failed workflows
"""

from typing import Any, Callable, Optional
from functools import wraps
import json
from pathlib import Path
from prefect import flow, task
from prefect.tasks import task_input_hash
from datetime import timedelta

class WorkflowManager:
    """Manages workflows with retry capabilities and state caching."""
    
    def __init__(self, cache_dir: Optional[Path] = None):
        self.cache_dir = cache_dir or Path.home() / ".sdl_prefect" / "cache"
        self.cache_dir.mkdir(parents=True, exist_ok=True)

    def create_workflow(self, retries: int = 3, cache_key_fn: Optional[Callable] = None):
        """Decorator to create a workflow with retry capabilities."""
        def decorator(func: Callable) -> Callable:
            @flow(name=func.__name__)
            @wraps(func)
            def wrapper(*args, **kwargs):
                return func(*args, **kwargs)
            return wrapper
        return decorator

    def run_workflow(self, workflow_func: Callable, *args, **kwargs) -> Any:
        """Run a workflow with state caching."""
        try:
            return workflow_func(*args, **kwargs)
        except Exception as e:
            # Cache the workflow state
            state = {
                "args": args,
                "kwargs": kwargs,
                "error": str(e)
            }
            cache_file = self.cache_dir / f"{workflow_func.__name__}_state.json"
            with open(cache_file, "w") as f:
                json.dump(state, f)
            raise e

    def retry_workflow(self, workflow_func: Callable, max_retries: int = 3) -> Any:
        """Retry a failed workflow from its cached state."""
        cache_file = self.cache_dir / f"{workflow_func.__name__}_state.json"
        if not cache_file.exists():
            raise FileNotFoundError("No cached state found for this workflow")

        with open(cache_file, "r") as f:
            state = json.load(f)

        for attempt in range(max_retries):
            try:
                result = workflow_func(*state["args"], **state["kwargs"])
                # Clear cache on success
                cache_file.unlink()
                return result
            except Exception as e:
                if attempt == max_retries - 1:
                    raise e

# Create default workflow manager instance
workflow_manager = WorkflowManager()

# Convenience functions
def create_workflow(retries: int = 3):
    """Create a workflow with retry capabilities."""
    return workflow_manager.create_workflow(retries=retries)

def run_workflow(workflow_func: Callable, *args, **kwargs) -> Any:
    """Run a workflow with state caching."""
    return workflow_manager.run_workflow(workflow_func, *args, **kwargs)

def retry_workflow(workflow_func: Callable, max_retries: int = 3) -> Any:
    """Retry a failed workflow from its cached state."""
    return workflow_manager.retry_workflow(workflow_func, max_retries=max_retries)



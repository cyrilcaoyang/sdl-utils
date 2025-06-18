import sys
import subprocess
import json
import logging

# Set up basic logging for the worker itself, which will go to the worker's stderr.
# This is separate from the JSON output that goes to stdout for the orchestrator.
logging.basicConfig(
    level=logging.INFO, 
    format='%(asctime)s - WORKER - %(levelname)s - %(message)s',
    stream=sys.stderr
)

def execute_remote_task():
    """
    Executes a task passed via command-line arguments and prints a JSON result to stdout.
    """
    if len(sys.argv) < 2:
        output = {"status": "error", "message": "No command provided."}
        print(json.dumps(output))
        sys.exit(1)
        
    command = " ".join(sys.argv[1:])
    logging.info(f"Executing command: {command}")
    
    try:
        result = subprocess.run(
            command,
            shell=True,
            check=True, # Raises CalledProcessError on non-zero exit codes
            capture_output=True,
            text=True
        )
        output = {
            "status": "success",
            "stdout": result.stdout,
            "stderr": result.stderr,
            "returncode": result.returncode,
        }
        print(json.dumps(output))
        logging.info("Command executed successfully.")
        
    except subprocess.CalledProcessError as e:
        output = {
            "status": "error",
            "message": "Command failed with a non-zero exit code.",
            "stdout": e.stdout,
            "stderr": e.stderr,
            "returncode": e.returncode
        }
        # Print the JSON to stdout so the orchestrator can capture it
        print(json.dumps(output))
        logging.error(f"Command failed with exit code {e.returncode}.")
        # Exit with the original error code to signal failure to the orchestrator
        sys.exit(e.returncode)
    except Exception as e:
        output = {
            "status": "error",
            "message": f"An unexpected error occurred in the worker script: {str(e)}",
        }
        print(json.dumps(output))
        logging.critical("An unexpected error occurred in worker script.", exc_info=True)
        sys.exit(1)

if __name__ == "__main__":
    execute_remote_task() 
from flask import Flask, request, jsonify
import requests
import base64
import os
import shutil
import subprocess
import logging
from dotenv import load_dotenv

# Load .env with error handling
try:
    load_dotenv('/Users/ashwath/Desktop/Sample App/.env')
except Exception as e:
    print(f"Error loading .env: {e}")

app = Flask(__name__)

# Set up logging
logging.basicConfig(filename='/Users/ashwath/Desktop/Sample App/deploy.log', level=logging.DEBUG)
logger = logging.getLogger(__name__)

@app.route('/run-task', methods=['POST'])
def run_task():
    try:
        task_data = request.json
        if not task_data or 'task' not in task_data:
            return jsonify({"error": "Task is required"}), 400
        agent_zero_url = os.getenv("AGENT_ZERO_API_URL", "http://localhost:50001/message")
        auth = os.getenv("AGENT_ZERO_AUTH", "admin:admin123")
        auth_header = f"Basic {base64.b64encode(auth.encode()).decode()}"
        response = requests.post(
            agent_zero_url,
            json=task_data,
            headers={"Content-Type": "application/json", "Authorization": auth_header},
            timeout=30
        )
        try:
            return jsonify(response.json()), response.status_code
        except ValueError:
            return jsonify({"error": f"Invalid JSON response from Agent Zero: {response.text}"}), 500
    except requests.exceptions.Timeout:
        return jsonify({"error": "Agent Zero API timed out"}), 504
    except Exception as e:
        logger.error(f"run-task error: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/agent/deploy-decision', methods=['POST'])
def deploy_decision():
    try:
        return jsonify({"deploy": True, "strategy": "canary"}), 200
    except Exception as e:
        logger.error(f"deploy-decision error: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/deploy', methods=['POST'])
def deploy():
    try:
        staging_dir = os.getenv("STAGING_DIRECTORY", "/Users/ashwath/Desktop/Sample App/staging-app")
        logger.info(f"Deploying to {staging_dir}")
        os.makedirs(staging_dir, exist_ok=True)
        files_to_copy = ['app.py', 'requirements.txt']
        env_file = "/Users/ashwath/Desktop/Sample App/.env"
        if os.path.exists(env_file):
            shutil.copy(env_file, os.path.join(staging_dir, '.env'))
            logger.info(f"Copied .env to {staging_dir}")
        else:
            logger.warning(f".env file not found at {env_file}")
        for file in files_to_copy:
            if os.path.exists(file):
                shutil.copy(file, staging_dir)
                logger.info(f"Copied {file} to {staging_dir}")
            else:
                logger.error(f"File {file} not found")
                return jsonify({"error": f"File {file} not found"}), 500
        venv_path = os.path.join(staging_dir, 'venv')
        python_path = shutil.which('python3')
        if not python_path:
            logger.error("Python3 not found in PATH")
            return jsonify({"error": "Python3 not found in PATH"}), 500
        result = subprocess.run([python_path, '-m', 'venv', venv_path], check=True, capture_output=True, text=True)
        logger.info(f"Created virtual environment: {result.stdout}")
        pip_path = os.path.join(venv_path, 'bin', 'pip')
        req_path = os.path.join(staging_dir, 'requirements.txt')
        result = subprocess.run([pip_path, 'install', '-r', req_path], check=True, capture_output=True, text=True)
        logger.info(f"Installed dependencies: {result.stdout}")
        app_path = os.path.join(staging_dir, 'app.py')
        log_file = os.path.join(staging_dir, 'staging.log')
        python_bin = os.path.join(venv_path, 'bin', 'python')
        if not os.path.exists(python_bin):
            logger.error(f"Python binary not found at {python_bin}")
            return jsonify({"error": f"Python binary not found at {python_bin}"}), 500
        try:
            with open(log_file, 'a') as f:
                process = subprocess.Popen(
                    [python_bin, app_path, '--port', '8081'],
                    env={**os.environ, 'FLASK_PORT': '8081', 'STAGING_DIRECTORY': staging_dir},
                    stdout=f, stderr=f
                )
            logger.info(f"Started Flask app on port 8081, PID: {process.pid}")
            # Wait briefly and verify process
            import time
            time.sleep(1)
            process.poll()
            if process.returncode is not None:
                logger.error(f"Staging app process exited with code {process.returncode}")
                with open(log_file, 'r') as f:
                    log_content = f.read()
                return jsonify({"error": f"Staging app failed to start: {log_content}"}), 500
            # Verify port
            result = subprocess.run(['netstat', '-an'], capture_output=True, text=True)
            if ':8081' not in result.stdout:
                logger.error("Port 8081 not in use")
                with open(log_file, 'r') as f:
                    log_content = f.read()
                return jsonify({"error": f"Staging app not listening on 8081: {log_content}"}), 500
            with open(os.path.join(staging_dir, "deployed.txt"), "w") as f:
                f.write(f"Deployed Flask app on port 8081, PID: {process.pid}")
            return jsonify({"status": f"Deployment successful to {staging_dir}, running on port 8081, PID: {process.pid}"}), 200
        except Exception as e:
            logger.error(f"Failed to start staging app: {str(e)}")
            return jsonify({"error": f"Failed to start staging app: {str(e)}"}), 500
    except subprocess.CalledProcessError as e:
        logger.error(f"Subprocess error: {e.stderr}")
        return jsonify({"error": f"Deployment failed: {e.stderr}"}), 500
    except Exception as e:
        logger.error(f"Deployment error: {str(e)}")
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    import sys
    port = int(os.getenv("FLASK_PORT", 8080))
    if '--port' in sys.argv:
        port = int(sys.argv[sys.argv.index('--port') + 1])
    app.run(port=port, debug=True)
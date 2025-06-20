from flask import Flask, request, jsonify
import requests
import base64
import os
from dotenv import load_dotenv
load_dotenv()

app = Flask(__name__)

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
            timeout=10  # Add timeout
        )
        return jsonify(response.json()), response.status_code
    except requests.exceptions.Timeout:
        return jsonify({"error": "Agent Zero API timed out"}), 504
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/agent/deploy-decision', methods=['POST'])
def deploy_decision():
    try:
        return jsonify({"deploy": True, "strategy": "canary"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/deploy', methods=['POST'])
def deploy():
    try:
        staging_dir = os.getenv("STAGING_DIRECTORY", "/Users/ashwath/Desktop/Sample App/staging-app")
        os.makedirs(staging_dir, exist_ok=True)
        with open(os.path.join(staging_dir, "deployed.txt"), "w") as f:
            f.write("Deployed")
        return jsonify({"status": f"Deployment successful to {staging_dir}"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    port = int(os.getenv("FLASK_PORT", 8080))
    app.run(port=port, debug=True)
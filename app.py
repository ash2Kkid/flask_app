from flask import Flask, request, jsonify
from agent_zero import Agent

app = Flask(__name__)

# Create a real Agent-Zero agent
agent = Agent(
    name="deployment-strategist",
    system_prompt="You decide whether to deploy based on test results."
)

# Register tool with the agent
@agent.tool
def deploy_decision(test_status: str) -> dict:
    return {
        "deploy": test_status == "passed",
        "strategy": "canary" if test_status == "passed" else "none"
    }

# Flask endpoint that GitHub will call
@app.route("/agent/deploy-decision", methods=["POST"])
def decision():
    data = request.get_json()
    result = agent.call_tool("deploy_decision", data["test_status"])
    return jsonify(result)

# Optional: landing page for browser
@app.route("/")
def index():
    return "✅ Agent-Zero is active."

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)

from flask import Flask, jsonify, request

app = Flask(__name__)

@app.route('/')
def home():
    return "Hello, Agent-Zero!"

@app.route('/agent/deploy-decision', methods=['POST'])
def deploy_decision():
    data = request.json
    test_status = data.get("test_status", "failed")

    if test_status == "passed":
        return jsonify({"deploy": True, "strategy": "canary"})
    else:
        return jsonify({"deploy": False, "reason": "Tests failed"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)

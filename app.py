from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route("/agent/deploy-decision", methods=["POST"])
def deploy_decision():
    try:
        data = request.get_json()
        print("Received JSON:", data)  # Debug

        test_status = data.get("test_status", "failed")

        if test_status == "passed":
            return jsonify({"deploy": True, "strategy": "canary"})
        else:
            return jsonify({"deploy": False, "strategy": "none"})
    except Exception as e:
        print("Error:", str(e))
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)

from app import app

def test_agent_decision():
    tester = app.test_client()
    response = tester.post('/agent/deploy-decision', json={"test_status": "passed"})
    assert response.status_code == 200
    assert response.json["deploy"] is True
    assert response.json["strategy"] == "canary"

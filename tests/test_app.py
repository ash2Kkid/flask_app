from flask import Flask
import pytest

@pytest.fixture
def client():
    from app import app
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_home(client):
    response = client.get('/')
    assert response.status_code == 200
    assert b"Welcome to the Flask App with Agent-Zero!" in response.data

def test_run_task_missing_task(client):
    response = client.post('/run-task', json={})
    assert response.status_code == 400
    assert b"Missing 'task' in request body" in response.data

def test_agent_decision(client):
    response = client.post('/agent/deploy-decision', json={"test_status": "passed"})
    assert response.status_code == 200
    assert response.json["deploy"] is True
    assert response.json["strategy"] == "canary"
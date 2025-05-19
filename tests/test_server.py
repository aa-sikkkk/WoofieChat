import pytest
import sys
import os

# Add the project root directory to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi.testclient import TestClient
from server import app
import json

client = TestClient(app)

def test_root_endpoint():
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["service"] == "woofie-chat"

def test_chat_endpoint_options():
    response = client.options("/api/chat")
    assert response.status_code == 200
    assert "Access-Control-Allow-Origin" in response.headers
    assert "Access-Control-Allow-Methods" in response.headers
    assert "Access-Control-Allow-Headers" in response.headers

def test_chat_endpoint_get():
    response = client.get("/api/chat")
    assert response.status_code == 405
    data = response.json()
    assert "error" in data
    assert "message" in data
    assert "Method Not Allowed" in data["error"]

def test_chat_endpoint_post_empty():
    response = client.post("/api/chat", json={"message": ""})
    assert response.status_code == 200
    data = response.json()
    assert "response" in data
    assert "confidence" in data
    assert "source" in data
    assert isinstance(data["confidence"], float)
    assert isinstance(data["response"], str)

def test_chat_endpoint_post_valid():
    response = client.post("/api/chat", json={"message": "How to train a dog?"})
    assert response.status_code == 200
    data = response.json()
    assert "response" in data
    assert "confidence" in data
    assert "source" in data
    assert isinstance(data["confidence"], float)
    assert isinstance(data["response"], str)
    assert 0 <= data["confidence"] <= 1

def test_chat_endpoint_post_invalid_json():
    response = client.post("/api/chat", data="invalid json")
    assert response.status_code == 422

def test_chat_endpoint_post_missing_message():
    response = client.post("/api/chat", json={})
    assert response.status_code == 422

def test_chat_endpoint_post_long_message():
    long_message = "?" * 1000  # Create a very long message
    response = client.post("/api/chat", json={"message": long_message})
    assert response.status_code == 200
    data = response.json()
    assert "response" in data
    assert "confidence" in data
    assert "source" in data

@pytest.mark.parametrize("message,expected_keywords", [
    ("How to feed a dog?", ["food", "diet", "feeding"]),
    ("Is my cat sick?", ["health", "veterinarian", "sick"]),
    ("Training tips for birds", ["training", "behavior", "tips"]),
    ("Fish tank setup", ["setup", "aquarium", "tank"]),
    ("Hamster care guide", ["care", "guide", "maintenance"])
])
def test_chat_endpoint_various_queries(message, expected_keywords):
    response = client.post("/api/chat", json={"message": message})
    assert response.status_code == 200
    data = response.json()
    assert "response" in data
    response_text = data["response"].lower()
    # Check if at least one of the expected keywords is in the response
    assert any(keyword in response_text for keyword in expected_keywords) 
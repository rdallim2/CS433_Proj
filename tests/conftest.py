import pytest
from app import app
from unittest.mock import patch

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_index(client):
    with patch('app.message_history', []):
        response = client.get('/')
        assert  response.status_code == 200
        assert b"Welcome to DP-433" in response.data
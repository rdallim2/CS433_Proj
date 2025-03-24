import pytest
from app import app
import json
from unittest.mock import patch, MagicMock

def test_index(client):
    with patch('app.message_history', []):
        response = client.get('/')
        assert  response.status_code == 200
        assert b"Welcome to DP-433" in response.data

@patch('app.pc.Index')
def test_update_data(mock_index,  client):
    mock_index_instance = MagicMock()
    mock_index.return_value = mock_index_instance
    
    test_data = {
        'id': '123',
        'text': 'test text'
    }
    

    response = client.post(
        '/update_data',
        data=json.dumps(test_data),
        content_type='application/json'
    )

    assert response.status_code == 200
    assert mock_index_instance.upsert.called

def test_set_level(client):
    data = {'level': 3}
    response = client.post(
        '/set_level',
        json = data
    )

    assert response.status_code == 200
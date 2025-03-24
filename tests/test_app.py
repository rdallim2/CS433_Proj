import pytest
from app import *
import json
from pinecone import ServerlessSpec
from p_db import *
from unittest.mock import Mock, patch, MagicMock

def test_index(client):
    with patch('app.message_history', []):
        response = client.get('/')
        assert  response.status_code == 200
        assert b"Welcome to DP-433" in response.data


@patch("app.get_embedding")  # Mock the embedding function
@patch("app.pc.Index")  # Mock Pinecone Index
def test_update_data(mock_index, mock_get_embedding, client):

    mock_get_embedding.return_value = [0.1, 0.2, 0.3]

    mock_index_instance = MagicMock()
    mock_index.return_value = mock_index_instance

    test_data = {
        "id": "123",
        "text": "Test text"
    }

    response = client.post('/update_data', data=json.dumps(test_data), content_type='application/json')

    assert response.status_code == 200
    response_json = response.get_json()
    assert response_json == {
        "message": "Update successful",
        "id": "123",
        "text": "Test text",
        "namespace": "ns1"
    }

    mock_get_embedding.assert_called_once_with("Test text")

    mock_index_instance.upsert.assert_called_once_with(
        vectors=[{
            "id": "123",
            "values": [0.1, 0.2, 0.3], 
            "metadata": {"text": "Test text"}
        }],
        namespace="ns1"
    )


def test_set_level(client):
    data = {'level': 3}
    response = client.post(
        '/set_level',
        json = data
    )

    assert response.status_code == 200


@patch('app.pc.Index')
def test_get_data(mock_index, client):
    mock_index_instance = MagicMock()
    mock_index.return_value = mock_index_instance


    # Mock query response from Pinecone
    mock_index_instance.fetch.return_value = MagicMock(
        vectors={
            "vec1": MagicMock(metadata={"text": "First vector"}),
            "vec2": MagicMock(metadata={"text": "Second vector"}),
            "vec3": MagicMock(metadata={"text": "Third vector"}),
        }
    )

    # Send POST request to /get_data
    response = client.post('/get_data')

    # Check response status code and JSON content
    assert response.status_code == 200
    response_json = response.get_json()
    assert response_json == {
        "data": [
            {"id": "vec1", "text": "First vector"},
            {"id": "vec2", "text": "Second vector"},
            {"id": "vec3", "text": "Third vector"},
        ]
    }

    # Ensure fetch was called with the correct parameters
    mock_index_instance.fetch.assert_called_once_with(
        ids=["vec1", "vec2", "vec3", "vec4", "vec5", "vec6", "vec7", "vec8", "vec9", "vec10"],
        namespace="ns1"
    )
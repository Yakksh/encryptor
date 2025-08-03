import pytest
from fastapi.testclient import TestClient
from cryptography.fernet import Fernet
import json

from main import app

client = TestClient(app)

def test_root_endpoint():
    """Test the root endpoint"""
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Fernet Encryptor API is running"}

def test_generate_key():
    """Test key generation endpoint"""
    response = client.post("/generate-key")
    assert response.status_code == 200

    data = response.json()
    assert "key" in data

    # Verify the key can be used to create a Fernet instance
    key = data["key"].encode()
    fernet = Fernet(key)  # Should not raise an exception

def test_encrypt_message_without_key():
    """Test encrypting a message without providing a key"""
    message = "Hello, World!"
    response = client.post("/encrypt", json={"message": message})

    assert response.status_code == 200
    data = response.json()

    assert "encrypted_message" in data
    assert "key" in data
    assert data["encrypted_message"] != message  # Should be encrypted

    # Verify the key format
    key = data["key"].encode()
    fernet = Fernet(key)  # Should not raise an exception

def test_encrypt_message_with_key():
    """Test encrypting a message with a provided key"""
    # Generate a key first
    key_response = client.post("/generate-key")
    key = key_response.json()["key"]

    message = "Hello with existing key!"
    response = client.post("/encrypt", json={"message": message, "key": key})

    assert response.status_code == 200
    data = response.json()

    assert "encrypted_message" in data
    assert "key" in data
    assert data["key"] == key  # Should return the same key
    assert data["encrypted_message"] != message  # Should be encrypted

def test_encrypt_message_with_invalid_key():
    """Test encrypting a message with an invalid key"""
    message = "Hello, World!"
    invalid_key = "invalid-key"

    response = client.post("/encrypt", json={"message": message, "key": invalid_key})
    assert response.status_code == 400
    assert "Invalid encryption key format" in response.json()["detail"]

def test_decrypt_message():
    """Test decrypting a message"""
    # First encrypt a message
    message = "Hello, Decryption!"
    encrypt_response = client.post("/encrypt", json={"message": message})
    encrypt_data = encrypt_response.json()

    # Then decrypt it
    decrypt_response = client.post("/decrypt", json={
        "encrypted_message": encrypt_data["encrypted_message"],
        "key": encrypt_data["key"]
    })

    assert decrypt_response.status_code == 200
    decrypt_data = decrypt_response.json()

    assert "decrypted_message" in decrypt_data
    assert decrypt_data["decrypted_message"] == message

def test_decrypt_message_with_invalid_key():
    """Test decrypting a message with an invalid key"""
    # First encrypt a message
    message = "Hello, World!"
    encrypt_response = client.post("/encrypt", json={"message": message})
    encrypt_data = encrypt_response.json()

    # Try to decrypt with wrong key
    decrypt_response = client.post("/decrypt", json={
        "encrypted_message": encrypt_data["encrypted_message"],
        "key": "invalid-key-format"
    })

    assert decrypt_response.status_code == 400
    assert "Invalid encryption key format" in decrypt_response.json()["detail"]

def test_decrypt_message_with_wrong_key():
    """Test decrypting a message with a valid but wrong key"""
    # First encrypt a message
    message = "Hello, World!"
    encrypt_response = client.post("/encrypt", json={"message": message})
    encrypt_data = encrypt_response.json()

    # Generate a different key
    key_response = client.post("/generate-key")
    wrong_key = key_response.json()["key"]

    # Try to decrypt with wrong key
    decrypt_response = client.post("/decrypt", json={
        "encrypted_message": encrypt_data["encrypted_message"],
        "key": wrong_key
    })

    assert decrypt_response.status_code == 400
    assert "Failed to decrypt message" in decrypt_response.json()["detail"]

def test_decrypt_invalid_encrypted_message():
    """Test decrypting an invalid encrypted message"""
    # Generate a key
    key_response = client.post("/generate-key")
    key = key_response.json()["key"]

    # Try to decrypt invalid message
    decrypt_response = client.post("/decrypt", json={
        "encrypted_message": "invalid-encrypted-message",
        "key": key
    })

    assert decrypt_response.status_code == 400
    assert "Failed to decrypt message" in decrypt_response.json()["detail"]

def test_encrypt_empty_message():
    """Test encrypting an empty message"""
    response = client.post("/encrypt", json={"message": ""})
    assert response.status_code == 200

    data = response.json()
    assert "encrypted_message" in data
    assert "key" in data

    # Verify we can decrypt it back to empty string
    decrypt_response = client.post("/decrypt", json={
        "encrypted_message": data["encrypted_message"],
        "key": data["key"]
    })

    assert decrypt_response.status_code == 200
    assert decrypt_response.json()["decrypted_message"] == ""

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
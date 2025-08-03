from flask import Flask, request, jsonify
from flask_cors import CORS
from cryptography.fernet import Fernet
import json

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

@app.route('/')
def root():
    return jsonify({"message": "Fernet Encryptor API is running"})

@app.route('/generate-key', methods=['POST'])
def generate_key():
    try:
        key = Fernet.generate_key()
        return jsonify({"key": key.decode()})
    except Exception as e:
        return jsonify({"detail": f"Error generating key: {str(e)}"}), 500

@app.route('/encrypt', methods=['POST'])
def encrypt_message():
    try:
        data = request.get_json()
        message = data.get('message')
        key_input = data.get('key')

        if not message:
            return jsonify({"detail": "Message is required"}), 400

        # Use provided key or generate a new one
        if key_input:
            try:
                key = key_input.encode()
                fernet = Fernet(key)
            except Exception:
                return jsonify({"detail": "Invalid encryption key format"}), 400
        else:
            key = Fernet.generate_key()
            fernet = Fernet(key)

        # Encrypt the message
        encrypted_message = fernet.encrypt(message.encode())

        return jsonify({
            "encrypted_message": encrypted_message.decode(),
            "key": key.decode()
        })
    except Exception as e:
        return jsonify({"detail": f"Error encrypting message: {str(e)}"}), 500

@app.route('/decrypt', methods=['POST'])
def decrypt_message():
    try:
        data = request.get_json()
        encrypted_message = data.get('encrypted_message')
        key_input = data.get('key')

        if not encrypted_message or not key_input:
            return jsonify({"detail": "Both encrypted_message and key are required"}), 400

        # Validate and create Fernet instance
        try:
            key = key_input.encode()
            fernet = Fernet(key)
        except Exception:
            return jsonify({"detail": "Invalid encryption key format"}), 400

        # Decrypt the message
        try:
            encrypted_bytes = encrypted_message.encode()
            decrypted_message = fernet.decrypt(encrypted_bytes)
            return jsonify({"decrypted_message": decrypted_message.decode()})
        except Exception:
            return jsonify({"detail": "Failed to decrypt message. Check your key and encrypted message."}), 400

    except Exception as e:
        return jsonify({"detail": f"Error decrypting message: {str(e)}"}), 500

# For local development
if __name__ == '__main__':
    app.run(debug=True)
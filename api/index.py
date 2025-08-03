from flask import Flask, request, jsonify
from flask_cors import CORS
from cryptography.fernet import Fernet
from functools import wraps
import json
import time
from collections import defaultdict

app = Flask(__name__)

# Secure CORS - only allow requests from your GitHub Pages domain
CORS(app, origins=[
    "https://yakksh.github.io",
    "http://localhost:3000",  # For local development
    "http://127.0.0.1:3000"   # Alternative local development
])

# Simple in-memory rate limiting (works better with serverless)
request_counts = defaultdict(list)

# Allowed origins for additional security checks
ALLOWED_ORIGINS = [
    "https://yakksh.github.io",
    "http://localhost:3000",
    "http://127.0.0.1:3000"
]

def simple_rate_limit(max_requests=20):
    """Simple rate limiting decorator"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            client_ip = request.environ.get('HTTP_X_FORWARDED_FOR', request.environ.get('REMOTE_ADDR', 'unknown'))
            current_time = time.time()

            # Clean old requests (older than 60 seconds)
            request_counts[client_ip] = [
                req_time for req_time in request_counts[client_ip]
                if current_time - req_time < 60
            ]

            # Check rate limit
            if len(request_counts[client_ip]) >= max_requests:
                return jsonify({"detail": "Rate limit exceeded. Please try again later."}), 429

            # Add current request
            request_counts[client_ip].append(current_time)

            return f(*args, **kwargs)
        return decorated_function
    return decorator

def verify_origin(f):
    """Decorator to verify request origin"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        origin = request.headers.get('Origin')
        referer = request.headers.get('Referer')

        # Check if request is from allowed origin
        if origin:
            if not any(origin.startswith(allowed) for allowed in ALLOWED_ORIGINS):
                return jsonify({"detail": "Unauthorized origin"}), 403

        # Additional check using referer for extra security
        if referer:
            if not any(referer.startswith(allowed) for allowed in ALLOWED_ORIGINS):
                return jsonify({"detail": "Unauthorized referer"}), 403

        return f(*args, **kwargs)
    return decorated_function

@app.route('/')
def root():
    return jsonify({"message": "Fernet Encryptor API is running"})

@app.route('/generate-key', methods=['POST'])
@simple_rate_limit(10)
@verify_origin
def generate_key():
    try:
        key = Fernet.generate_key()
        return jsonify({"key": key.decode()})
    except Exception as e:
        return jsonify({"detail": f"Error generating key: {str(e)}"}), 500

@app.route('/encrypt', methods=['POST'])
@simple_rate_limit(20)
@verify_origin
def encrypt_message():
    try:
        data = request.get_json()
        if not data:
            return jsonify({"detail": "No JSON data provided"}), 400

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
@simple_rate_limit(20)
@verify_origin
def decrypt_message():
    try:
        data = request.get_json()
        if not data:
            return jsonify({"detail": "No JSON data provided"}), 400

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
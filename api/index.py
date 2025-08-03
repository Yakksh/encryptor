from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from cryptography.fernet import Fernet
import base64
import os
from typing import Optional

app = FastAPI(title="Fernet Encryptor API", version="1.0.0")

# Configure CORS to allow requests from GitHub Pages
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your GitHub Pages domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class EncryptRequest(BaseModel):
    message: str
    key: Optional[str] = None

class DecryptRequest(BaseModel):
    encrypted_message: str
    key: str

class KeyResponse(BaseModel):
    key: str

class EncryptResponse(BaseModel):
    encrypted_message: str
    key: str

class DecryptResponse(BaseModel):
    decrypted_message: str

@app.get("/")
async def root():
    return {"message": "Fernet Encryptor API is running"}

@app.post("/generate-key", response_model=KeyResponse)
async def generate_key():
    """Generate a new Fernet encryption key"""
    try:
        key = Fernet.generate_key()
        return KeyResponse(key=key.decode())
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating key: {str(e)}")

@app.post("/encrypt", response_model=EncryptResponse)
async def encrypt_message(request: EncryptRequest):
    """Encrypt a message using Fernet encryption"""
    try:
        # Use provided key or generate a new one
        if request.key:
            try:
                key = request.key.encode()
                # Validate the key by trying to create a Fernet instance
                fernet = Fernet(key)
            except Exception:
                raise HTTPException(status_code=400, detail="Invalid encryption key format")
        else:
            key = Fernet.generate_key()
            fernet = Fernet(key)
        
        # Encrypt the message
        encrypted_message = fernet.encrypt(request.message.encode())
        
        return EncryptResponse(
            encrypted_message=encrypted_message.decode(),
            key=key.decode()
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error encrypting message: {str(e)}")

@app.post("/decrypt", response_model=DecryptResponse)
async def decrypt_message(request: DecryptRequest):
    """Decrypt a message using Fernet decryption"""
    try:
        # Validate and create Fernet instance with provided key
        try:
            key = request.key.encode()
            fernet = Fernet(key)
        except Exception:
            raise HTTPException(status_code=400, detail="Invalid encryption key format")
        
        # Decrypt the message
        try:
            encrypted_bytes = request.encrypted_message.encode()
            decrypted_message = fernet.decrypt(encrypted_bytes)
            return DecryptResponse(decrypted_message=decrypted_message.decode())
        except Exception:
            raise HTTPException(status_code=400, detail="Failed to decrypt message. Check your key and encrypted message.")
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error decrypting message: {str(e)}")

# Export app for Vercel
handler = app
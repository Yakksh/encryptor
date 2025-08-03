# Fernet Encryptor

A secure message encryption and decryption application using Python's `cryptography` library with Fernet encryption. The project consists of a Python FastAPI backend and a static HTML/CSS/JavaScript frontend that can be deployed on GitHub Pages.

## Features

- **Secure Encryption**: Uses Fernet symmetric encryption from Python's `cryptography` library
- **Key Generation**: Generate new encryption keys on demand
- **Message Encryption**: Encrypt messages with existing or new keys
- **Message Decryption**: Decrypt messages using the appropriate key
- **Web Interface**: Clean, responsive web interface
- **GitHub Pages Compatible**: Frontend can be deployed on GitHub Pages
- **API Backend**: Separate backend API that can be deployed on services like Vercel

## Project Structure

```
fernet-encryptor/
├── backend/
│   └── main.py                 # FastAPI backend application
├── frontend/
│   ├── index.html             # Main web interface
│   ├── styles.css             # Styling
│   └── script.js              # Frontend JavaScript
├── requirements.txt           # Python dependencies
├── vercel.json               # Vercel deployment configuration
├── .gitignore                # Git ignore file
└── README.md                 # This file
```

## Local Development

### Backend Setup

1. **Install Python dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Run the FastAPI server:**
   ```bash
   cd backend
   python main.py
   ```

   Or using uvicorn directly:
   ```bash
   uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
   ```

   The API will be available at `http://localhost:8000`

3. **API Documentation:**
   Visit `http://localhost:8000/docs` for interactive API documentation

### Frontend Setup

1. **Update API URL:**
   Edit `frontend/script.js` and update the `API_BASE_URL` variable to point to your backend:
   ```javascript
   const API_BASE_URL = 'http://localhost:8000'; // For local development
   ```

2. **Serve the frontend:**
   You can use any static file server. For example:
   ```bash
   cd frontend
   python -m http.server 3000
   ```

   Or use a simple Node.js server:
   ```bash
   npx serve frontend
   ```

## Deployment

### Backend Deployment (Vercel)

1. **Install Vercel CLI:**
   ```bash
   npm install -g vercel
   ```

2. **Deploy to Vercel:**
   ```bash
   vercel
   ```

3. **Configure Environment:**
   The `vercel.json` file is already configured to route all requests to the Python backend.

4. **Note your API URL:**
   After deployment, Vercel will provide you with a URL like `https://your-project.vercel.app`

### Frontend Deployment (GitHub Pages)

1. **Update API URL:**
   In `frontend/script.js`, update the `API_BASE_URL` to your deployed backend URL:
   ```javascript
   const API_BASE_URL = 'https://your-project.vercel.app';
   ```

2. **Create a new repository:**
   - Create a new GitHub repository
   - Push your code to the repository

3. **Enable GitHub Pages:**
   - Go to your repository settings
   - Navigate to "Pages" section
   - Set source to "Deploy from a branch"
   - Select the branch containing your code
   - Set folder to `/frontend`
   - Save the settings

4. **Access your application:**
   Your frontend will be available at `https://yourusername.github.io/repository-name`

### Alternative Deployment Options

#### Backend Alternatives:
- **Heroku**: Create a `Procfile` with `web: uvicorn backend.main:app --host 0.0.0.0 --port $PORT`
- **Railway**: Direct deployment with Python support
- **DigitalOcean App Platform**: Python app deployment
- **AWS Lambda**: Using frameworks like Mangum for serverless deployment

#### Frontend Alternatives:
- **Netlify**: Drag and drop the `frontend` folder
- **Vercel**: Deploy frontend separately from backend
- **Firebase Hosting**: Host static files

## API Endpoints

### `GET /`
Health check endpoint

### `POST /generate-key`
Generate a new Fernet encryption key

**Response:**
```json
{
  "key": "base64-encoded-key"
}
```

### `POST /encrypt`
Encrypt a message

**Request:**
```json
{
  "message": "Your message to encrypt",
  "key": "optional-existing-key"
}
```

**Response:**
```json
{
  "encrypted_message": "encrypted-message",
  "key": "encryption-key-used"
}
```

### `POST /decrypt`
Decrypt a message

**Request:**
```json
{
  "encrypted_message": "encrypted-message",
  "key": "decryption-key"
}
```

**Response:**
```json
{
  "decrypted_message": "Your original message"
}
```

## Security Notes

- **Key Management**: Fernet keys are 256-bit and base64-encoded. Store them securely.
- **HTTPS**: Always use HTTPS in production to protect data in transit.
- **Key Storage**: Never store encryption keys in client-side code or version control.
- **CORS**: The backend is configured with permissive CORS for development. Restrict this in production.

## Technologies Used

- **Backend**: Python, FastAPI, cryptography library
- **Frontend**: HTML5, CSS3, JavaScript (Vanilla)
- **Deployment**: Vercel (backend), GitHub Pages (frontend)
- **Encryption**: Fernet symmetric encryption

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This project is open source and available under the [MIT License](LICENSE).
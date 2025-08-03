// Configuration
const API_BASE_URL = 'https://encryptor-iota.vercel.app';

// DOM Elements
const apiStatusIndicator = document.getElementById('api-status-indicator');
const apiStatusText = document.getElementById('api-status-text');
const loadingElement = document.getElementById('loading');
const errorMessageElement = document.getElementById('error-message');

// Initialize the application
document.addEventListener('DOMContentLoaded', function() {
    checkApiStatus();
    showTab('encrypt'); // Show encrypt tab by default
});

// API Status Check
async function checkApiStatus() {
    try {
        const response = await fetch(`${API_BASE_URL}/`);
        if (response.ok) {
            apiStatusIndicator.className = 'status-indicator online';
            apiStatusText.textContent = 'API Online';
        } else {
            throw new Error('API not responding');
        }
    } catch (error) {
        apiStatusIndicator.className = 'status-indicator offline';
        apiStatusText.textContent = 'API Offline - Check backend configuration';
    }
}

// Tab Management
function showTab(tabName) {
    // Hide all tab contents
    const tabContents = document.querySelectorAll('.tab-content');
    tabContents.forEach(tab => tab.classList.remove('active'));

    // Remove active class from all tab buttons
    const tabButtons = document.querySelectorAll('.tab-button');
    tabButtons.forEach(button => button.classList.remove('active'));

    // Show selected tab content
    document.getElementById(tabName).classList.add('active');

    // Add active class to clicked button
    event.target.classList.add('active');

    // Hide any previous results
    hideResults();
}

// Utility Functions
function showLoading() {
    loadingElement.style.display = 'block';
    hideError();
}

function hideLoading() {
    loadingElement.style.display = 'none';
}

function showError(message) {
    errorMessageElement.textContent = message;
    errorMessageElement.style.display = 'block';
    hideLoading();
}

function hideError() {
    errorMessageElement.style.display = 'none';
}

function hideResults() {
    document.getElementById('encrypt-result').style.display = 'none';
    document.getElementById('decrypt-result').style.display = 'none';
    document.getElementById('generated-key-result').style.display = 'none';
    hideError();
}

function copyToClipboard(elementId) {
    const element = document.getElementById(elementId);
    const text = element.textContent;

    navigator.clipboard.writeText(text).then(function() {
        // Visual feedback
        const originalText = element.nextElementSibling.textContent;
        element.nextElementSibling.textContent = 'Copied!';
        setTimeout(() => {
            element.nextElementSibling.textContent = originalText;
        }, 2000);
    }).catch(function(err) {
        console.error('Could not copy text: ', err);
        // Fallback for older browsers
        const textArea = document.createElement('textarea');
        textArea.value = text;
        document.body.appendChild(textArea);
        textArea.select();
        document.execCommand('copy');
        document.body.removeChild(textArea);
    });
}

// API Functions
async function generateKey() {
    showLoading();
    hideResults();

    try {
        const response = await fetch(`${API_BASE_URL}/generate-key`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const data = await response.json();

        document.getElementById('generated-key-value').textContent = data.key;
        document.getElementById('generated-key-result').style.display = 'block';

    } catch (error) {
        showError(`Error generating key: ${error.message}`);
    } finally {
        hideLoading();
    }
}

async function encryptMessage() {
    const message = document.getElementById('encrypt-message').value.trim();
    const key = document.getElementById('encrypt-key').value.trim();

    if (!message) {
        showError('Please enter a message to encrypt');
        return;
    }

    showLoading();
    hideResults();

    try {
        const requestBody = {
            message: message
        };

        if (key) {
            requestBody.key = key;
        }

        const response = await fetch(`${API_BASE_URL}/encrypt`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(requestBody)
        });

        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.detail || `HTTP error! status: ${response.status}`);
        }

        const data = await response.json();

        document.getElementById('encrypted-message-value').textContent = data.encrypted_message;
        document.getElementById('encryption-key-value').textContent = data.key;
        document.getElementById('encrypt-result').style.display = 'block';

    } catch (error) {
        showError(`Error encrypting message: ${error.message}`);
    } finally {
        hideLoading();
    }
}

async function decryptMessage() {
    const encryptedMessage = document.getElementById('decrypt-message').value.trim();
    const key = document.getElementById('decrypt-key').value.trim();

    if (!encryptedMessage) {
        showError('Please enter an encrypted message');
        return;
    }

    if (!key) {
        showError('Please enter the decryption key');
        return;
    }

    showLoading();
    hideResults();

    try {
        const response = await fetch(`${API_BASE_URL}/decrypt`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                encrypted_message: encryptedMessage,
                key: key
            })
        });

        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.detail || `HTTP error! status: ${response.status}`);
        }

        const data = await response.json();

        document.getElementById('decrypted-message-value').textContent = data.decrypted_message;
        document.getElementById('decrypt-result').style.display = 'block';

    } catch (error) {
        showError(`Error decrypting message: ${error.message}`);
    } finally {
        hideLoading();
    }
}

// Enhanced error handling for network issues
window.addEventListener('online', checkApiStatus);
window.addEventListener('offline', function() {
    apiStatusIndicator.className = 'status-indicator offline';
    apiStatusText.textContent = 'No Internet Connection';
});
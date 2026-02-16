// API Service for File Integrity & Authenticity Verification Platform

const API_BASE_URL = 'http://localhost:8000/api/v1';
const TOKEN_KEY = 'auth_token';

class APIService {
    // Get stored token
    getToken() {
        return localStorage.getItem(TOKEN_KEY);
    }

    // Save token
    saveToken(token) {
        localStorage.setItem(TOKEN_KEY, token);
    }

    // Remove token
    removeToken() {
        localStorage.removeItem(TOKEN_KEY);
    }

    // Get headers with auth
    getHeaders(includeAuth = true) {
        const headers = {
            'Content-Type': 'application/json',
        };
        
        if (includeAuth) {
            const token = this.getToken();
            if (token) {
                headers['Authorization'] = `Bearer ${token}`;
            }
        }
        
        return headers;
    }

    // Register user
    async register(username, email, password) {
        try {
            const response = await fetch(`${API_BASE_URL}/auth/register`, {
                method: 'POST',
                headers: this.getHeaders(false),
                body: JSON.stringify({ username, email, password })
            });
            
            if (!response.ok) {
                const error = await response.json();
                const errorMessage = error.detail || error.message || 'Registration failed';
                throw new Error(typeof errorMessage === 'string' ? errorMessage : JSON.stringify(errorMessage));
            }
            
            return await response.json();
        } catch (err) {
            if (err instanceof Error) {
                throw err;
            }
            throw new Error(String(err));
        }
    }

    // Login user
    async login(username, password) {
        try {
            const response = await fetch(`${API_BASE_URL}/auth/login`, {
                method: 'POST',
                headers: this.getHeaders(false),
                body: JSON.stringify({ username, password })
            });
            
            if (!response.ok) {
                const error = await response.json();
                const errorMessage = error.detail || error.message || 'Login failed';
                throw new Error(typeof errorMessage === 'string' ? errorMessage : JSON.stringify(errorMessage));
            }
            
            const data = await response.json();
            this.saveToken(data.access_token);
            return data;
        } catch (err) {
            if (err instanceof Error) {
                throw err;
            }
            throw new Error(String(err));
        }
    }

    // Logout
    logout() {
        this.removeToken();
    }

    // Upload file
    async uploadFile(file, password, description = null) {
        try {
            const formData = new FormData();
            formData.append('file', file);
            formData.append('password', password);
            if (description) {
                formData.append('description', description);
            }

            const response = await fetch(`${API_BASE_URL}/files/upload`, {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${this.getToken()}`
                },
                body: formData
            });

            if (!response.ok) {
                const error = await response.json();
                const errorMessage = error.detail || error.message || 'Upload failed';
                throw new Error(typeof errorMessage === 'string' ? errorMessage : JSON.stringify(errorMessage));
            }

            return await response.json();
        } catch (err) {
            if (err instanceof Error) {
                throw err;
            }
            throw new Error(String(err));
        }
    }

    // List files
    async listFiles() {
        const response = await fetch(`${API_BASE_URL}/files`, {
            headers: this.getHeaders()
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Failed to fetch files');
        }

        return await response.json();
    }

    // Get file metadata
    async getFileMetadata(fileId) {
        const response = await fetch(`${API_BASE_URL}/files/${fileId}`, {
            headers: this.getHeaders()
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Failed to fetch file metadata');
        }

        return await response.json();
    }

    // Verify file
    async verifyFile(fileId) {
        const response = await fetch(`${API_BASE_URL}/verify/${fileId}`, {
            method: 'POST',
            headers: this.getHeaders()
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Verification failed');
        }

        return await response.json();
    }

    // Download file
    async downloadFile(fileId, filename) {
        const response = await fetch(`${API_BASE_URL}/files/${fileId}/download`, {
            headers: this.getHeaders()
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Download failed');
        }

        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = filename;
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        document.body.removeChild(a);
    }

    // Delete file
    async deleteFile(fileId) {
        const response = await fetch(`${API_BASE_URL}/files/${fileId}`, {
            method: 'DELETE',
            headers: this.getHeaders()
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Delete failed');
        }

        return await response.json();
    }

    // Health check
    async healthCheck() {
        const response = await fetch('http://localhost:8000/health');
        return await response.json();
    }
}

// Export API service
const api = new APIService();

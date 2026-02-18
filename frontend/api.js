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
        console.log('[API] Attempting login...');
        console.log('[API] Username:', username);
        console.log('[API] API URL:', `${API_BASE_URL}/auth/login`);
        
        try {
            const response = await fetch(`${API_BASE_URL}/auth/login`, {
                method: 'POST',
                headers: this.getHeaders(false),
                body: JSON.stringify({ username, password })
            });
            
            console.log('[API] Response status:', response.status, response.statusText);
            
            if (!response.ok) {
                const error = await response.json();
                console.error('[API] Login failed:', error);
                const errorMessage = error.detail || error.message || 'Login failed';
                throw new Error(typeof errorMessage === 'string' ? errorMessage : JSON.stringify(errorMessage));
            }
            
            const data = await response.json();
            console.log('[API] Login successful!');
            console.log('[API] User:', data.username, '- Admin:', data.is_admin);
            this.saveToken(data.access_token);
            return data;
        } catch (err) {
            console.error('[API] Login error:', err);
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
        console.log('[API] Fetching files list...');
        const response = await fetch(`${API_BASE_URL}/files`, {
            headers: this.getHeaders()
        });

        if (!response.ok) {
            const error = await response.json();
            console.error('[API] Failed to fetch files:', error);
            throw new Error(error.detail || 'Failed to fetch files');
        }

        const data = await response.json();
        console.log('[API] Files received:', data);
        console.log('[API] Number of files:', data.files?.length || 0);
        return data;
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

    // Get file details (alias for getFileMetadata)
    async getFileDetails(fileId) {
        return await this.getFileMetadata(fileId);
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

    // Update file status (admin only)
    async updateFileStatus(fileId, status) {
        const response = await fetch(`${API_BASE_URL}/admin/files/${fileId}/status`, {
            method: 'PATCH',
            headers: {
                'Authorization': `Bearer ${this.getToken()}`,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ verification_status: status })
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Failed to update file status');
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

// Log API methods for debugging
console.log('[API] APIService loaded. Methods:', Object.getOwnPropertyNames(Object.getPrototypeOf(api)));
console.log('[API] updateFileStatus exists:', typeof api.updateFileStatus === 'function');

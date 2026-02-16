# File Integrity & Authenticity Verification Platform - Frontend

A modern, secure web interface for the File Integrity & Authenticity Verification Platform.

## Features

- 🔐 **Secure Authentication** - JWT-based login and registration
- 📁 **File Upload** - Drag & drop file uploads with encryption
- 🔍 **File Verification** - Real-time integrity checking
- 📊 **Dashboard** - Visual statistics and file management
- 🎨 **Modern UI** - Security-themed color palette with deep blues and cyans
- 📱 **Responsive** - Works on desktop and mobile devices

## Color Palette

The frontend uses a professional security-themed color scheme:

- **Primary (Security Blue)**: `#1e3a8a`, `#2563eb`, `#3b82f6`
- **Success (Verified Green)**: `#059669`, `#10b981`, `#34d399`
- **Error (Tampered Red)**: `#dc2626`, `#ef4444`, `#f87171`
- **Accent (Technology Cyan)**: `#0891b2`, `#06b6d4`, `#22d3ee`
- **Background (Dark Slate)**: `#0f172a`, `#1e293b`, `#334155`

## Quick Start

1. **Start the Backend Server**:
   ```bash
   cd "/Users/Dipesh/Desktop/five/File Integrity & Authenticity Verification System"
   python3 -m uvicorn gateway.main:app --host 0.0.0.0 --port 8000
   ```

2. **Open the Frontend**:
   - Simply open `frontend/index.html` in your web browser
   - Or use a local server:
     ```bash
     cd frontend
     python3 -m http.server 3000
     ```
   - Then visit: http://localhost:3000

## Usage

### 1. Create an Account
- Click "Sign Up" on the login page
- Enter username, email, and password
- Click "Create Account"

### 2. Login
- Enter your username and password
- Click "Sign In"

### 3. Upload Files
- Drag and drop a file or click "Choose File"
- Enter an encryption password
- Optionally add a description
- Click "Upload & Secure File"

### 4. Verify Files
- Click the "Verify" button on any file
- View the verification status (Verified, Tampered, or Pending)

### 5. Download Files
- Click the "Download" button to retrieve your encrypted file

### 6. Delete Files
- Click the "Delete" button to remove a file permanently

## File Structure

```
frontend/
├── index.html      # Main HTML page
├── styles.css      # Complete styling with security theme
├── api.js          # API service for backend communication
├── app.jsx         # React components and application logic
└── README.md       # This file
```

## Components

### Authentication
- **Login** - User authentication with JWT
- **Register** - New user registration with RSA key generation

### Dashboard
- **Stats Cards** - Total files, verified files, pending verifications
- **File Upload** - Drag & drop interface with encryption
- **File List** - Manage all uploaded files

### File Management
- **FileItem** - Individual file card with actions
- **Verification Badge** - Visual status indicator
- **File Actions** - Verify, download, delete operations

## API Integration

The frontend communicates with the backend API at `http://localhost:8000/api/v1`:

- `POST /auth/register` - User registration
- `POST /auth/login` - User authentication
- `POST /files/upload` - File upload with encryption
- `GET /files` - List all user files
- `GET /files/{file_id}/download` - Download file
- `POST /verify/{file_id}` - Verify file integrity
- `DELETE /files/{file_id}` - Delete file

## Browser Compatibility

- Chrome/Edge (latest)
- Firefox (latest)
- Safari (latest)

## Security Features

- JWT token-based authentication
- Encrypted file storage (AES-256-GCM)
- Digital signatures (RSA-2048)
- SHA-256 file hashing
- Secure password handling

## Troubleshooting

### Cannot connect to backend
- Ensure the backend server is running on port 8000
- Check that MongoDB is running
- Verify CORS settings in the backend

### Files not uploading
- Check file size (max 100MB)
- Ensure you've entered an encryption password
- Verify you're logged in (token is valid)

### Verification failing
- Ensure the file hasn't been modified
- Check that the backend can access the encrypted file
- Verify the RSA keys are stored correctly

## Development

To modify the frontend:

1. Edit the relevant files (index.html, styles.css, api.js, app.jsx)
2. Refresh your browser to see changes
3. For production, consider building with a bundler like Webpack or Vite

## License

Part of the File Integrity & Authenticity Verification Platform.

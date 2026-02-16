// File Integrity & Authenticity Verification Platform - React App

const { useState, useEffect, useCallback } = React;

// Alert Component
function Alert({ type, message, onClose }) {
    // Ensure message is always a string
    const displayMessage = typeof message === 'string' ? message : JSON.stringify(message);
    
    return (
        <div className={`alert alert-${type}`}>
            <span>
                {type === 'success' && '✓'}
                {type === 'error' && '✕'}
                {type === 'info' && 'ℹ'}
            </span>
            <span>{displayMessage}</span>
            {onClose && (
                <button onClick={onClose} style={{ marginLeft: 'auto', background: 'none', border: 'none', color: 'inherit', cursor: 'pointer', fontSize: '1.2rem' }}>×</button>
            )}
        </div>
    );
}

// Loading Overlay
function LoadingOverlay({ message = 'Processing...' }) {
    return (
        <div className="loading-overlay">
            <div style={{ textAlign: 'center' }}>
                <div className="loading-spinner"></div>
                <p style={{ marginTop: '1rem', color: 'var(--text-secondary)' }}>{message}</p>
            </div>
        </div>
    );
}

// Login Component
function Login({ onLogin, onSwitchToRegister }) {
    const [username, setUsername] = useState('');
    const [password, setPassword] = useState('');
    const [error, setError] = useState('');
    const [loading, setLoading] = useState(false);

    const handleSubmit = async (e) => {
        e.preventDefault();
        setError('');
        setLoading(true);

        try {
            await api.login(username, password);
            onLogin();
        } catch (err) {
            console.error('Login error:', err);
            const errorMessage = err.message || err.toString() || 'Login failed. Please try again.';
            setError(errorMessage);
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="auth-container">
            <div className="auth-box">
                <div className="auth-header">
                    <div className="logo-icon" style={{ margin: '0 auto 1rem' }}>🔒</div>
                    <h2>Welcome Back</h2>
                    <p>Sign in to verify your files</p>
                </div>

                {error && <Alert type="error" message={error} onClose={() => setError('')} />}

                <form onSubmit={handleSubmit}>
                    <div className="form-group">
                        <label>Username</label>
                        <input
                            type="text"
                            value={username}
                            onChange={(e) => setUsername(e.target.value)}
                            placeholder="Enter your username"
                            required
                        />
                    </div>

                    <div className="form-group">
                        <label>Password</label>
                        <input
                            type="password"
                            value={password}
                            onChange={(e) => setPassword(e.target.value)}
                            placeholder="Enter your password"
                            required
                        />
                    </div>

                    <button type="submit" className="btn btn-primary" disabled={loading}>
                        {loading ? <><span className="spinner"></span> Signing In...</> : 'Sign In'}
                    </button>
                </form>

                <p className="text-center mt-2" style={{ color: 'var(--text-muted)', fontSize: '0.875rem' }}>
                    Don't have an account?{' '}
                    <a href="#" onClick={(e) => { e.preventDefault(); onSwitchToRegister(); }} style={{ color: 'var(--primary-500)', textDecoration: 'none', fontWeight: 600 }}>
                        Sign Up
                    </a>
                </p>
            </div>
        </div>
    );
}

// Register Component
function Register({ onRegister, onSwitchToLogin }) {
    const [username, setUsername] = useState('');
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [error, setError] = useState('');
    const [success, setSuccess] = useState('');
    const [loading, setLoading] = useState(false);

    const handleSubmit = async (e) => {
        e.preventDefault();
        setError('');
        setSuccess('');
        setLoading(true);

        try {
            await api.register(username, email, password);
            setSuccess('Registration successful! Please sign in.');
            setTimeout(() => onSwitchToLogin(), 2000);
        } catch (err) {
            console.error('Registration error:', err);
            const errorMessage = err.message || err.toString() || 'Registration failed. Please try again.';
            setError(errorMessage);
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="auth-container">
            <div className="auth-box">
                <div className="auth-header">
                    <div className="logo-icon" style={{ margin: '0 auto 1rem' }}>🔐</div>
                    <h2>Create Account</h2>
                    <p>Join the secure file verification platform</p>
                </div>

                {error && <Alert type="error" message={error} onClose={() => setError('')} />}
                {success && <Alert type="success" message={success} />}

                <form onSubmit={handleSubmit}>
                    <div className="form-group">
                        <label>Username</label>
                        <input
                            type="text"
                            value={username}
                            onChange={(e) => setUsername(e.target.value)}
                            placeholder="Choose a username"
                            required
                        />
                    </div>

                    <div className="form-group">
                        <label>Email</label>
                        <input
                            type="email"
                            value={email}
                            onChange={(e) => setEmail(e.target.value)}
                            placeholder="Enter your email"
                            required
                        />
                    </div>

                    <div className="form-group">
                        <label>Password</label>
                        <input
                            type="password"
                            value={password}
                            onChange={(e) => setPassword(e.target.value)}
                            placeholder="Create a strong password"
                            required
                        />
                    </div>

                    <button type="submit" className="btn btn-primary" disabled={loading}>
                        {loading ? <><span className="spinner"></span> Creating Account...</> : 'Create Account'}
                    </button>
                </form>

                <p className="text-center mt-2" style={{ color: 'var(--text-muted)', fontSize: '0.875rem' }}>
                    Already have an account?{' '}
                    <a href="#" onClick={(e) => { e.preventDefault(); onSwitchToLogin(); }} style={{ color: 'var(--primary-500)', textDecoration: 'none', fontWeight: 600 }}>
                        Sign In
                    </a>
                </p>
            </div>
        </div>
    );
}

// File Upload Component
function FileUpload({ onUploadSuccess }) {
    const [selectedFile, setSelectedFile] = useState(null);
    const [password, setPassword] = useState('');
    const [description, setDescription] = useState('');
    const [dragOver, setDragOver] = useState(false);
    const [uploading, setUploading] = useState(false);
    const [error, setError] = useState('');

    const handleFileSelect = (e) => {
        const file = e.target.files[0];
        if (file) {
            setSelectedFile(file);
            setError('');
        }
    };

    const handleDrop = (e) => {
        e.preventDefault();
        setDragOver(false);
        const file = e.dataTransfer.files[0];
        if (file) {
            setSelectedFile(file);
            setError('');
        }
    };

    const handleUpload = async (e) => {
        e.preventDefault();
        if (!selectedFile || !password) {
            setError('Please select a file and enter a password');
            return;
        }

        setUploading(true);
        setError('');

        try {
            await api.uploadFile(selectedFile, password, description || null);
            setSelectedFile(null);
            setPassword('');
            setDescription('');
            if (onUploadSuccess) {
                onUploadSuccess();
            }
        } catch (err) {
            console.error('Upload error:', err);
            const errorMsg = err.message || err.toString() || 'Upload failed';
            setError(errorMsg);
        } finally {
            setUploading(false);
        }
    };

    return (
        <div
            className={`upload-section ${dragOver ? 'drag-over' : ''}`}
            onDragOver={(e) => { e.preventDefault(); setDragOver(true); }}
            onDragLeave={() => setDragOver(false)}
            onDrop={handleDrop}>
            
            <div className="upload-icon">📁</div>
            <h3 style={{ marginBottom: '0.5rem' }}>Upload File for Verification</h3>
            <p style={{ color: 'var(--text-muted)', marginBottom: '1.5rem' }}>
                Drag and drop or click to select a file
            </p>

            <div style={{ marginBottom: '1rem', padding: '0.75rem', background: 'rgba(6, 182, 212, 0.1)', border: '1px solid var(--accent-700)', borderRadius: '8px', fontSize: '0.875rem' }}>
                ℹ️ <strong>Important:</strong> Use your account password for file signing
            </div>

            {error && <Alert type="error" message={error} onClose={() => setError('')} />}

            <form onSubmit={handleUpload}>
                <input
                    type="file"
                    id="fileInput"
                    className="file-input"
                    onChange={handleFileSelect}
                />
                
                <label htmlFor="fileInput" className="btn btn-secondary" style={{ marginBottom: '1rem' }}>
                    📎 Choose File
                </label>

                {selectedFile && (
                    <div style={{ marginBottom: '1rem', color: 'var(--accent-500)' }}>
                        Selected: {selectedFile.name} ({(selectedFile.size / 1024).toFixed(2)} KB)
                    </div>
                )}

                <div className="form-group" style={{ maxWidth: '400px', margin: '0 auto 1rem' }}>
                    <label>Your Account Password (for signing)</label>
                    <input
                        type="password"
                        value={password}
                        onChange={(e) => setPassword(e.target.value)}
                        placeholder="Enter your account password"
                        required
                    />
                    <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginTop: '0.25rem' }}>
                        This must be the password you used during registration
                    </div>
                </div>

                <div className="form-group" style={{ maxWidth: '400px', margin: '0 auto 1rem' }}>
                    <label>Description (Optional)</label>
                    <input
                        type="text"
                        value={description}
                        onChange={(e) => setDescription(e.target.value)}
                        placeholder="Add a description"
                    />
                </div>

                {selectedFile && (
                    <button type="submit" className="btn btn-primary" disabled={uploading}>
                        {uploading ? <><span className="spinner"></span> Uploading...</> : '🚀 Upload & Secure File'}
                    </button>
                )}
            </form>
        </div>
    );
}

// File Item Component
function FileItem({ file, onVerify, onDownload, onDelete }) {
    const [verifying, setVerifying] = useState(false);

    const handleVerify = async () => {
        setVerifying(true);
        await onVerify(file.file_id);
        setVerifying(false);
    };

    const formatDate = (dateStr) => {
        return new Date(dateStr).toLocaleString();
    };

    const getStatusBadge = () => {
        const status = file.verification_status || 'pending';
        if (status === 'verified' || status === 'integrity_confirmed') {
            return <span className="badge badge-verified">✓ Verified</span>;
        } else if (status === 'tampered' || status === 'integrity_compromised') {
            return <span className="badge badge-tampered">⚠ Tampered</span>;
        } else {
            return <span className="badge badge-pending">⏳ Pending</span>;
        }
    };

    return (
        <div className="file-item">
            <div className="file-info">
                <div className="file-name">{file.filename}</div>
                <div className="file-meta">
                    Uploaded: {formatDate(file.uploaded_at)} • 
                    Verifications: {file.verification_count || 0} • 
                    Hash: {file.file_hash.substring(0, 16)}...
                </div>
                {file.description && (
                    <div className="file-meta" style={{ marginTop: '0.25rem' }}>
                        {file.description}
                    </div>
                )}
                <div style={{ marginTop: '0.5rem' }}>
                    {getStatusBadge()}
                </div>
            </div>
            <div className="file-actions">
                <button 
                    className="btn btn-secondary btn-small"
                    onClick={handleVerify}
                    disabled={verifying}>
                    {verifying ? <span className="spinner"></span> : '🔍'} Verify
                </button>
                <button 
                    className="btn btn-secondary btn-small"
                    onClick={() => onDownload(file.file_id, file.filename)}>
                    ⬇ Download
                </button>
                <button 
                    className="btn btn-danger btn-small"
                    onClick={() => onDelete(file.file_id)}>
                    🗑 Delete
                </button>
            </div>
        </div>
    );
}

// Dashboard Component
function Dashboard({ onLogout }) {
    const [files, setFiles] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState('');
    const [success, setSuccess] = useState('');
    const [stats, setStats] = useState({ total: 0, verified: 0, pending: 0 });

    const loadFiles = useCallback(async () => {
        try {
            const data = await api.listFiles();
            const filesList = data.files || [];
            setFiles(filesList);
            
            // Calculate stats
            const total = filesList.length;
            const verified = filesList.filter(f => 
                f.verification_status === 'verified' || 
                f.verification_status === 'integrity_confirmed'
            ).length;
            const pending = filesList.filter(f => 
                !f.verification_status || 
                f.verification_status === 'pending'
            ).length;
            
            setStats({ total, verified, pending });
        } catch (err) {
            console.error('Error loading files:', err);
            const errorMsg = err.message || err.toString() || 'Failed to load files';
            setError(errorMsg);
        } finally {
            setLoading(false);
        }
    }, []);

    useEffect(() => {
        loadFiles();
    }, [loadFiles]);

    const handleUploadSuccess = async () => {
        try {
            setSuccess('File uploaded and secured successfully!');
            setError('');
            await loadFiles();
            setTimeout(() => setSuccess(''), 3000);
        } catch (err) {
            console.error('Error refreshing files:', err);
        }
    };

    const handleVerify = async (fileId) => {
        try {
            const result = await api.verifyFile(fileId);
            const status = result.verified ? '✅ Verified - File is authentic and unmodified' : 
                          result.tampered ? '⚠️ Tampered - File has been modified' : 
                          result.verification_status || 'Complete';
            setSuccess(`Verification complete: ${status}`);
            loadFiles();
            setTimeout(() => setSuccess(''), 5000);
        } catch (err) {
            setError(err.message);
            setTimeout(() => setError(''), 3000);
        }
    };

    const handleDownload = async (fileId, filename) => {
        try {
            await api.downloadFile(fileId, filename);
            setSuccess('File downloaded successfully!');
            setTimeout(() => setSuccess(''), 3000);
        } catch (err) {
            setError(err.message);
            setTimeout(() => setError(''), 3000);
        }
    };

    const handleDelete = async (fileId) => {
        if (!confirm('Are you sure you want to delete this file?')) return;
        
        try {
            await api.deleteFile(fileId);
            setSuccess('File deleted successfully!');
            loadFiles();
            setTimeout(() => setSuccess(''), 3000);
        } catch (err) {
            setError(err.message);
            setTimeout(() => setError(''), 3000);
        }
    };

    if (loading) {
        return <LoadingOverlay message="Loading your files..." />;
    }

    return (
        <>
            <header className="header">
                <div className="header-content">
                    <div className="logo">
                        <div className="logo-icon">🔒</div>
                        <div className="logo-text">
                            <h1>File Integrity & Authenticity</h1>
                            <p>Verification Platform</p>
                        </div>
                    </div>
                    <div className="nav-buttons">
                        <div className="user-info">
                            <span>👤</span>
                            <span>Authenticated</span>
                        </div>
                        <button className="btn btn-secondary btn-small" onClick={onLogout}>
                            Logout
                        </button>
                    </div>
                </div>
            </header>

            <div className="container">
                {success && <Alert type="success" message={success} onClose={() => setSuccess('')} />}
                {error && <Alert type="error" message={error} onClose={() => setError('')} />}

                <div className="dashboard-header">
                    <h2>Dashboard</h2>
                    <p style={{ color: 'var(--text-muted)' }}>Manage and verify your files securely</p>
                </div>

                <div className="dashboard-stats">
                    <div className="stat-card">
                        <h3>Total Files</h3>
                        <div className="value">{stats.total}</div>
                    </div>
                    <div className="stat-card">
                        <h3>Verified Files</h3>
                        <div className="value" style={{ color: 'var(--success-500)' }}>{stats.verified}</div>
                    </div>
                    <div className="stat-card">
                        <h3>Pending Verification</h3>
                        <div className="value" style={{ color: 'var(--warning-500)' }}>{stats.pending}</div>
                    </div>
                </div>

                <FileUpload onUploadSuccess={handleUploadSuccess} />

                <div className="file-list">
                    <div className="file-list-header">
                        <h3>Your Files ({files.length})</h3>
                        <button className="btn btn-secondary btn-small" onClick={loadFiles}>
                            🔄 Refresh
                        </button>
                    </div>
                    
                    {!files || files.length === 0 ? (
                        <div style={{ padding: '3rem', textAlign: 'center', color: 'var(--text-muted)' }}>
                            <div style={{ fontSize: '3rem', marginBottom: '1rem' }}>📂</div>
                            <p>No files uploaded yet</p>
                            <p style={{ fontSize: '0.875rem' }}>Upload your first file to get started</p>
                        </div>
                    ) : (
                        Array.isArray(files) && files.map(file => file && file.file_id ? (
                            <FileItem
                                key={file.file_id}
                                file={file}
                                onVerify={handleVerify}
                                onDownload={handleDownload}
                                onDelete={handleDelete}
                            />
                        ) : null)
                    )}
                </div>
            </div>
        </>
    );
}

// Main App Component
function App() {
    const [isAuthenticated, setIsAuthenticated] = useState(false);
    const [isAdmin, setIsAdmin] = useState(false);
    const [currentView, setCurrentView] = useState('login'); // 'login' or 'register'

    useEffect(() => {
        // Check if user has a token
        const token = api.getToken();
        if (token) {
            setIsAuthenticated(true);
            checkAdminStatus();
        }
    }, []);

    const checkAdminStatus = async () => {
        try {
            const token = api.getToken();
            const response = await fetch('http://localhost:8000/api/v1/admin/stats', {
                headers: { 'Authorization': `Bearer ${token}` }
            });
            setIsAdmin(response.ok);
        } catch {
            setIsAdmin(false);
        }
    };

    const handleLogin = async () => {
        setIsAuthenticated(true);
        await checkAdminStatus();
    };

    const handleLogout = () => {
        api.logout();
        setIsAuthenticated(false);
        setIsAdmin(false);
        setCurrentView('login');
    };

    if (isAuthenticated) {
        if (isAdmin) {
            return <AdminDashboard onLogout={handleLogout} />;
        }
        return <Dashboard onLogout={handleLogout} />;
    }

    if (currentView === 'register') {
        return (
            <Register
                onRegister={handleLogin}
                onSwitchToLogin={() => setCurrentView('login')}
            />
        );
    }

    return (
        <Login
            onLogin={handleLogin}
            onSwitchToRegister={() => setCurrentView('register')}
        />
    );
}

// Render App
ReactDOM.render(<App />, document.getElementById('root'));

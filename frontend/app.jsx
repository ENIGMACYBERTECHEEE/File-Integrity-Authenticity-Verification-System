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
    const [username, setUsername] = useState('admin');
    const [password, setPassword] = useState('admin123');
    const [error, setError] = useState('');
    const [loading, setLoading] = useState(false);

    const handleSubmit = async (e) => {
        e.preventDefault();
        setError('');
        setLoading(true);

        try {
            const response = await api.login(username, password);
            onLogin(response);
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
function FileItem({ file, onVerify, onDownload, onDelete, isAdmin }) {
    const [verifying, setVerifying] = useState(false);

    const handleVerify = async () => {
        setVerifying(true);
        await onVerify(file.file_id);
        setVerifying(false);
    };

    const formatDate = (dateStr) => {
        if (!dateStr) return 'N/A';
        try {
            const date = new Date(dateStr);
            if (isNaN(date.getTime())) return 'N/A';
            return date.toLocaleString();
        } catch (e) {
            return 'N/A';
        }
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
                    Uploaded: {formatDate(file.uploaded_at || file.upload_date || file.created_at)} • 
                    Verifications: {file.verification_count || 0} • 
                    Hash: {file.file_hash ? file.file_hash.substring(0, 16) : 'N/A'}...
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
                {isAdmin && (
                    <button 
                        className="btn btn-secondary btn-small"
                        onClick={handleVerify}
                        disabled={verifying}>
                        {verifying ? <span className="spinner"></span> : '🔍'} Verify
                    </button>
                )}
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
function Dashboard({ onLogout, currentUser }) {
    const [files, setFiles] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState('');
    const [success, setSuccess] = useState('');
    const [stats, setStats] = useState({ total: 0, verified: 0, pending: 0 });
    const [adminStats, setAdminStats] = useState(null);
    const [allUsers, setAllUsers] = useState([]);
    const [allFiles, setAllFiles] = useState([]);
    const [verifications, setVerifications] = useState([]);
    const [timeline, setTimeline] = useState([]);
    const [activeTab, setActiveTab] = useState('files'); // 'files', 'users', 'verifications', 'activity'
    
    // Check if user is admin
    const isAdmin = currentUser?.role === 'admin' || currentUser?.is_admin || false;

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

    const loadAdminData = useCallback(async () => {
        if (!isAdmin) return;
        
        try {
            // Load admin stats
            const statsData = await api.get('/api/v1/admin/stats');
            setAdminStats(statsData);

            // Load all users
            const usersData = await api.get('/api/v1/admin/users?limit=100');
            setAllUsers(usersData.users || []);

            // Load all files (admin view)
            const filesData = await api.get('/api/v1/admin/files?limit=100');
            setAllFiles(filesData.files || []);

            // Load verifications
            const verifsData = await api.get('/api/v1/admin/verifications?limit=50');
            setVerifications(verifsData.verifications || []);

            // Load activity timeline
            const timelineData = await api.get('/api/v1/admin/activity-timeline?hours=24');
            setTimeline(timelineData.timeline || []);
        } catch (err) {
            console.error('Error loading admin data:', err);
        }
    }, [isAdmin]);

    useEffect(() => {
        loadFiles();
        if (isAdmin) {
            loadAdminData();
        }
    }, [loadFiles, loadAdminData, isAdmin]);

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

    const toggleUserStatus = async (userId, currentStatus) => {
        try {
            await api.patch(`/api/v1/admin/users/${userId}/status`, {
                is_active: !currentStatus
            });
            setSuccess('User status updated');
            loadAdminData();
            setTimeout(() => setSuccess(''), 3000);
        } catch (err) {
            setError('Failed to update user status');
            setTimeout(() => setError(''), 3000);
        }
    };

    const updateUserRole = async (userId, newRole) => {
        try {
            await api.patch(`/api/v1/admin/users/${userId}/role`, {
                role: newRole
            });
            setSuccess('User role updated');
            loadAdminData();
            setTimeout(() => setSuccess(''), 3000);
        } catch (err) {
            setError('Failed to update user role');
            setTimeout(() => setError(''), 3000);
        }
    };

    const deleteFileAdmin = async (fileId) => {
        if (!confirm('Are you sure you want to permanently delete this file?')) return;
        try {
            await api.delete(`/api/v1/admin/files/${fileId}`);
            setSuccess('File permanently deleted');
            loadAdminData();
            loadFiles();
            setTimeout(() => setSuccess(''), 3000);
        } catch (err) {
            setError('Failed to delete file');
            setTimeout(() => setError(''), 3000);
        }
    };

    const formatDate = (dateStr) => {
        if (!dateStr) return 'N/A';
        return new Date(dateStr).toLocaleString();
    };

    const formatBytes = (bytes) => {
        if (!bytes) return '0 B';
        const k = 1024;
        const sizes = ['B', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i];
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
                            <span>{currentUser?.username || 'User'}</span>
                            {isAdmin && <span className="badge" style={{background: '#667eea', color: 'white', padding: '4px 12px', borderRadius: '12px', fontSize: '12px', marginLeft: '8px'}}>ADMIN</span>}
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
                    <h2>{isAdmin ? 'Admin Dashboard' : 'Dashboard'}</h2>
                    <p style={{ color: 'var(--text-muted)' }}>
                        {isAdmin ? 'Manage users, files, and system operations' : 'Manage and verify your files securely'}
                    </p>
                </div>

                {isAdmin && adminStats && (
                    <div className="dashboard-stats" style={{gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))'}}>
                        <div className="stat-card">
                            <h3>Total Users</h3>
                            <div className="value">{adminStats.total_users}</div>
                            <small style={{color: 'var(--success-500)'}}>+{adminStats.recent_users_24h} today</small>
                        </div>
                        <div className="stat-card">
                            <h3>Total Files</h3>
                            <div className="value">{adminStats.total_files}</div>
                            <small style={{color: 'var(--success-500)'}}>+{adminStats.recent_uploads_24h} today</small>
                        </div>
                        <div className="stat-card">
                            <h3>Verifications</h3>
                            <div className="value">{adminStats.total_verifications}</div>
                            <small>{adminStats.recent_verifications_24h} today</small>
                        </div>
                        <div className="stat-card">
                            <h3>Storage</h3>
                            <div className="value">{adminStats.total_storage_mb}MB</div>
                            <small>{formatBytes(adminStats.total_storage_bytes)}</small>
                        </div>
                        <div className="stat-card">
                            <h3>Success Rate</h3>
                            <div className="value" style={{color: 'var(--success-500)'}}>{adminStats.verification_success_rate}%</div>
                            <small>Verification accuracy</small>
                        </div>
                    </div>
                )}

                {!isAdmin && (
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
                )}

                {isAdmin && (
                    <div style={{marginBottom: '2rem'}}>
                        <div style={{display: 'flex', gap: '10px', borderBottom: '2px solid #e5e7eb', marginBottom: '20px'}}>
                            <button 
                                className={`btn ${activeTab === 'files' ? 'btn-primary' : 'btn-secondary'}`}
                                onClick={() => setActiveTab('files')}
                                style={{borderRadius: '8px 8px 0 0', borderBottom: activeTab === 'files' ? '3px solid #667eea' : 'none'}}
                            >
                                📁 My Files ({files.length})
                            </button>
                            <button 
                                className={`btn ${activeTab === 'users' ? 'btn-primary' : 'btn-secondary'}`}
                                onClick={() => setActiveTab('users')}
                                style={{borderRadius: '8px 8px 0 0', borderBottom: activeTab === 'users' ? '3px solid #667eea' : 'none'}}
                            >
                                👥 All Users ({allUsers.length})
                            </button>
                            <button 
                                className={`btn ${activeTab === 'allfiles' ? 'btn-primary' : 'btn-secondary'}`}
                                onClick={() => setActiveTab('allfiles')}
                                style={{borderRadius: '8px 8px 0 0', borderBottom: activeTab === 'allfiles' ? '3px solid #667eea' : 'none'}}
                            >
                                🗂️ All Files ({allFiles.length})
                            </button>
                            <button 
                                className={`btn ${activeTab === 'verifications' ? 'btn-primary' : 'btn-secondary'}`}
                                onClick={() => setActiveTab('verifications')}
                                style={{borderRadius: '8px 8px 0 0', borderBottom: activeTab === 'verifications' ? '3px solid #667eea' : 'none'}}
                            >
                                ✓ Verifications ({verifications.length})
                            </button>
                            <button 
                                className={`btn ${activeTab === 'activity' ? 'btn-primary' : 'btn-secondary'}`}
                                onClick={() => setActiveTab('activity')}
                                style={{borderRadius: '8px 8px 0 0', borderBottom: activeTab === 'activity' ? '3px solid #667eea' : 'none'}}
                            >
                                📊 Activity
                            </button>
                        </div>
                    </div>
                )}

                {(!isAdmin || activeTab === 'files') && (
                    <>
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
                                        isAdmin={isAdmin}
                                    />
                                ) : null)
                            )}
                        </div>
                    </>
                )}

                {isAdmin && activeTab === 'users' && (
                    <div className="card">
                        <h3 style={{marginBottom: '1rem'}}>User Management</h3>
                        <table style={{width: '100%', borderCollapse: 'collapse'}}>
                            <thead>
                                <tr style={{borderBottom: '2px solid #e5e7eb'}}>
                                    <th style={{padding: '12px', textAlign: 'left'}}>Username</th>
                                    <th style={{padding: '12px', textAlign: 'left'}}>Email</th>
                                    <th style={{padding: '12px', textAlign: 'left'}}>Role</th>
                                    <th style={{padding: '12px', textAlign: 'left'}}>Status</th>
                                    <th style={{padding: '12px', textAlign: 'left'}}>Created</th>
                                    <th style={{padding: '12px', textAlign: 'left'}}>Actions</th>
                                </tr>
                            </thead>
                            <tbody>
                                {allUsers.map(user => (
                                    <tr key={user._id} style={{borderBottom: '1px solid #e5e7eb'}}>
                                        <td style={{padding: '12px'}}>{user.username}</td>
                                        <td style={{padding: '12px'}}>{user.email}</td>
                                        <td style={{padding: '12px'}}>
                                            <select 
                                                value={user.role || 'user'}
                                                onChange={(e) => updateUserRole(user._id, e.target.value)}
                                                className="btn btn-small"
                                            >
                                                <option value="user">User</option>
                                                <option value="admin">Admin</option>
                                            </select>
                                        </td>
                                        <td style={{padding: '12px'}}>
                                            <span className={`badge ${user.is_active ? 'badge-success' : 'badge-danger'}`}>
                                                {user.is_active ? 'Active' : 'Inactive'}
                                            </span>
                                        </td>
                                        <td style={{padding: '12px'}}>{formatDate(user.created_at)}</td>
                                        <td style={{padding: '12px'}}>
                                            <button 
                                                className={`btn btn-small ${user.is_active ? 'btn-danger' : 'btn-primary'}`}
                                                onClick={() => toggleUserStatus(user._id, user.is_active)}
                                            >
                                                {user.is_active ? 'Deactivate' : 'Activate'}
                                            </button>
                                        </td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    </div>
                )}

                {isAdmin && activeTab === 'allfiles' && (
                    <div className="card">
                        <h3 style={{marginBottom: '1rem'}}>All System Files</h3>
                        <table style={{width: '100%', borderCollapse: 'collapse'}}>
                            <thead>
                                <tr style={{borderBottom: '2px solid #e5e7eb'}}>
                                    <th style={{padding: '12px', textAlign: 'left'}}>Filename</th>
                                    <th style={{padding: '12px', textAlign: 'left'}}>Owner</th>
                                    <th style={{padding: '12px', textAlign: 'left'}}>Size</th>
                                    <th style={{padding: '12px', textAlign: 'left'}}>Upload Date</th>
                                    <th style={{padding: '12px', textAlign: 'left'}}>Verifications</th>
                                    <th style={{padding: '12px', textAlign: 'left'}}>Actions</th>
                                </tr>
                            </thead>
                            <tbody>
                                {allFiles.map(file => (
                                    <tr key={file._id} style={{borderBottom: '1px solid #e5e7eb'}}>
                                        <td style={{padding: '12px'}}>{file.filename}</td>
                                        <td style={{padding: '12px'}}>{file.username}</td>
                                        <td style={{padding: '12px'}}>{formatBytes(file.size)}</td>
                                        <td style={{padding: '12px'}}>{formatDate(file.upload_date)}</td>
                                        <td style={{padding: '12px'}}>{file.verification_count || 0}</td>
                                        <td style={{padding: '12px'}}>
                                            <button 
                                                className="btn btn-small btn-danger"
                                                onClick={() => deleteFileAdmin(file.file_id)}
                                            >
                                                Delete
                                            </button>
                                        </td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    </div>
                )}

                {isAdmin && activeTab === 'verifications' && (
                    <div className="card">
                        <h3 style={{marginBottom: '1rem'}}>Verification Logs</h3>
                        <table style={{width: '100%', borderCollapse: 'collapse'}}>
                            <thead>
                                <tr style={{borderBottom: '2px solid #e5e7eb'}}>
                                    <th style={{padding: '12px', textAlign: 'left'}}>File</th>
                                    <th style={{padding: '12px', textAlign: 'left'}}>User</th>
                                    <th style={{padding: '12px', textAlign: 'left'}}>Timestamp</th>
                                    <th style={{padding: '12px', textAlign: 'left'}}>Hash</th>
                                    <th style={{padding: '12px', textAlign: 'left'}}>Signature</th>
                                    <th style={{padding: '12px', textAlign: 'left'}}>Result</th>
                                </tr>
                            </thead>
                            <tbody>
                                {verifications.map(verif => (
                                    <tr key={verif._id} style={{borderBottom: '1px solid #e5e7eb'}}>
                                        <td style={{padding: '12px'}}>{verif.filename}</td>
                                        <td style={{padding: '12px'}}>{verif.username}</td>
                                        <td style={{padding: '12px'}}>{formatDate(verif.timestamp)}</td>
                                        <td style={{padding: '12px'}}>
                                            <span className={`badge ${verif.hash_match ? 'badge-success' : 'badge-danger'}`}>
                                                {verif.hash_match ? 'Match' : 'Mismatch'}
                                            </span>
                                        </td>
                                        <td style={{padding: '12px'}}>
                                            <span className={`badge ${verif.signature_valid ? 'badge-success' : 'badge-danger'}`}>
                                                {verif.signature_valid ? 'Valid' : 'Invalid'}
                                            </span>
                                        </td>
                                        <td style={{padding: '12px'}}>
                                            <span className={`badge ${verif.verified ? 'badge-success' : 'badge-danger'}`}>
                                                {verif.verified ? 'VERIFIED' : 'FAILED'}
                                            </span>
                                        </td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    </div>
                )}

                {isAdmin && activeTab === 'activity' && (
                    <div className="card">
                        <h3 style={{marginBottom: '1rem'}}>System Activity (Last 24h)</h3>
                        {timeline.map((event, idx) => (
                            <div key={idx} style={{padding: '15px', borderLeft: '3px solid #667eea', marginBottom: '12px', background: '#f9fafb', borderRadius: '0 8px 8px 0'}}>
                                <div style={{display: 'flex', justifyContent: 'space-between', alignItems: 'center'}}>
                                    <div>
                                        <span className={`badge ${event.type === 'upload' ? 'badge-info' : 'badge-warning'}`}>
                                            {event.type.toUpperCase()}
                                        </span>
                                        <strong style={{marginLeft: '10px'}}>{event.username}</strong>
                                        <span style={{margin: '0 10px', color: '#6b7280'}}>→</span>
                                        <strong>{event.filename}</strong>
                                        {event.type === 'verification' && (
                                            <span className={`badge ${event.verified ? 'badge-success' : 'badge-danger'}`} style={{marginLeft: '10px'}}>
                                                {event.verified ? '✓ Verified' : '✗ Failed'}
                                            </span>
                                        )}
                                    </div>
                                    <div style={{fontSize: '0.85em', color: '#6b7280'}}>{formatDate(event.timestamp)}</div>
                                </div>
                            </div>
                        ))}
                    </div>
                )}
            </div>
        </>
    );
}

// Main App Component
function App() {
    const [isAuthenticated, setIsAuthenticated] = useState(false);
    const [isAdmin, setIsAdmin] = useState(false);
    const [currentUser, setCurrentUser] = useState(null);
    const [currentView, setCurrentView] = useState('login'); // 'login' or 'register'

    useEffect(() => {
        // Check if user has a token
        const token = api.getToken();
        const userData = localStorage.getItem('user_data');
        if (token && userData) {
            const user = JSON.parse(userData);
            setCurrentUser(user);
            setIsAuthenticated(true);
            setIsAdmin(user.is_admin || false);
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

    const handleLogin = async (userData) => {
        setCurrentUser(userData);
        setIsAuthenticated(true);
        // Check role from userData
        const adminStatus = userData.role === 'admin' || userData.is_admin || false;
        setIsAdmin(adminStatus);
        localStorage.setItem('user_data', JSON.stringify(userData));
    };

    const handleLogout = () => {
        api.logout();
        localStorage.removeItem('user_data');
        setCurrentUser(null);
        setIsAuthenticated(false);
        setIsAdmin(false);
        setCurrentView('login');
    };

    if (isAuthenticated) {
        return <Dashboard onLogout={handleLogout} currentUser={currentUser} />;
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

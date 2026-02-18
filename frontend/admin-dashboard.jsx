// Admin Dashboard Component for File Integrity Platform

// Add this to app.jsx after the Dashboard component

// Admin Dashboard Component
function AdminDashboard({ onLogout }) {
    const [stats, setStats] = useState({ total_users: 0, total_files: 0, total_verifications: 0 });
    const [users, setUsers] = useState([]);
    const [allFiles, setAllFiles] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState('');
    const [success, setSuccess] = useState('');
    const [activeTab, setActiveTab] = useState('overview'); // 'overview', 'users', 'files'

    useEffect(() => {
        loadAdminData();
    }, []);

    const loadAdminData = async () => {
        try {
            console.log('[AdminDashboard] Loading admin data...');
            const token = api.getToken();
            
            // Load stats - Try admin endpoint first, fall back to calculating from files
            console.log('[AdminDashboard] Fetching stats...');
            const statsResponse = await fetch('http://localhost:8000/api/v1/admin/stats', {
                headers: { 'Authorization': `Bearer ${token}` }
            });
            if (statsResponse.ok) {
                const statsData = await statsResponse.json();
                console.log('[AdminDashboard] Stats received:', statsData);
                setStats(statsData);
            } else {
                console.warn('[AdminDashboard] Stats endpoint failed:', statsResponse.status);
            }

            // Load users - Try admin endpoint first
            console.log('[AdminDashboard] Fetching users...');
            const usersResponse = await fetch('http://localhost:8000/api/v1/admin/users', {
                headers: { 'Authorization': `Bearer ${token}` }
            });
            if (usersResponse.ok) {
                const usersData = await usersResponse.json();
                console.log('[AdminDashboard] Users received:', usersData);
                setUsers(usersData.users || []);
            } else {
                console.warn('[AdminDashboard] Users endpoint failed:', usersResponse.status);
            }

            // Load all files - Use the working user files endpoint
            console.log('[AdminDashboard] Fetching files from user endpoint...');
            const filesData = await api.listFiles();
            console.log('[AdminDashboard] Files data:', filesData);
            if (filesData && filesData.files) {
                console.log('[AdminDashboard] Setting files:', filesData.files.length, 'files');
                setAllFiles(filesData.files);
                
                // Update stats if admin endpoint didn't work
                if (!statsResponse.ok) {
                    const calculatedStats = {
                        total_files: filesData.files.length,
                        verified_files: filesData.files.filter(f => f.verification_status === 'verified').length,
                        tampered_files: filesData.files.filter(f => f.verification_status === 'tampered').length,
                        pending_files: filesData.files.filter(f => f.verification_status === 'pending').length,
                        total_verifications: filesData.files.reduce((sum, f) => sum + (f.verification_count || 0), 0),
                        storage_used_mb: filesData.files.reduce((sum, f) => sum + (f.size || 0), 0) / (1024 * 1024)
                    };
                    console.log('[AdminDashboard] Calculated stats:', calculatedStats);
                    setStats(calculatedStats);
                }
            } else {
                console.error('[AdminDashboard] No files data received');
            }

            setLoading(false);
        } catch (err) {
            console.error('Admin data load error:', err);
            setError('Failed to load admin data: ' + err.message);
            setLoading(false);
        }
    };

    const handleUploadSuccess = async () => {
        setSuccess('File uploaded successfully!');
        await loadAdminData();
        setTimeout(() => setSuccess(''), 3000);
    };

    if (loading) {
        return <LoadingOverlay message="Loading admin dashboard..." />;
    }

    return (
        <>
            <header className="header">
                <div className="header-content">
                    <div className="logo">
                        <div className="logo-icon">🔐</div>
                        <div className="logo-text">
                            <h1>Admin Dashboard</h1>
                            <p>System Management</p>
                        </div>
                    </div>
                    <div className="nav-buttons">
                        <div className="user-info">
                            <span>👤</span>
                            <span style={{ color: 'var(--warning-500)', fontWeight: 600 }}>Administrator</span>
                        </div>
                        <button className="btn btn-secondary btn-small" onClick={onLogout}>
                            Logout
                        </button>
                    </div>
                </div>
            </header>

            <div className="container">
                {error && <Alert type="error" message={error} onClose={() => setError('')} />}
                {success && <Alert type="success" message={success} onClose={() => setSuccess('')} />}

                <div className="dashboard-header">
                    <h2>System Overview</h2>
                    <p style={{ color: 'var(--text-muted)' }}>Monitor and manage the platform</p>
                </div>

                <div className="dashboard-stats">
                    <div className="stat-card">
                        <h3>Total Files</h3>
                        <div className="value">{stats.total_files}</div>
                    </div>
                    <div className="stat-card">
                        <h3>Verified Files</h3>
                        <div className="value" style={{ color: 'var(--success-500)' }}>{stats.verified_files}</div>
                    </div>
                    <div className="stat-card">
                        <h3>Total Verifications</h3>
                        <div className="value">{stats.total_verifications}</div>
                    </div>
                </div>
File Upload Section */}
                <FileUpload onUploadSuccess={handleUploadSuccess} />

                {/* 
                {/* Tab Navigation */}
                <div style={{ marginTop: '2rem', marginBottom: '1rem', display: 'flex', gap: '1rem', borderBottom: '1px solid var(--border-color)' }}>
                    <button 
                        onClick={() => setActiveTab('overview')}
                        style={{ 
                            padding: '0.75rem 1.5rem', 
                            background: 'none', 
                            border: 'none', 
                            borderBottom: activeTab === 'overview' ? '2px solid var(--primary-500)' : '2px solid transparent',
                            color: activeTab === 'overview' ? 'var(--primary-500)' : 'var(--text-secondary)',
                            cursor: 'pointer',
                            fontWeight: 600
                        }}>
                        Overview
                    </button>
                    <button 
                        onClick={() => setActiveTab('files')}
                        style={{ 
                            padding: '0.75rem 1.5rem', 
                            background: 'none', 
                            border: 'none', 
                            borderBottom: activeTab === 'files' ? '2px solid var(--primary-500)' : '2px solid transparent',
                            color: activeTab === 'files' ? 'var(--primary-500)' : 'var(--text-secondary)',
                            cursor: 'pointer',
                            fontWeight: 600
                        }}>
                        All Files ({allFiles.length})
                    </button>
                </div>

                {/* Files Tab */}
                {activeTab === 'files' && (
                    <div className="file-list">
                        <div className="file-list-header">
                            <h3>All Files in System</h3>
                            <button 
                                onClick={loadAdminData}
                                style={{
                                    padding: '0.5rem 1rem',
                                    background: 'var(--primary-500)',
                                    color: 'white',
                                    border: 'none',
                                    borderRadius: '6px',
                                    cursor: 'pointer',
                                    fontSize: '0.875rem',
                                    fontWeight: 500
                                }}>
                                🔄 Refresh All
                            </button>
                        </div>
                        {allFiles.map(file => (
                            <div key={file.file_id} className="file-item">
                                <div className="file-info">
                                    <div className="file-name">{file.filename}</div>
                                    <div className="file-meta">
                                        User: {file.user_id} • 
                                        Size: {(file.size / 1024).toFixed(2)} KB • 
                                        Hash: {file.file_hash.substring(0, 16)}...
                                    </div>
                                    <div className="file-meta">
                                        Uploaded: {new Date(file.upload_date).toLocaleString()} • 
                                        Verifications: {file.verification_count}
                                    </div>
                                    <div style={{ marginTop: '0.5rem' }}>
                                        {file.verification_status === 'verified' && <span className="badge badge-verified">✓ Verified</span>}
                                        {file.verification_status === 'tampered' && <span className="badge badge-tampered">✗ Rejected</span>}
                                        {file.verification_status === 'pending' && <span className="badge badge-pending">⏳ Pending</span>}
                                    </div>
                                </div>
                                <div style={{ display: 'flex', gap: '0.5rem', flexWrap: 'wrap' }}>
                                    <button
                                        onClick={async () => {
                                            try {
                                                await api.downloadFile(file.file_id, file.filename);
                                                setSuccess('File opened/downloaded!');
                                            } catch (err) {
                                                setError('Failed to open file: ' + err.message);
                                            }
                                        }}
                                        style={{
                                            padding: '0.5rem 1rem',
                                            background: 'var(--info-500, #3b82f6)',
                                            color: 'white',
                                            border: 'none',
                                            borderRadius: '6px',
                                            cursor: 'pointer',
                                            fontSize: '0.875rem',
                                            fontWeight: 500
                                        }}>
                                        📂 Open
                                    </button>
                                    <button
                                        onClick={async () => {
                                            try {
                                                await api.verifyFile(file.file_id);
                                                setSuccess('File verification completed!');
                                                await loadAdminData();
                                            } catch (err) {
                                                setError('Verification failed: ' + err.message);
                                            }
                                        }}
                                        style={{
                                            padding: '0.5rem 1rem',
                                            background: 'var(--success-500)',
                                            color: 'white',
                                            border: 'none',
                                            borderRadius: '6px',
                                            cursor: 'pointer',
                                            fontSize: '0.875rem',
                                            fontWeight: 500
                                        }}>
                                        ✓ Verified
                                    </button>
                                    <button
                                        onClick={async () => {
                                            if (confirm(`Delete "${file.filename}"? This cannot be undone.`)) {
                                                try {
                                                    await api.deleteFile(file.file_id);
                                                    setSuccess('File deleted successfully!');
                                                    await loadAdminData();
                                                } catch (err) {
                                                    setError('Delete failed: ' + err.message);
                                                }
                                            }
                                        }}
                                        style={{
                                            padding: '0.5rem 1rem',
                                            background: 'var(--error-500)',
                                            color: 'white',
                                            border: 'none',
                                            borderRadius: '6px',
                                            cursor: 'pointer',
                                            fontSize: '0.875rem',
                                            fontWeight: 500
                                        }}>
                                        🗑 Delete
                                    </button>
                                </div>
                            </div>
                        ))}
                    </div>
                )}

                {/* Overview Tab */}
                {activeTab === 'overview' && (
                    <div style={{ marginTop: '2rem' }}>
                        <div style={{ background: 'rgba(30, 41, 59, 0.6)', padding: '2rem', borderRadius: '12px', border: '1px solid var(--border-color)' }}>
                            <h3 style={{ marginBottom: '1rem' }}>📊 System Health</h3>
                            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '1rem' }}>
                                <div>
                                    <p style={{ color: 'var(--text-muted)', fontSize: '0.875rem' }}>Verification Rate</p>
                                    <p style={{ fontSize: '1.5rem', fontWeight: 600 }}>
                                        {stats.total_files > 0 ? Math.round((stats.verified_files / stats.total_files) * 100) : 0}%
                                    </p>
                                </div>
                                <div>
                                    <p style={{ color: 'var(--text-muted)', fontSize: '0.875rem' }}>Pending Review</p>
                                    <p style={{ fontSize: '1.5rem', fontWeight: 600, color: 'var(--warning-500)' }}>
                                        {stats.pending_files}
                                    </p>
                                </div>
                            </div>
                        </div>
                    </div>
                )}
            </div>
        </>
    );
}

// Admin Dashboard Component for File Integrity Platform

// Add this to app.jsx after the Dashboard component

// Admin Dashboard Component
function AdminDashboard({ onLogout }) {
    const [stats, setStats] = useState({ total_users: 0, total_files: 0, total_verifications: 0 });
    const [users, setUsers] = useState([]);
    const [allFiles, setAllFiles] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState('');
    const [activeTab, setActiveTab] = useState('overview'); // 'overview', 'users', 'files'

    useEffect(() => {
        loadAdminData();
    }, []);

    const loadAdminData = async () => {
        try {
            const token = api.getToken();
            
            // Load stats
            const statsResponse = await fetch('http://localhost:8000/api/v1/admin/stats', {
                headers: { 'Authorization': `Bearer ${token}` }
            });
            if (statsResponse.ok) {
                const statsData = await statsResponse.json();
                setStats(statsData);
            }

            // Load users
            const usersResponse = await fetch('http://localhost:8000/api/v1/admin/users', {
                headers: { 'Authorization': `Bearer ${token}` }
            });
            if (usersResponse.ok) {
                const usersData = await usersResponse.json();
                setUsers(usersData.users || []);
            }

            // Load all files
            const filesResponse = await fetch('http://localhost:8000/api/v1/admin/files', {
                headers: { 'Authorization': `Bearer ${token}` }
            });
            if (filesResponse.ok) {
                const filesData = await filesResponse.json();
                setAllFiles(filesData.files || []);
            }

            setLoading(false);
        } catch (err) {
            console.error('Admin data load error:', err);
            setError('Failed to load admin data');
            setLoading(false);
        }
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

                <div className="dashboard-header">
                    <h2>System Overview</h2>
                    <p style={{ color: 'var(--text-muted)' }}>Monitor and manage the platform</p>
                </div>

                <div className="dashboard-stats">
                    <div className="stat-card">
                        <h3>Total Users</h3>
                        <div className="value">{stats.total_users}</div>
                    </div>
                    <div className="stat-card">
                        <h3>Total Files</h3>
                        <div className="value">{stats.total_files}</div>
                    </div>
                    <div className="stat-card">
                        <h3>Verified Files</h3>
                        <div className="value" style={{ color: 'var(--success-500)' }}>{stats.verified_files}</div>
                    </div>
                    <div className="stat-card">
                        <h3>Tampered Files</h3>
                        <div className="value" style={{ color: 'var(--error-500)' }}>{stats.tampered_files}</div>
                    </div>
                    <div className="stat-card">
                        <h3>Total Verifications</h3>
                        <div className="value">{stats.total_verifications}</div>
                    </div>
                    <div className="stat-card">
                        <h3>Storage Used</h3>
                        <div className="value">{stats.total_storage_mb} MB</div>
                    </div>
                </div>

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
                        onClick={() => setActiveTab('users')}
                        style={{ 
                            padding: '0.75rem 1.5rem', 
                            background: 'none', 
                            border: 'none', 
                            borderBottom: activeTab === 'users' ? '2px solid var(--primary-500)' : '2px solid transparent',
                            color: activeTab === 'users' ? 'var(--primary-500)' : 'var(--text-secondary)',
                            cursor: 'pointer',
                            fontWeight: 600
                        }}>
                        Users ({users.length})
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

                {/* Users Tab */}
                {activeTab === 'users' && (
                    <div className="file-list">
                        <div className="file-list-header">
                            <h3>All Users</h3>
                        </div>
                        {users.map(user => (
                            <div key={user._id} className="file-item">
                                <div className="file-info">
                                    <div className="file-name">{user.username}</div>
                                    <div className="file-meta">
                                        Email: {user.email} • 
                                        Role: {user.is_admin ? 'Administrator' : 'User'} • 
                                        ID: {user._id}
                                    </div>
                                    {user.created_at && (
                                        <div className="file-meta">Joined: {new Date(user.created_at).toLocaleString()}</div>
                                    )}
                                </div>
                                <div>
                                    {user.is_admin && <span className="badge badge-verified">Admin</span>}
                                </div>
                            </div>
                        ))}
                    </div>
                )}

                {/* Files Tab */}
                {activeTab === 'files' && (
                    <div className="file-list">
                        <div className="file-list-header">
                            <h3>All Files in System</h3>
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
                                        {file.verification_status === 'tampered' && <span className="badge badge-tampered">⚠ Tampered</span>}
                                        {file.verification_status === 'pending' && <span className="badge badge-pending">⏳ Pending</span>}
                                    </div>
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
                                    <p style={{ color: 'var(--text-muted)', fontSize: '0.875rem' }}>Avg per User</p>
                                    <p style={{ fontSize: '1.5rem', fontWeight: 600 }}>
                                        {stats.total_users > 0 ? Math.round(stats.total_files / stats.total_users) : 0} files
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

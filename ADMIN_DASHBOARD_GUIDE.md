# Admin Dashboard Access Guide

## Overview
The File Integrity & Authenticity Verification Platform now includes a comprehensive admin dashboard with full administrative controls.

## Admin Dashboard Features

### 1. **System Statistics**
- Total users, files, and verifications
- Storage usage tracking
- Recent activity (last 24 hours)
- Verification success rate

### 2. **User Management**
- View all registered users
- Activate/Deactivate user accounts
- Change user roles (admin/user)
- View user activity history

### 3. **File Management**
- View all files from all users
- Monitor file uploads
- Permanently delete files (admin only)
- Track verification counts

### 4. **Verification Logs**
- View all verification attempts
- Track hash matches and signature validation
- Monitor verification success/failure rates

### 5. **Activity Timeline**
- Real-time system activity feed
- Upload and verification events
- User actions tracking

## Accessing the Admin Dashboard

### Option 1: Through Frontend
1. Open your browser and go to: **http://localhost:3000/admin.html**
2. You'll be redirected to login if not authenticated
3. Log in with admin credentials
4. Access the full admin dashboard

### Option 2: Direct API Access
Use the following admin endpoints:

```bash
# Get your admin token first
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "your_password"}'

# Save the token
TOKEN="your_token_here"

# Get system statistics
curl http://localhost:8000/api/v1/admin/stats \
  -H "Authorization: Bearer $TOKEN"

# Get all users
curl http://localhost:8000/api/v1/admin/users \
  -H "Authorization: Bearer $TOKEN"

# Get all files
curl http://localhost:8000/api/v1/admin/files \
  -H "Authorization: Bearer $TOKEN"

# Get verification logs
curl http://localhost:8000/api/v1/admin/verifications \
  -H "Authorization: Bearer $TOKEN"

# Get activity timeline
curl http://localhost:8000/api/v1/admin/activity-timeline?hours=24 \
  -H "Authorization: Bearer $TOKEN"
```

## Admin Endpoints Reference

### Statistics
- **GET** `/api/v1/admin/stats` - Get comprehensive system statistics

### User Management
- **GET** `/api/v1/admin/users` - Get all users (with pagination)
- **PATCH** `/api/v1/admin/users/{user_id}/status` - Activate/deactivate user
- **PATCH** `/api/v1/admin/users/{user_id}/role` - Update user role
- **GET** `/api/v1/admin/users/{user_id}/activity` - Get user activity

### File Management
- **GET** `/api/v1/admin/files` - Get all files (with pagination)
- **DELETE** `/api/v1/admin/files/{file_id}` - Permanently delete file

### Verification Management
- **GET** `/api/v1/admin/verifications` - Get all verification records

### Activity
- **GET** `/api/v1/admin/activity-timeline` - Get system activity timeline

## Creating an Admin User

If you don't have an admin user yet, create one using the Python script:

```bash
# Create admin user
python create_admin.py
```

Or manually set a user as admin in MongoDB:

```javascript
// In MongoDB shell
use file_integrity_db

db.users.updateOne(
  { username: "your_username" },
  { $set: { role: "admin" } }
)
```

## Admin Dashboard URLs

- **Admin Dashboard**: http://localhost:3000/admin.html
- **API Documentation**: http://localhost:8000/docs (shows all admin endpoints)
- **Regular Dashboard**: http://localhost:3000

## Security Notes

1. Admin endpoints require authentication (JWT token)
2. Only users with `role: "admin"` can access admin endpoints
3. All admin actions are logged in audit logs
4. Admin users can:
   - View all system data
   - Modify user accounts
   - Delete any file
   - Access all verification records

## Admin Actions

### Activate/Deactivate User
```bash
curl -X PATCH http://localhost:8000/api/v1/admin/users/{user_id}/status \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"is_active": false}'
```

### Change User Role
```bash
curl -X PATCH http://localhost:8000/api/v1/admin/users/{user_id}/role \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"role": "admin"}'
```

### Delete File Permanently
```bash
curl -X DELETE http://localhost:8000/api/v1/admin/files/{file_id} \
  -H "Authorization: Bearer $TOKEN"
```

## Dashboard Features

The admin dashboard includes:
- 📊 Real-time statistics cards
- 👥 User management table with inline actions
- 📁 File browser with delete capabilities
- ✓ Verification history viewer
- 📈 Activity timeline with visual indicators
- 🎨 Modern, responsive UI with tabs
- 🔄 Auto-refresh capabilities

## Troubleshooting

### "Admin privileges required" error
- Check that your user has `role: "admin"` in the database
- Verify your JWT token is valid
- Ensure you're using the correct authorization header

### Admin endpoints return 404
- Verify the backend container is running
- Check that the latest code is deployed
- Restart the backend: `docker-compose restart backend`

### Cannot access admin.html
- Ensure frontend container is running
- Check that file exists at `frontend/admin.html`
- Verify nginx is serving the file correctly

## What's Next

The admin dashboard provides comprehensive control over the File Integrity Platform. You can:

1. Monitor system health and usage
2. Manage user accounts and permissions
3. Oversee all file operations
4. Track verification activities
5. Analyze system trends

For more information, consult the API documentation at http://localhost:8000/docs

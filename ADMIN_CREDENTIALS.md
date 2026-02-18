# Admin Credentials

## Default Admin Account

The system comes with a pre-configured admin account:

- **Username**: `admin`
- **Password**: `admin123`
- **Email**: `admin@test.com`

## How to Login

### Via Web Interface
1. Navigate to `http://localhost:3000` (or your frontend URL)
2. Enter username: `admin`
3. Enter password: `admin123`
4. Click "Sign In"

### Via API
```bash
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "admin123"}'
```

### Via CLI
```bash
cd cli
python client.py --username admin --password admin123
```

## Test User Account

There's also a test user account available:

- **Username**: `testuser`
- **Password**: `testpass123`
- **Email**: `test@test.com`

## Creating a New Admin User

If you need to create a new admin user, run:

```bash
python create_admin.py
```

This will prompt you to enter:
- Username
- Email
- Password (minimum 8 characters)

## Resetting Admin Password

If you've forgotten the admin password, you can reset it by running:

```bash
python reset_admin_password.py
```

(Note: You may need to create this script if it doesn't exist)

## Troubleshooting Login Issues

### 1. Verify the Backend is Running
```bash
# Check if the API server is running
curl http://localhost:8000/health
```

Expected response:
```json
{
  "status": "healthy",
  "timestamp": "...",
  "version": "1.0.0"
}
```

### 2. Test Login via Command Line
```bash
cd "/Users/Dipesh/Desktop/five/File Integrity & Authenticity Verification System"
python3 -c "
from database import MongoDB
from services.auth_service import auth_service

MongoDB.connect()
result = auth_service.login_user('admin', 'admin123')
print('Login successful!')
print(f'Token: {result[\"access_token\"][:50]}...')
"
```

### 3. Verify User Exists in Database
```bash
python3 -c "
from database import MongoDB, get_collection
MongoDB.connect()
users = get_collection('users')
admin = users.find_one({'username': 'admin'})
if admin:
    print('Admin user found!')
    print(f'Email: {admin[\"email\"]}')
    print(f'Is Admin: {admin.get(\"is_admin\", False)}')
else:
    print('Admin user not found!')
"
```

### 4. Check Frontend API Configuration
Make sure the frontend [api.js](frontend/api.js) has the correct API_BASE_URL:
```javascript
const API_BASE_URL = 'http://localhost:8000/api/v1';
```

### 5. Check Browser Console
Open the browser's Developer Tools (F12) and check the Console tab for any errors when trying to login.

### 6. Check Network Tab
In the browser's Developer Tools, go to the Network tab and monitor the login request:
- URL should be: `http://localhost:8000/api/v1/auth/login`
- Method: POST
- Status: 200 (if successful) or 401 (if credentials are wrong)

## Common Issues

### "Connection Refused" Error
- **Cause**: Backend server is not running
- **Solution**: Start the backend server:
  ```bash
  uvicorn gateway.main:app --reload --host 0.0.0.0 --port 8000
  ```

### "Invalid username or password" Error
- **Cause**: Wrong credentials
- **Solution**: Make sure you're using `admin` / `admin123`

### "CORS" Error in Browser
- **Cause**: Frontend and backend CORS mismatch
- **Solution**: The backend already has CORS enabled for all origins in [gateway/main.py](gateway/main.py)

### Database Not Connected
- **Cause**: MongoDB is not running
- **Solution**: Start MongoDB:
  ```bash
  # If using Docker
  docker-compose up -d mongodb
  
  # If using local MongoDB
  brew services start mongodb-community  # macOS
  sudo systemctl start mongod            # Linux
  ```

## Security Recommendations

⚠️ **IMPORTANT**: Change the default admin password in production!

1. Create a new admin user with a strong password
2. Delete or disable the default admin account
3. Use environment variables for sensitive credentials
4. Enable two-factor authentication (if available)

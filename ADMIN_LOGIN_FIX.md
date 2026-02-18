# Admin Login - Quick Fix Guide

## ✅ VERIFIED: Your System is Working!

I've tested your system and confirmed that **the admin login is working correctly**:

- ✅ Backend server: Running on http://localhost:8000
- ✅ Frontend server: Running on http://localhost:3000
- ✅ Database: Connected and working
- ✅ Admin user: Exists and active
- ✅ Authentication: Fully functional

## 🔑 Admin Credentials

```
Username: admin
Password: admin123
```

**Important:** Use exactly these credentials (all lowercase, no spaces)

## 🚀 How to Login

### Method 1: Use the Main Application

1. Open your browser
2. Go to: **http://localhost:3000**
3. Type username: `admin`
4. Type password: `admin123`
5. Click "Sign In"

### Method 2: Use the Test Page (Recommended for Testing)

I've created a dedicated test page for you:

1. Open your browser
2. Go to: **file:///Users/Dipesh/Desktop/five/File%20Integrity%20&%20Authenticity%20Verification%20System/test_login.html**
3. Click "Test Login" (credentials are pre-filled)
4. You'll see a detailed response showing if login works

Or simply open this file in your browser:
```
/Users/Dipesh/Desktop/five/File Integrity & Authenticity Verification System/test_login.html
```

### Method 3: Command Line Test

```bash
cd "/Users/Dipesh/Desktop/five/File Integrity & Authenticity Verification System"
python3 test_admin_login.py
```

Expected output:
```
✓ ALL TESTS PASSED

You can now login with:
  Username: admin
  Password: admin123
```

## 🔍 If Login Still Doesn't Work

### Common Issues & Solutions

#### 1. "Invalid username or password"
- ✅ Make sure you're typing exactly: `admin` (lowercase)
- ✅ Password is: `admin123` (no spaces)
- ✅ Check Caps Lock is off

#### 2. Connection/Network Errors
Check if servers are running:
```bash
# Check backend
curl http://localhost:8000/health

# Should return:
# {"status":"healthy","timestamp":"...","version":"1.0.0"}
```

If backend is not running:
```bash
cd "/Users/Dipesh/Desktop/five/File Integrity & Authenticity Verification System"
uvicorn gateway.main:app --reload --host 0.0.0.0 --port 8000
```

#### 3. Frontend Issues
- Clear browser cache (Ctrl+Shift+Delete or Cmd+Shift+Delete)
- Try a different browser (Chrome, Firefox, Safari)
- Check browser console for errors (F12 → Console tab)

#### 4. Password Changed/Forgotten
Reset the admin password:
```bash
python3 reset_admin_password.py
```

## 📝 New Files Created for You

I've created several helpful files:

1. **test_login.html** - Interactive test page to verify login works
2. **test_admin_login.py** - Command-line script to test admin login
3. **reset_admin_password.py** - Reset admin password if needed
4. **ADMIN_CREDENTIALS.md** - Complete credentials documentation
5. **LOGIN_TROUBLESHOOTING.md** - Detailed troubleshooting guide
6. **ADMIN_LOGIN_FIX.md** - This file

## 🎯 Recommended Steps

1. **First, verify the backend works:**
   ```bash
   python3 test_admin_login.py
   ```
   This should show "✓ ALL TESTS PASSED"

2. **Test the API directly:**
   ```bash
   curl -X POST http://localhost:8000/api/v1/auth/login \
     -H "Content-Type: application/json" \
     -d '{"username": "admin", "password": "admin123"}'
   ```
   This should return a JSON with `"access_token"` and `"is_admin": true`

3. **Test in the browser:**
   - Open: http://localhost:3000
   - Login with: admin / admin123

4. **If browser login fails but command-line works:**
   - The issue is in the frontend
   - Check browser console (F12)
   - Try the test_login.html page
   - Clear browser cache

## 🛠️ Useful Commands

### View All Users
```bash
python3 -c "
from database import MongoDB, get_collection
MongoDB.connect()
users = get_collection('users')
for u in users.find():
    print(f'User: {u[\"username\"]}, Admin: {u.get(\"is_admin\", False)}')
"
```

### Create New Admin
```bash
python3 create_admin.py
```

### Start Backend Server
```bash
uvicorn gateway.main:app --reload --host 0.0.0.0 --port 8000
```

### Start Frontend Server
```bash
cd frontend
python3 -m http.server 3000
```

## 📞 Need More Help?

If you're still having issues, please provide:

1. **What happens when you try to login?**
   - Error message shown
   - Screenshot if possible

2. **Output of this command:**
   ```bash
   python3 test_admin_login.py
   ```

3. **Browser console errors:**
   - Press F12
   - Go to Console tab
   - Copy any red error messages

4. **Network request details:**
   - Press F12
   - Go to Network tab
   - Try to login
   - Click on the "/auth/login" request
   - Share the Status Code and Response

## 📚 Additional Documentation

- [ADMIN_CREDENTIALS.md](ADMIN_CREDENTIALS.md) - Full credentials documentation
- [LOGIN_TROUBLESHOOTING.md](LOGIN_TROUBLESHOOTING.md) - Detailed troubleshooting
- [QUICK_START.md](QUICK_START.md) - Quick start guide
- [README.md](README.md) - Main project documentation

## ✨ Summary

Your authentication system **is working correctly**. The admin credentials are:

**Username:** `admin`  
**Password:** `admin123`

If you're having trouble logging in through the web interface, use the test tools I've provided to isolate the issue.

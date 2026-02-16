# 🔐 File Integrity Platform - Quick Guide

## 📚 **How to Verify Documents**

### Method 1: Through Web Interface (http://localhost:3000)

1. **Login** to your account
2. **Upload** a file with your password
3. **Click "Verify" button** on the file
4. System will:
   - Decrypt the file
   - Recalculate the hash
   - Compare with original hash
   - Verify digital signature
   - Show status: ✅ **Verified** or ⚠️ **Tampered**

### Method 2: Through API

```bash
# Get your JWT token
TOKEN=$(curl -s -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "dipesh", "password": "dipesh123"}' | \
  python3 -c "import sys, json; print(json.load(sys.stdin)['access_token'])")

# Verify a file
curl -X POST http://localhost:8000/api/v1/verify/FILE_ID_HERE \
  -H "Authorization: Bearer $TOKEN"
```

## 👑 **Admin User Setup**

### Create Admin User

```bash
cd "/Users/Dipesh/Desktop/five/File Integrity & Authenticity Verification System"
python3 create_admin.py
```

Follow the prompts to create admin account.

### Quick Admin Setup (Automated)

```bash
echo -e "admin\nadmin@fileintegrity.local\nadmin123456" | python3 create_admin.py
```

This creates:
- **Username**: admin
- **Password**: admin123456
- **Role**: Administrator

## 🎯 **Admin Dashboard Features**

After logging in as admin, you'll see:

### Overview Tab
- Total users count
- Total files in system
- Verified vs tampered files
- Total storage used
- Verification statistics

### Users Tab
- List all registered users
- See user roles (Admin/User)
- View user IDs and emails
- Registration dates

### Files Tab
- View ALL files in the system
- See file owner (user_id)
- Check verification status
- Monitor file sizes and hashes

## 🔍 **Verification Workflow**

```
1. Upload File → Encrypted with AES-256
2. Hash Created → SHA-256 of original file
3. Signed → RSA-2048 digital signature
4. Stored → Encrypted file saved
5. Verify Click → 
   ├─ Decrypt file
   ├─ Recalculate hash
   ├─ Compare hashes
   ├─ Verify signature
   └─ Result: VERIFIED or TAMPERED
```

## 🚀 **Current Status**

✅ Backend: Running on http://localhost:8000
✅ Frontend: Running on http://localhost:3000
✅ MongoDB: Connected
✅ Admin Features: Available

## 👤 **Existing Users**

**Regular User:**
- Username: dipesh
- Password: dipesh123
- Access: User dashboard

**Admin User:**
- Create using: `python3 create_admin.py`
- Access: Admin dashboard with system overview

## 📊 **What Each User Sees**

### Regular User Dashboard
- Their own files only
- Upload/download/verify/delete their files
- Personal statistics

### Admin Dashboard
- All users in system
- All files from all users
- System-wide statistics
- Full platform overview
- Cannot modify other users' files

## 🎨 **Visual Indicators**

- ✅ **Green Badge**: File is verified, integrity confirmed
- ⚠️ **Red Badge**: File has been tampered with
- ⏳ **Yellow Badge**: File not yet verified
- 👑 **Admin Badge**: Administrator user

## 🔧 **Next Steps**

1. **Create Admin**: Run `python3 create_admin.py`
2. **Login as Admin**: Use admin credentials
3. **Verify Files**: Click verify button on any file
4. **Monitor**: Check admin dashboard for system health

---

**Verification is instant!** Just click the "Verify" button on any file.

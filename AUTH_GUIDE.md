# Authentication Guide - SATRIA JKN API

## Overview

SATRIA JKN API menggunakan JWT (JSON Web Token) untuk autentikasi dan otorisasi.

## User Roles

Sistem mendukung 3 role pengguna:

- **admin**: Akses penuh ke semua fitur dan endpoint
- **auditor**: Akses ke alerts, audit trail, dan data klaim
- **user**: Akses standar ke data umum

## Default Users

Setelah instalasi, tersedia 3 user default:

| Username | Password   | Role    | Email                 |
| -------- | ---------- | ------- | --------------------- |
| admin    | admin123   | admin   | admin@satriajkn.com   |
| auditor  | auditor123 | auditor | auditor@satriajkn.com |
| user     | user123    | user    | user@satriajkn.com    |

⚠️ **PENTING**: Ganti password default ini setelah instalasi!

## Authentication Endpoints

### 1. Register User

**POST** `/api/auth/register`

Request body:

```json
{
  "username": "newuser",
  "email": "newuser@example.com",
  "password": "securepassword",
  "full_name": "New User",
  "role": "user"
}
```

Response (201):

```json
{
  "message": "User registered successfully",
  "user": {
    "user_id": "uuid",
    "username": "newuser",
    "email": "newuser@example.com",
    "full_name": "New User",
    "role": "user",
    "created_at": "2025-11-13T10:00:00"
  }
}
```

### 2. Login

**POST** `/api/auth/login`

Request body:

```json
{
  "username": "admin",
  "password": "admin123"
}
```

Response (200):

```json
{
  "message": "Login successful",
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "user": {
    "user_id": "uuid",
    "username": "admin",
    "email": "admin@satriajkn.com",
    "full_name": "Administrator",
    "role": "admin"
  }
}
```

### 3. Get Current User

**GET** `/api/auth/me`

Headers:

```
Authorization: Bearer <your_jwt_token>
```

Response (200):

```json
{
  "user_id": "uuid",
  "username": "admin",
  "email": "admin@satriajkn.com",
  "full_name": "Administrator",
  "role": "admin",
  "last_login": "2025-11-13T10:00:00",
  "created_at": "2025-11-10T00:00:00"
}
```

### 4. Change Password

**POST** `/api/auth/change-password`

Headers:

```
Authorization: Bearer <your_jwt_token>
```

Request body:

```json
{
  "old_password": "admin123",
  "new_password": "newSecurePassword123"
}
```

Response (200):

```json
{
  "message": "Password changed successfully"
}
```

## User Management (Admin Only)

### 5. Get All Users

**GET** `/api/users`

Headers:

```
Authorization: Bearer <admin_jwt_token>
```

Response (200):

```json
[
  {
    "user_id": "uuid",
    "username": "admin",
    "email": "admin@satriajkn.com",
    "full_name": "Administrator",
    "role": "admin",
    "is_active": 1,
    "created_at": "2025-11-10T00:00:00",
    "last_login": "2025-11-13T10:00:00"
  }
]
```

### 6. Get/Update/Delete User

**GET/PUT/DELETE** `/api/users/<user_id>`

Headers:

```
Authorization: Bearer <admin_jwt_token>
```

Update request body (PUT):

```json
{
  "email": "newemail@example.com",
  "full_name": "Updated Name",
  "role": "auditor",
  "is_active": 1
}
```

## Using JWT Token

### In Postman

1. Go to **Authorization** tab
2. Select **Bearer Token** type
3. Paste your JWT token

### In Code (JavaScript/Fetch)

```javascript
fetch("http://localhost:5000/api/dashboard/overview", {
  headers: {
    Authorization: `Bearer ${token}`,
    "Content-Type": "application/json",
  },
});
```

### In Code (Python/Requests)

```python
import requests

headers = {
    'Authorization': f'Bearer {token}',
    'Content-Type': 'application/json'
}

response = requests.get('http://localhost:5000/api/dashboard/overview', headers=headers)
```

### In cURL

```bash
curl -H "Authorization: Bearer YOUR_TOKEN_HERE" http://localhost:5000/api/dashboard/overview
```

## Protected Endpoints

### Token Required (All authenticated users)

- `/api/dashboard/overview` - GET
- `/api/peserta` - GET, POST
- `/api/peserta/<id>` - GET, PUT, DELETE
- `/api/faskes` - GET, POST
- `/api/faskes/<id>` - GET, PUT, DELETE
- `/api/klaim` - GET, POST
- `/api/klaim/<id>` - GET, PUT, DELETE
- `/api/diagnosis` - GET, POST
- `/api/tindakan` - GET, POST
- `/api/ai/recommendations` - GET, POST
- `/api/pembayaran` - GET, POST

### Admin & Auditor Only

- `/api/alerts` - GET, POST
- `/api/alerts/<id>` - GET, PUT, DELETE
- `/api/audit-trail` - GET, POST

### Admin Only

- `/api/settings` - GET, PUT
- `/api/users` - GET
- `/api/users/<id>` - GET, PUT, DELETE

## Error Responses

### 401 Unauthorized

```json
{
  "error": "Token is missing"
}
```

```json
{
  "error": "Token is invalid or expired"
}
```

```json
{
  "error": "Invalid username or password"
}
```

### 403 Forbidden

```json
{
  "error": "Admin access required"
}
```

```json
{
  "error": "Access denied. Required roles: admin, auditor"
}
```

### 409 Conflict

```json
{
  "error": "Username or email already exists"
}
```

## Token Details

- **Algorithm**: HS256
- **Expiration**: 24 hours
- **Payload includes**: user_id, username, role, exp, iat

## Security Best Practices

1. **Always use HTTPS** in production
2. **Change SECRET_KEY** in `auth.py` (use environment variable)
3. **Change default passwords** immediately after setup
4. **Implement token refresh** mechanism for production
5. **Add rate limiting** to prevent brute force attacks
6. **Store tokens securely** (never in localStorage for sensitive apps)
7. **Implement token revocation** for logout functionality
8. **Use strong passwords** with minimum requirements

## Environment Variables (Recommended for Production)

Create `.env` file:

```env
SECRET_KEY=your-very-secret-key-here-use-random-string
JWT_EXPIRATION_HOURS=24
DATABASE_NAME=satriajkn.db
```

## Testing Authentication

### 1. Login and save token

```bash
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}'
```

### 2. Use token to access protected endpoint

```bash
TOKEN="your_token_here"
curl -H "Authorization: Bearer $TOKEN" http://localhost:5000/api/dashboard/overview
```

### 3. Test unauthorized access

```bash
# Should return 401 error
curl http://localhost:5000/api/dashboard/overview
```

## Troubleshooting

### Token Expired

Login again to get a new token. Consider implementing token refresh.

### Invalid Token Format

Ensure format is: `Bearer <token>` with space between Bearer and token.

### User Not Active

Admin must reactivate user account via `/api/users/<user_id>` endpoint.

### Permission Denied

Check user role matches required role for endpoint.

## Next Steps

1. Install dependencies: `pip install -r requirements.txt`
2. Initialize database: `python database.py`
3. Start server: `python app.py`
4. Test login with default credentials
5. Change default passwords
6. Create additional users as needed

For more information, see the main [API_DOCUMENTATION.md](API_DOCUMENTATION.md)

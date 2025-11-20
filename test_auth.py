"""
Test Authentication Endpoints
Run with: python test_auth.py
"""

import requests
import json

BASE_URL = "http://localhost:5000"

def print_response(title, response):
    """Print formatted response"""
    print(f"\n{'='*60}")
    print(f"{title}")
    print(f"{'='*60}")
    print(f"Status Code: {response.status_code}")
    try:
        print(f"Response: {json.dumps(response.json(), indent=2)}")
    except:
        print(f"Response: {response.text}")

def test_authentication():
    """Test authentication flow"""
    
    print("\n🧪 Testing SATRIA JKN Authentication System\n")
    
    # Test 1: Register new user
    print("\n1️⃣  Testing User Registration...")
    register_data = {
        "username": "testuser",
        "email": "testuser@example.com",
        "password": "testpass123",
        "full_name": "Test User"
    }
    response = requests.post(f"{BASE_URL}/api/auth/register", json=register_data)
    print_response("REGISTER USER", response)
    
    # Test 2: Login with admin
    print("\n2️⃣  Testing Login (Admin)...")
    login_data = {
        "username": "admin",
        "password": "admin123"
    }
    response = requests.post(f"{BASE_URL}/api/auth/login", json=login_data)
    print_response("LOGIN ADMIN", response)
    
    if response.status_code == 200:
        admin_token = response.json()['token']
        print(f"\n✅ Admin Token: {admin_token[:50]}...")
        
        # Test 3: Get current user info
        print("\n3️⃣  Testing Get Current User...")
        headers = {"Authorization": f"Bearer {admin_token}"}
        response = requests.get(f"{BASE_URL}/api/auth/me", headers=headers)
        print_response("GET CURRENT USER", response)
        
        # Test 4: Access protected endpoint
        print("\n4️⃣  Testing Protected Endpoint (Dashboard)...")
        response = requests.get(f"{BASE_URL}/api/dashboard/overview", headers=headers)
        print_response("PROTECTED DASHBOARD", response)
        
        # Test 5: Get all users (Admin only)
        print("\n5️⃣  Testing Admin-Only Endpoint (Get All Users)...")
        response = requests.get(f"{BASE_URL}/api/users", headers=headers)
        print_response("GET ALL USERS", response)
        
        # Test 6: Change password
        print("\n6️⃣  Testing Change Password...")
        change_pass_data = {
            "old_password": "admin123",
            "new_password": "newadmin123"
        }
        response = requests.post(f"{BASE_URL}/api/auth/change-password", 
                                json=change_pass_data, headers=headers)
        print_response("CHANGE PASSWORD", response)
        
        # If password changed, change it back
        if response.status_code == 200:
            print("\n🔄 Reverting password change...")
            # Login with new password
            login_data["password"] = "newadmin123"
            response = requests.post(f"{BASE_URL}/api/auth/login", json=login_data)
            if response.status_code == 200:
                new_token = response.json()['token']
                headers = {"Authorization": f"Bearer {new_token}"}
                # Change back to original
                change_pass_data = {
                    "old_password": "newadmin123",
                    "new_password": "admin123"
                }
                requests.post(f"{BASE_URL}/api/auth/change-password", 
                            json=change_pass_data, headers=headers)
                print("✅ Password reverted to original")
    
    # Test 7: Login with user role
    print("\n7️⃣  Testing Login (Regular User)...")
    login_data = {
        "username": "user",
        "password": "user123"
    }
    response = requests.post(f"{BASE_URL}/api/auth/login", json=login_data)
    print_response("LOGIN USER", response)
    
    if response.status_code == 200:
        user_token = response.json()['token']
        headers = {"Authorization": f"Bearer {user_token}"}
        
        # Test 8: Try to access admin endpoint (should fail)
        print("\n8️⃣  Testing Access Control (User accessing Admin endpoint)...")
        response = requests.get(f"{BASE_URL}/api/users", headers=headers)
        print_response("UNAUTHORIZED ACCESS ATTEMPT", response)
        
        # Test 9: Access allowed endpoint
        print("\n9️⃣  Testing User Access to Allowed Endpoint...")
        response = requests.get(f"{BASE_URL}/api/klaim", headers=headers)
        print_response("USER ACCESS KLAIM", response)
    
    # Test 10: Login with auditor
    print("\n🔟 Testing Login (Auditor)...")
    login_data = {
        "username": "auditor",
        "password": "auditor123"
    }
    response = requests.post(f"{BASE_URL}/api/auth/login", json=login_data)
    print_response("LOGIN AUDITOR", response)
    
    if response.status_code == 200:
        auditor_token = response.json()['token']
        headers = {"Authorization": f"Bearer {auditor_token}"}
        
        # Test 11: Access alerts endpoint
        print("\n1️⃣1️⃣  Testing Auditor Access to Alerts...")
        response = requests.get(f"{BASE_URL}/api/alerts", headers=headers)
        print_response("AUDITOR ACCESS ALERTS", response)
    
    # Test 12: Access without token (should fail)
    print("\n1️⃣2️⃣  Testing Access Without Token...")
    response = requests.get(f"{BASE_URL}/api/dashboard/overview")
    print_response("NO TOKEN ACCESS", response)
    
    # Test 13: Invalid credentials
    print("\n1️⃣3️⃣  Testing Invalid Login Credentials...")
    login_data = {
        "username": "admin",
        "password": "wrongpassword"
    }
    response = requests.post(f"{BASE_URL}/api/auth/login", json=login_data)
    print_response("INVALID CREDENTIALS", response)
    
    # Test 14: Invalid token
    print("\n1️⃣4️⃣  Testing Invalid Token...")
    headers = {"Authorization": "Bearer invalid_token_here"}
    response = requests.get(f"{BASE_URL}/api/dashboard/overview", headers=headers)
    print_response("INVALID TOKEN", response)
    
    print("\n" + "="*60)
    print("🎉 Authentication Testing Complete!")
    print("="*60)

if __name__ == "__main__":
    try:
        # Test if server is running
        response = requests.get(f"{BASE_URL}/")
        if response.status_code == 200:
            print(f"✅ Server is running: {response.json()}")
            test_authentication()
        else:
            print("❌ Server returned unexpected response")
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to server. Make sure Flask server is running on http://localhost:5000")
        print("   Run: python app.py")

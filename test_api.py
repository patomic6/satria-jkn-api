import requests
import json

# Base URL
BASE_URL = "http://localhost:5000"

# Create a session (no token hardcoded)
session = requests.Session()
session.headers.update({
    "Content-Type": "application/json",
    "Accept": "application/json",
})

def _safe_json(resp):
    try:
        return resp.json()
    except Exception:
        return resp.text

def print_response(name, response):
    content = _safe_json(response)
    try:
        pretty = json.dumps(content, indent=2)
    except Exception:
        pretty = str(content)
    print(f"   {name} -> Status: {response.status_code}")
    print(f"   Response: {pretty}\n")

def test_api():
    print("🚀 Testing SATRIA JKN REST API\n")
    
    # Test 1: Root endpoint
    print("1️⃣ Testing root endpoint...")
    response = session.get(f"{BASE_URL}/")
    print_response("ROOT", response)
    
    # Test 2: Login (Admin) — use auth to obtain token instead of hardcoded TOKEN
    print("\n2️⃣  Testing Login (Admin)...")
    login_data = {
        "username": "admin",
        "password": "admin123"
    }
    response = session.post(f"{BASE_URL}/api/auth/login", json=login_data)
    print_response("LOGIN ADMIN", response)

    # If login returned a token, set Authorization header for the session
    try:
        body = response.json()
        token = None
        # common token keys
        for key in ("access_token", "token", "jwt"):
            if key in body:
                token = body[key]
                break
        # sometimes token is nested
        if not token:
            if isinstance(body, dict):
                # try common nested structures
                token = body.get("data", {}).get("access_token") or body.get("data", {}).get("token")
        if token:
            session.headers.update({"Authorization": f"Bearer {token}"})
            print("   Authorization header set from login response.\n")
        else:
            print("   No token found in login response; proceeding without Authorization header.\n")
    except Exception:
        print("   Could not parse login response; proceeding without Authorization header.\n")

    # Test 3: Dashboard Overview
    print("3️⃣ Testing dashboard overview...")
    response = session.get(f"{BASE_URL}/api/dashboard/overview")
    print_response("DASHBOARD OVERVIEW", response)
    
    # Test 4: Get All Claims
    print("4️⃣ Testing get all claims...")
    response = session.get(f"{BASE_URL}/api/klaim")
    all_claims = _safe_json(response)
    print_response("GET ALL CLAIMS", response)
    print(f"   Found {len(all_claims) if isinstance(all_claims, list) else 'N/A'} claims\n")
    
    # Test 5: Create New Claim
    print("5️⃣ Testing create new claim...")
    new_claim = {
        "nomor_klaim": "TEST-001",
        "total_biaya": 2000000,
        "status": "Pending",
        "provider": "Test Hospital"
    }
    response = session.post(f"{BASE_URL}/api/klaim", json=new_claim)
    print_response("CREATE CLAIM", response)
    
    # Test 6: Get Alerts
    print("6️⃣ Testing get alerts...")
    response = session.get(f"{BASE_URL}/api/alerts")
    alerts = _safe_json(response)
    print_response("GET ALERTS", response)
    print(f"   Found {len(alerts) if isinstance(alerts, list) else 'N/A'} alerts\n")
    
    # Test 7: Get High Risk Alerts
    print("7️⃣ Testing get high risk alerts...")
    response = session.get(f"{BASE_URL}/api/alerts?risk_level=High")
    high_alerts = _safe_json(response)
    print_response("HIGH RISK ALERTS", response)
    print(f"   Found {len(high_alerts) if isinstance(high_alerts, list) else 'N/A'} high risk alerts\n")
    
    # Test 8: Get Alerts Summary
    print("8️⃣ Testing alerts summary...")
    response = session.get(f"{BASE_URL}/api/alerts/summary")
    print_response("ALERTS SUMMARY", response)
    
    # Test 9: Get Audit Trail
    print("9️⃣ Testing audit trail...")
    response = session.get(f"{BASE_URL}/api/audit-trail")
    audit = _safe_json(response)
    print_response("AUDIT TRAIL", response)
    print(f"   Found {len(audit) if isinstance(audit, list) else 'N/A'} audit logs\n")
    
    # Test 10: Get Reports
    print("🔟 Testing reports...")
    response = session.get(f"{BASE_URL}/api/reports")
    reports = _safe_json(response)
    print_response("REPORTS", response)
    print(f"   Found {len(reports) if isinstance(reports, list) else 'N/A'} reports\n")
    
    # Test 11: Get Settings
    print("1️⃣1️⃣ Testing settings...")
    response = session.get(f"{BASE_URL}/api/settings")
    print_response("SETTINGS", response)
    
    # Test 12: Search Claims
    print("1️⃣2️⃣ Testing search claims...")
    response = session.get(f"{BASE_URL}/api/klaim/search?q=CL001")
    search_results = _safe_json(response)
    print_response("SEARCH CLAIMS", response)
    print(f"   Found {len(search_results) if isinstance(search_results, list) else 'N/A'} matching claims\n")
    
    # Test 13: Get Anomaly Chart
    print("1️⃣3️⃣ Testing anomaly chart data...")
    response = session.get(f"{BASE_URL}/api/klaim/anomaly-chart")
    print_response("ANOMALY CHART", response)
    
    print("✅ All tests completed!")

if __name__ == "__main__":
    try:
        test_api()
    except requests.exceptions.ConnectionError:
        print("❌ Error: Cannot connect to API. Make sure the server is running on http://localhost:5000")
    except Exception as e:
        print(f"❌ Error: {str(e)}")

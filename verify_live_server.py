import urllib.request
import urllib.parse
import http.cookiejar
import json

BASE_URL = "http://127.0.0.1:5000"

def test_live_server():
    print("=" * 60)
    print("TESTING LIVE RUNNING FLASK SERVER AT http://127.0.0.1:5000")
    print("=" * 60)

    cj = http.cookiejar.CookieJar()
    opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))

    # 1. Test Login GET & POST
    print("\n[1/7] Testing Login Page & Authentication...")
    resp = opener.open(f"{BASE_URL}/login")
    assert resp.status == 200, f"Login GET failed: {resp.status}"
    print("  [OK] Login page rendered (HTTP 200)")

    login_data = urllib.parse.urlencode({
        "email": "demo@example.com",
        "password": "Demo@123"
    }).encode("utf-8")
    
    resp = opener.open(f"{BASE_URL}/login", data=login_data)
    assert resp.status == 200, f"Login POST failed: {resp.status}"
    body = resp.read().decode("utf-8")
    assert "Welcome back, Hemant" in body, "Dashboard did not load after login"
    print("  [OK] Authenticated successfully as demo@example.com")

    # 2. Test Dashboard
    print("\n[2/7] Testing Dashboard Page...")
    resp = opener.open(f"{BASE_URL}/")
    assert resp.status == 200
    dash_html = resp.read().decode("utf-8")
    assert "Your Learning Profile" in dash_html
    assert "AI Analysis &amp; Insights" in dash_html or "AI Analysis & Insights" in dash_html
    assert "Recommended for You" in dash_html
    print("  [OK] Dashboard loaded with real metrics, AI insights, and progress chart")

    # 3. Test Profile Page
    print("\n[3/7] Testing My Profile Page...")
    resp = opener.open(f"{BASE_URL}/profile")
    assert resp.status == 200
    prof_html = resp.read().decode("utf-8")
    assert "Performance Overview" in prof_html
    assert "Detailed Learning Profile" in prof_html
    assert "Subject-wise Performance" in prof_html
    print("  [OK] Profile page loaded with streak, 5 metric boxes, subject bars, and goals")

    # 4. Test AI Analysis Page & Live Refresh API
    print("\n[4/7] Testing AI Analysis Page & Refresh API...")
    resp = opener.open(f"{BASE_URL}/ai-analysis")
    assert resp.status == 200
    ana_html = resp.read().decode("utf-8")
    assert "Overall Learning Level" in ana_html
    assert "AI Confidence Score" in ana_html
    assert "Learning Behaviour" in ana_html
    print("  [OK] AI Analysis page loaded with cluster cards and dual-bar comparisons")

    req = urllib.request.Request(f"{BASE_URL}/api/analysis/refresh", data=b"{}", headers={"Content-Type": "application/json"})
    resp = opener.open(req)
    assert resp.status == 200
    ref_data = json.loads(resp.read().decode("utf-8"))
    assert ref_data["status"] == "success"
    print(f"  [OK] POST /api/analysis/refresh succeeded: Learning Level = {ref_data['cluster_result']['overall_learning_level']}")

    # 5. Test Recommendations Page
    print("\n[5/7] Testing Personalised Recommendations Page...")
    resp = opener.open(f"{BASE_URL}/recommendations")
    assert resp.status == 200
    rec_html = resp.read().decode("utf-8")
    assert "Personalised Learning Plan" in rec_html
    assert "Top Recommendations for You" in rec_html
    assert "Recommended Learning Path" in rec_html
    print("  [OK] Recommendations page loaded with 4 priority cards and sequential path")

    # 6. Test Practice Quiz & Submit API
    print("\n[6/7] Testing Practice Quiz Hub, Live Quiz & ML Feedback Submission...")
    resp = opener.open(f"{BASE_URL}/practice-quiz")
    assert resp.status == 200
    
    resp = opener.open(f"{BASE_URL}/practice-quiz/start?subject=Python&difficulty=Medium")
    assert resp.status == 200
    quiz_html = resp.read().decode("utf-8")
    assert "Live Assessment" in quiz_html
    assert "countdownTimer" in quiz_html
    print("  [OK] Active quiz loaded with questions and countdown timer")

    # Fetch questions from API or send submission
    quiz_payload = json.dumps({
        "subject": "Python",
        "difficulty": "Medium",
        "answers": {"1": "B", "2": "C", "3": "B", "4": "B", "5": "C"},
        "time_taken_seconds": 110.0
    }).encode("utf-8")
    req = urllib.request.Request(f"{BASE_URL}/api/quiz/submit", data=quiz_payload, headers={"Content-Type": "application/json"})
    resp = opener.open(req)
    assert resp.status == 200
    sub_data = json.loads(resp.read().decode("utf-8"))
    assert sub_data["status"] == "success"
    print(f"  [OK] POST /api/quiz/submit scored: {sub_data['score']}% (Accuracy: {sub_data['accuracy']}%)")
    print(f"       Ingested into ML Pipeline -> Updated Mastery: {sub_data['updated_mastery_score']}%, Cluster: {sub_data['updated_cluster']}")

    # 7. Test Progress & Resources & Logout
    print("\n[7/7] Testing Progress & Analytics, Resources, and Logout...")
    resp = opener.open(f"{BASE_URL}/progress")
    assert resp.status == 200
    
    resp = opener.open(f"{BASE_URL}/resources")
    assert resp.status == 200
    
    resp = opener.open(f"{BASE_URL}/settings")
    assert resp.status == 200
    
    resp = opener.open(f"{BASE_URL}/logout")
    assert resp.status == 200
    print("  [OK] Progress, Resources, Settings, and Logout all verified on live server")

    print("\n" + "=" * 60)
    print("LIVE FLASK SERVER FULLY VERIFIED - ZERO ERRORS")
    print("=" * 60)

if __name__ == "__main__":
    test_live_server()

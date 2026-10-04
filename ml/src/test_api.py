"""
test_api.py
===========
Day 19/20 - Comprehensive API Tests (Postman-equivalent)
Tests both /predict and /predict/from-app endpoints.
"""
import json
import sys
import requests

BASE = "http://127.0.0.1:8000"
results = []

def test(name, method, url, payload=None, expected_status=200, check_fn=None):
    try:
        if method == "POST":
            resp = requests.post(url, json=payload, timeout=30)
        else:
            resp = requests.get(url, timeout=30)
        
        passed = resp.status_code == expected_status
        detail = ""
        body = None
        try:
            body = resp.json()
        except:
            body = resp.text
            
        if check_fn and passed and body:
            try:
                check_fn(body)
            except AssertionError as ae:
                passed = False
                detail = str(ae)
                
        status = "PASS" if passed else "FAIL"
        results.append({"test": name, "status": status, "http_status": resp.status_code, "detail": detail})
        print(f"  [{status}] {name} (HTTP {resp.status_code}){' - ' + detail if detail else ''}")
        return body
    except requests.exceptions.ConnectionError:
        results.append({"test": name, "status": "FAIL", "http_status": None, "detail": "Connection refused"})
        print(f"  [FAIL] {name} - Connection refused")
        return None

print("=" * 70)
print("NutriWise ML API - Comprehensive Test Suite")
print("=" * 70)

# ── Test 1: Health check ──────────────────────────────────────────────────────
print("\n--- Test 1: Server Health ---")
test("OpenAPI docs accessible", "GET", f"{BASE}/docs", expected_status=200)

# ── Test 2: Valid /predict request ────────────────────────────────────────────
print("\n--- Test 2: POST /predict (valid, all deficiencies) ---")
payload_valid = {
    "age": 35, "gender": 0, "bmi": 24.5, "is_pregnant": 0, "is_smoker": 0,
    "activity_level": 1, "dietary_preference": 2,
    "dietary_iron_mg": 5.0, "dietary_calcium_mg": 500, "dietary_vitamin_d_mcg": 2.0,
    "dietary_vitamin_b12_mcg": 0.5, "dietary_folate_mcg": 200, "dietary_vitamin_c_mg": 40,
    "dietary_protein_g": 45, "dietary_calories_kcal": 1500, "dietary_fiber_g": 10,
    "symptom_fatigue": 1, "symptom_hair_loss": 0, "symptom_skin_issues": 0,
    "symptom_muscle_weakness": 0, "symptom_mood_low": 1, "symptom_bone_pain": 0,
    "symptom_tingling": 1, "symptom_cold_intolerance": 1,
}

def check_full_predict(body):
    assert body["status"] == "success", f"Expected success, got {body['status']}"
    for d in ["iron", "vitamin_d", "vitamin_b12", "calcium", "folate"]:
        assert d in body["data"], f"Missing deficiency: {d}"
        assert body["data"][d]["status"] == "success"
        assert body["data"][d]["risk_probability"] is not None
        assert body["data"][d]["risk_level"] in ["Low", "Moderate", "High"]
        assert "contributors" in body["data"][d]
        assert "disclaimer" in body["data"][d]

body = test("Full prediction (5 deficiencies)", "POST", f"{BASE}/predict", payload_valid, check_fn=check_full_predict)
if body:
    for d in ["iron", "vitamin_d", "vitamin_b12", "calcium", "folate"]:
        p = body["data"][d]["risk_probability"]
        l = body["data"][d]["risk_level"]
        print(f"    {d}: prob={p}, level={l}")

# ── Test 3: Selective targets ─────────────────────────────────────────────────
print("\n--- Test 3: POST /predict (selective targets) ---")
payload_selective = {**payload_valid, "requested_targets": ["iron", "vitamin_b12"]}

def check_selective(body):
    assert len(body["data"]) == 2, f"Expected 2 results, got {len(body['data'])}"
    assert "iron" in body["data"]
    assert "vitamin_b12" in body["data"]

test("Selective targets (iron, B12)", "POST", f"{BASE}/predict", payload_selective, check_fn=check_selective)

# ── Test 4: Unsupported deficiency ────────────────────────────────────────────
print("\n--- Test 4: POST /predict (unsupported deficiency) ---")
payload_unsupported = {**payload_valid, "requested_targets": ["iron", "zinc"]}

def check_unsupported(body):
    assert body["data"]["zinc"]["status"] == "unsupported"
    assert body["data"]["iron"]["status"] == "success"

test("Unsupported target (zinc)", "POST", f"{BASE}/predict", payload_unsupported, check_fn=check_unsupported)

# ── Test 5: Validation error (age out of range) ──────────────────────────────
print("\n--- Test 5: Validation errors ---")
payload_bad_age = {**payload_valid, "age": 5}
test("Age below 18", "POST", f"{BASE}/predict", payload_bad_age, expected_status=422)

payload_bad_bmi = {**payload_valid, "bmi": -1}
test("Negative BMI", "POST", f"{BASE}/predict", payload_bad_bmi, expected_status=422)

# ── Test 6: /predict/from-app (integration endpoint) ─────────────────────────
print("\n--- Test 6: POST /predict/from-app (Milestone 1 integration) ---")
integration_payload = {
    "health_profile": {
        "age": 28, "gender": "female",
        "height_cm": 165, "weight_kg": 58,
        "activity_level": "light", "dietary_preference": "vegan"
    },
    "food_diary_entries": [
        {"food_name": "Oatmeal", "calories": 300, "protein_g": 10, "fiber_g": 8,
         "vitamin_c_mg": 0, "calcium_mg": 100, "iron_mg": 3},
        {"food_name": "Lentil Soup", "calories": 350, "protein_g": 18, "fiber_g": 12,
         "vitamin_c_mg": 10, "calcium_mg": 50, "iron_mg": 4},
    ],
    "symptoms": [
        {"symptom_name": "fatigue", "severity": "moderate"},
        {"symptom_name": "tingling", "severity": "mild"},
    ],
    "requested_targets": ["iron", "vitamin_b12", "vitamin_d"]
}

def check_integration(body):
    assert body["status"] == "success"
    assert "data_gaps" in body, "data_gaps missing from response"
    assert "field_mapping" in body, "field_mapping missing from response"
    assert body["data"]["iron"]["status"] == "success"
    assert body["data"]["vitamin_b12"]["status"] == "success"

body2 = test("Integration endpoint", "POST", f"{BASE}/predict/from-app", integration_payload, check_fn=check_integration)
if body2:
    print(f"    Data gaps reported: {len(body2.get('data_gaps', []))}")
    for g in body2.get("data_gaps", []):
        print(f"      - {g}")

# ── Test 7: /predict/from-app with empty diary ───────────────────────────────
print("\n--- Test 7: POST /predict/from-app (empty diary) ---")
empty_diary_payload = {
    "health_profile": {"age": 50, "gender": "male"},
    "food_diary_entries": [],
    "symptoms": [],
}

def check_empty_diary(body):
    assert body["status"] == "success"
    # All dietary values should be 0.0 but model should still return valid predictions
    for d in ["iron", "vitamin_d", "vitamin_b12", "calcium", "folate"]:
        assert body["data"][d]["status"] == "success"

test("Empty diary + no symptoms", "POST", f"{BASE}/predict/from-app", empty_diary_payload, check_fn=check_empty_diary)

# ── Summary ───────────────────────────────────────────────────────────────────
print("\n" + "=" * 70)
print("TEST SUMMARY")
print("=" * 70)
passed = sum(1 for r in results if r["status"] == "PASS")
failed = sum(1 for r in results if r["status"] == "FAIL")
print(f"Total: {len(results)} | Passed: {passed} | Failed: {failed}")
for r in results:
    status_icon = "+" if r["status"] == "PASS" else "X"
    print(f"  [{status_icon}] {r['test']}")

# Save results as JSON for documentation
import pathlib
report_dir = pathlib.Path(__file__).parent.parent / "reports"
with open(report_dir / "api_test_results.json", "w") as f:
    json.dump(results, f, indent=2)
print(f"\nTest results saved to: {report_dir / 'api_test_results.json'}")

sys.exit(0 if failed == 0 else 1)

import requests
import sys

# Ensure UTF-8 output
sys.stdout.reconfigure(encoding='utf-8')

BASE_URL = "http://127.0.0.1:8000/api"

def print_header(title):
    print(f"\n{'='*60}\n{title}\n{'='*60}")

def print_result(msg, is_success):
    print(f"   {'✅' if is_success else '❌'} {msg}")
    if not is_success:
        sys.exit(1)

def print_info(msg):
    print(f"   ℹ️  {msg}")

def main():
    print_header("WEEK 2 FULL SYSTEM VERIFICATION")

    # 1. Registration & Auth
    user_a = {"email": "usera@example.com", "username": "usera", "password": "password123", "name": "User A"}
    user_b = {"email": "userb@example.com", "username": "userb", "password": "password123", "name": "User B"}

    for user in [user_a, user_b]:
        r = requests.post(f"{BASE_URL}/auth/register", json=user)
        if r.status_code == 201:
            print_info(f"Registered {user['name']}")
        elif r.status_code == 409:
            print_info(f"{user['name']} already exists")
        else:
            print_result(f"Failed to register {user['name']}: {r.text}", False)

    # Login User A
    r = requests.post(f"{BASE_URL}/auth/login", json={"email": user_a["email"], "password": user_a["password"]})
    if r.status_code == 200:
        token_a = r.json()["access_token"]
        auth_a = {"Authorization": f"Bearer {token_a}"}
        print_result("User A authenticated", True)
    else:
        print_result("User A login failed", False)

    # Login User B
    r = requests.post(f"{BASE_URL}/auth/login", json={"email": user_b["email"], "password": user_b["password"]})
    if r.status_code == 200:
        token_b = r.json()["access_token"]
        auth_b = {"Authorization": f"Bearer {token_b}"}
        print_result("User B authenticated", True)
    else:
        print_result("User B login failed", False)

    print_header("TESTING HEALTH PROFILE")
    # Health Profile User A
    r = requests.get(f"{BASE_URL}/health-profile/", headers=auth_a)
    if r.status_code == 404:
        r = requests.post(f"{BASE_URL}/health-profile/", headers=auth_a, json={
            "date_of_birth": "1990-01-01", "gender": "male", "height_cm": 180, "weight_kg": 75, "activity_level": "active"
        })
        print_result("Created User A Health Profile", r.status_code == 201)
    else:
        r = requests.put(f"{BASE_URL}/health-profile/", headers=auth_a, json={"weight_kg": 76})
        print_result("Updated User A Health Profile", r.status_code == 200)

    print_header("TESTING FOOD DIARY")
    # Food Diary User A
    r = requests.post(f"{BASE_URL}/food-diary/", headers=auth_a, json={
        "food_name": "Test Apple", "quantity_g": 100, "meal_type": "snack"
    })
    print_result("Created Food Diary Entry for User A", r.status_code == 201)
    entry_id = r.json()["id"]

    r = requests.get(f"{BASE_URL}/food-diary/{entry_id}", headers=auth_a)
    print_result("Fetched Food Diary Entry for User A", r.status_code == 200)

    r = requests.put(f"{BASE_URL}/food-diary/{entry_id}", headers=auth_a, json={"quantity_g": 200})
    print_result("Updated Food Diary Entry for User A", r.status_code == 200)

    print_header("TESTING NUTRITION API")
    r = requests.get(f"{BASE_URL}/nutrition/search?query=banana", headers=auth_a)
    print_result("Searched Nutrition Database", r.status_code == 200 and len(r.json()) > 0)

    print_header("TESTING SYMPTOMS (STEP 11)")
    # Create Symptom User A
    r = requests.post(f"{BASE_URL}/symptoms/", headers=auth_a, json={
        "symptom_name": "Headache", "severity": "moderate", "symptom_date": "2026-09-27"
    })
    print_result("Created Symptom for User A", r.status_code == 201)
    symptom_id = r.json()["id"]

    # Invalid Severity
    r = requests.post(f"{BASE_URL}/symptoms/", headers=auth_a, json={
        "symptom_name": "Nausea", "severity": "extreme", "symptom_date": "2026-09-27"
    })
    print_result("Rejected invalid symptom severity", r.status_code == 422)

    # Get Symptoms
    r = requests.get(f"{BASE_URL}/symptoms/", headers=auth_a)
    print_result("Fetched Symptoms for User A", r.status_code == 200 and len(r.json()) > 0)

    # Update Symptom
    r = requests.put(f"{BASE_URL}/symptoms/{symptom_id}", headers=auth_a, json={"severity": "mild"})
    print_result("Updated Symptom for User A", r.status_code == 200)

    print_header("TESTING BLOOD TESTS (STEP 11)")
    # Create Lab Result User A
    r = requests.post(f"{BASE_URL}/lab-results/", headers=auth_a, json={
        "test_name": "Hemoglobin", "result_value": 14.5, "unit": "g/dL", "test_date": "2026-09-27"
    })
    print_result("Created Lab Result for User A", r.status_code == 201)
    lab_id = r.json()["id"]

    # Get Lab Results
    r = requests.get(f"{BASE_URL}/lab-results/", headers=auth_a)
    print_result("Fetched Lab Results for User A", r.status_code == 200 and len(r.json()) > 0)

    # Update Lab Result
    r = requests.put(f"{BASE_URL}/lab-results/{lab_id}", headers=auth_a, json={"notes": "Fasting"})
    print_result("Updated Lab Result for User A", r.status_code == 200)

    print_header("TESTING CLINICAL QUESTIONNAIRE & ESSENTIAL BIOMARKERS")
    # Verify the 5 key symptoms can be saved
    key_symptoms = ["Fatigue", "Hair loss", "Skin conditions", "Muscle weakness", "Mood-related symptoms"]
    for s_name in key_symptoms:
        r = requests.post(f"{BASE_URL}/symptoms/", headers=auth_a, json={
            "symptom_name": s_name, "severity": "moderate", "symptom_date": "2026-09-27"
        })
        print_result(f"Logged clinical symptom '{s_name}'", r.status_code == 201)

    # Verify the 5 essential blood biomarkers can be saved
    key_biomarkers = [
        ("Hemoglobin", 14.2, "g/dL"),
        ("Vitamin D", 42.0, "ng/mL"),
        ("Vitamin B12", 450.0, "pg/mL"),
        ("Iron", 95.0, "mcg/dL"),
        ("Calcium", 9.4, "mg/dL"),
    ]
    for b_name, val, unit in key_biomarkers:
        r = requests.post(f"{BASE_URL}/lab-results/", headers=auth_a, json={
            "test_name": b_name, "result_value": val, "unit": unit, "test_date": "2026-09-27"
        })
        print_result(f"Logged clinical biomarker '{b_name}'", r.status_code == 201)

    print_header("CROSS-USER SECURITY TEST (USER B -> USER A)")
    # User B tries to read User A's data
    r = requests.get(f"{BASE_URL}/health-profile/", headers=auth_b)
    print_result("User B cannot read User A's Health Profile", r.status_code == 404)

    r = requests.get(f"{BASE_URL}/food-diary/{entry_id}", headers=auth_b)
    print_result("User B cannot read User A's Food Diary Entry", r.status_code == 404)

    r = requests.put(f"{BASE_URL}/symptoms/{symptom_id}", headers=auth_b, json={"severity": "severe"})
    print_result("User B cannot update User A's Symptom", r.status_code == 404)

    r = requests.delete(f"{BASE_URL}/lab-results/{lab_id}", headers=auth_b)
    print_result("User B cannot delete User A's Lab Result", r.status_code == 404)

    print_header("TESTS COMPLETE ✅")

if __name__ == "__main__":
    main()

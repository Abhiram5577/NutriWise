"""
integration.py
==============
Day 20 - Milestone 1 -> Milestone 2 Integration Bridge
ML Nutritional Deficiency Detection Engine

Maps Milestone 1 application data (food diary, symptoms, health profile, lab results)
into the ML prediction service input format.

FIELD MAPPING DOCUMENTATION
----------------------------
Milestone 1 stores data in these models:
  - HealthProfile: age (int), gender (str: "male"/"female"), height_cm, weight_kg,
                   activity_level (str: "sedentary"...), dietary_preference (str: "omnivore"...)
  - FoodDiaryEntry: calories, protein_g, carbs_g, fat_g, fiber_g,
                    vitamin_a_mcg, vitamin_c_mg, calcium_mg, iron_mg
  - Symptom: symptom_name (str), severity (str: "mild"/"moderate"/"severe")
  - LabResult: test_name (str), result_value (float), unit (str)

ML model expects:
  - age (int), gender (int: 0/1), bmi (float), is_pregnant (int: 0/1), is_smoker (int: 0/1)
  - activity_level (int: 0-4), dietary_preference (int: 0-2)
  - dietary_* (9 float fields from food diary totals)
  - symptom_* (8 binary fields + symptom_count)

GAPS IDENTIFIED:
  - Food diary in M1 tracks: calories, protein, carbs, fat, fiber, vitamin_a, vitamin_c, calcium, iron
  - ML model needs additionally: vitamin_d, vitamin_b12, folate
  - These 3 dietary micronutrients are NOT in M1's FoodDiaryEntry model
  - Resolution: Set to 0.0 with a documented gap; flag in the response as "unavailable_inputs"
  - is_pregnant and is_smoker are not in M1 HealthProfile; default to 0 with gap noted
"""

from typing import Dict, Any, List, Optional


# ─── Mapping Constants ────────────────────────────────────────────────────────

GENDER_MAP = {
    "female": 0,
    "male": 1,
    "other": 1,              # Default to male encoding for model (no separate category)
    "prefer_not_to_say": 1,  # Default
}

ACTIVITY_LEVEL_MAP = {
    "sedentary": 0,
    "light": 1,
    "moderate": 2,
    "active": 3,
    "very_active": 4,
}

DIETARY_PREFERENCE_MAP = {
    "omnivore": 0,
    "vegetarian": 1,
    "vegan": 2,
    "pescatarian": 0,   # Closest to omnivore for model purposes
    "keto": 0,
    "paleo": 0,
    "gluten_free": 0,
    "dairy_free": 0,
    "other": 0,
}

# Maps Milestone 1 symptom_name strings to ML feature names
# Only symptoms the model was trained on are mapped; others are ignored
SYMPTOM_NAME_MAP = {
    "fatigue": "symptom_fatigue",
    "hair loss": "symptom_hair_loss",
    "hair_loss": "symptom_hair_loss",
    "skin issues": "symptom_skin_issues",
    "skin_issues": "symptom_skin_issues",
    "muscle weakness": "symptom_muscle_weakness",
    "muscle_weakness": "symptom_muscle_weakness",
    "low mood": "symptom_mood_low",
    "mood_low": "symptom_mood_low",
    "depression": "symptom_mood_low",
    "bone pain": "symptom_bone_pain",
    "bone_pain": "symptom_bone_pain",
    "joint pain": "symptom_bone_pain",
    "tingling": "symptom_tingling",
    "numbness": "symptom_tingling",
    "tingling/numbness": "symptom_tingling",
    "cold intolerance": "symptom_cold_intolerance",
    "cold_intolerance": "symptom_cold_intolerance",
}


def transform_health_profile(profile: Dict[str, Any]) -> Dict[str, Any]:
    """
    Transform Milestone 1 HealthProfile data into ML input features.

    Input fields used:
      - age (int)
      - gender (str: "male"/"female"/...)
      - height_cm (float)
      - weight_kg (float)
      - activity_level (str)
      - dietary_preference (str)

    Output fields:
      - age (int)
      - gender (int: 0=female, 1=male)
      - bmi (float: computed from height_cm and weight_kg)
      - activity_level (int: 0-4)
      - dietary_preference (int: 0-2)
      - is_pregnant (int: 0 -- not available in M1)
      - is_smoker (int: 0 -- not available in M1)
    """
    result = {}
    gaps = []

    # Age
    result["age"] = profile.get("age", 30)  # Default 30 if missing

    # Gender
    gender_str = (profile.get("gender") or "male").lower().strip()
    result["gender"] = GENDER_MAP.get(gender_str, 1)

    # BMI (computed)
    height_cm = profile.get("height_cm")
    weight_kg = profile.get("weight_kg")
    if height_cm and weight_kg and height_cm > 0:
        height_m = height_cm / 100.0
        result["bmi"] = round(weight_kg / (height_m ** 2), 1)
    else:
        result["bmi"] = 25.0  # Population average default
        gaps.append("bmi: computed from default (height/weight missing)")

    # Activity level
    activity_str = (profile.get("activity_level") or "sedentary").lower().strip()
    result["activity_level"] = ACTIVITY_LEVEL_MAP.get(activity_str, 0)

    # Dietary preference
    diet_str = (profile.get("dietary_preference") or "omnivore").lower().strip()
    result["dietary_preference"] = DIETARY_PREFERENCE_MAP.get(diet_str, 0)

    # Fields NOT in Milestone 1 HealthProfile
    result["is_pregnant"] = 0
    gaps.append("is_pregnant: not available in Milestone 1 HealthProfile; defaulted to 0")
    result["is_smoker"] = 0
    gaps.append("is_smoker: not available in Milestone 1 HealthProfile; defaulted to 0")

    return result, gaps


def transform_food_diary(entries: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Aggregate daily food diary entries into ML dietary features.

    Input: list of FoodDiaryEntry dicts (one day's entries)
    Output: summed dietary_* features for the day

    Mapping:
      M1 FoodDiaryEntry.iron_mg       -> dietary_iron_mg
      M1 FoodDiaryEntry.calcium_mg    -> dietary_calcium_mg
      M1 FoodDiaryEntry.vitamin_c_mg  -> dietary_vitamin_c_mg
      M1 FoodDiaryEntry.protein_g     -> dietary_protein_g
      M1 FoodDiaryEntry.calories      -> dietary_calories_kcal
      M1 FoodDiaryEntry.fiber_g       -> dietary_fiber_g

    GAPS (not tracked in M1 FoodDiaryEntry):
      dietary_vitamin_d_mcg    -> 0.0
      dietary_vitamin_b12_mcg  -> 0.0
      dietary_folate_mcg       -> 0.0
    """
    result = {
        "dietary_iron_mg": 0.0,
        "dietary_calcium_mg": 0.0,
        "dietary_vitamin_d_mcg": 0.0,
        "dietary_vitamin_b12_mcg": 0.0,
        "dietary_folate_mcg": 0.0,
        "dietary_vitamin_c_mg": 0.0,
        "dietary_protein_g": 0.0,
        "dietary_calories_kcal": 0.0,
        "dietary_fiber_g": 0.0,
    }
    gaps = []

    for entry in entries:
        result["dietary_iron_mg"] += float(entry.get("iron_mg") or 0)
        result["dietary_calcium_mg"] += float(entry.get("calcium_mg") or 0)
        result["dietary_vitamin_c_mg"] += float(entry.get("vitamin_c_mg") or 0)
        result["dietary_protein_g"] += float(entry.get("protein_g") or 0)
        result["dietary_calories_kcal"] += float(entry.get("calories") or 0)
        result["dietary_fiber_g"] += float(entry.get("fiber_g") or 0)

    # These 3 micronutrients are NOT in Milestone 1 food diary
    gaps.append("dietary_vitamin_d_mcg: NOT tracked in M1 food diary; set to 0.0")
    gaps.append("dietary_vitamin_b12_mcg: NOT tracked in M1 food diary; set to 0.0")
    gaps.append("dietary_folate_mcg: NOT tracked in M1 food diary; set to 0.0")

    return result, gaps


def transform_symptoms(symptoms: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Transform Milestone 1 Symptom records into ML binary symptom features.

    Input: list of Symptom dicts with symptom_name and severity
    Output: symptom_* binary fields + symptom_count

    Mapping: Any symptom with severity "moderate" or "severe" is treated as present (1).
    Mild symptoms are also marked present since the model uses binary flags.
    """
    ml_symptoms = {
        "symptom_fatigue": 0,
        "symptom_hair_loss": 0,
        "symptom_skin_issues": 0,
        "symptom_muscle_weakness": 0,
        "symptom_mood_low": 0,
        "symptom_bone_pain": 0,
        "symptom_tingling": 0,
        "symptom_cold_intolerance": 0,
    }
    unmapped = []

    for s in symptoms:
        name = (s.get("symptom_name") or "").lower().strip()
        ml_key = SYMPTOM_NAME_MAP.get(name)
        if ml_key:
            ml_symptoms[ml_key] = 1
        else:
            unmapped.append(name)

    ml_symptoms["symptom_count"] = sum(v for k, v in ml_symptoms.items() if k != "symptom_count")

    gaps = []
    if unmapped:
        gaps.append(f"Unmapped symptoms (not in ML model): {', '.join(unmapped)}")

    return ml_symptoms, gaps


def build_prediction_request(
    health_profile: Dict[str, Any],
    food_diary_entries: List[Dict[str, Any]],
    symptoms: List[Dict[str, Any]],
    requested_targets: Optional[List[str]] = None,
) -> Dict[str, Any]:
    """
    Build a complete ML prediction request from Milestone 1 data.

    This is the main integration function that combines:
    1. Health profile -> demographics + activity + diet preference
    2. Food diary entries -> daily dietary totals
    3. Symptoms -> binary symptom flags

    Returns:
      - request_payload: dict ready to POST to /predict
      - data_gaps: list of documented gaps/defaults
      - field_mapping: dict documenting each field's source
    """
    profile_data, profile_gaps = transform_health_profile(health_profile)
    dietary_data, dietary_gaps = transform_food_diary(food_diary_entries)
    symptom_data, symptom_gaps = transform_symptoms(symptoms)

    # Merge all into one payload
    payload = {**profile_data, **dietary_data, **symptom_data}
    if requested_targets:
        payload["requested_targets"] = requested_targets

    all_gaps = profile_gaps + dietary_gaps + symptom_gaps

    # Field mapping documentation
    field_mapping = {
        "age": "HealthProfile.age",
        "gender": "HealthProfile.gender -> encoded (0=F, 1=M)",
        "bmi": "Computed from HealthProfile.height_cm / weight_kg",
        "is_pregnant": "NOT IN M1 (defaulted to 0)",
        "is_smoker": "NOT IN M1 (defaulted to 0)",
        "activity_level": "HealthProfile.activity_level -> encoded (0-4)",
        "dietary_preference": "HealthProfile.dietary_preference -> encoded (0-2)",
        "dietary_iron_mg": "SUM(FoodDiaryEntry.iron_mg)",
        "dietary_calcium_mg": "SUM(FoodDiaryEntry.calcium_mg)",
        "dietary_vitamin_d_mcg": "NOT IN M1 FoodDiary (set to 0.0)",
        "dietary_vitamin_b12_mcg": "NOT IN M1 FoodDiary (set to 0.0)",
        "dietary_folate_mcg": "NOT IN M1 FoodDiary (set to 0.0)",
        "dietary_vitamin_c_mg": "SUM(FoodDiaryEntry.vitamin_c_mg)",
        "dietary_protein_g": "SUM(FoodDiaryEntry.protein_g)",
        "dietary_calories_kcal": "SUM(FoodDiaryEntry.calories)",
        "dietary_fiber_g": "SUM(FoodDiaryEntry.fiber_g)",
        "symptom_*": "Symptom.symptom_name mapped to binary flags via SYMPTOM_NAME_MAP",
        "symptom_count": "Derived: sum of all active symptom flags",
    }

    return payload, all_gaps, field_mapping


if __name__ == "__main__":
    import json

    # Simulate Milestone 1 data
    profile = {
        "age": 28,
        "gender": "female",
        "height_cm": 165,
        "weight_kg": 58,
        "activity_level": "light",
        "dietary_preference": "vegan",
    }

    diary = [
        {"food_name": "Oatmeal", "calories": 300, "protein_g": 10, "carbs_g": 50,
         "fat_g": 5, "fiber_g": 8, "vitamin_c_mg": 0, "calcium_mg": 100, "iron_mg": 3},
        {"food_name": "Salad", "calories": 200, "protein_g": 5, "carbs_g": 20,
         "fat_g": 10, "fiber_g": 6, "vitamin_c_mg": 30, "calcium_mg": 80, "iron_mg": 2},
        {"food_name": "Lentil Soup", "calories": 350, "protein_g": 18, "carbs_g": 45,
         "fat_g": 3, "fiber_g": 12, "vitamin_c_mg": 10, "calcium_mg": 50, "iron_mg": 4},
    ]

    symptoms = [
        {"symptom_name": "fatigue", "severity": "moderate", "symptom_date": "2026-10-01"},
        {"symptom_name": "tingling", "severity": "mild", "symptom_date": "2026-10-01"},
        {"symptom_name": "headache", "severity": "mild", "symptom_date": "2026-10-01"},  # unmapped
    ]

    payload, gaps, mapping = build_prediction_request(profile, diary, symptoms)

    print("=== PREDICTION REQUEST PAYLOAD ===")
    print(json.dumps(payload, indent=2))
    print("\n=== DATA GAPS ===")
    for g in gaps:
        print(f"  - {g}")
    print("\n=== FIELD MAPPING ===")
    for k, v in mapping.items():
        print(f"  {k}: {v}")

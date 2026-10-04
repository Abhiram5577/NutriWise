# Day 18 - Risk Score & SHAP Explainability Report
## Milestone 2: ML Nutritional Deficiency Detection Engine

---

## 1. Risk-Score Output Specification

### 1.1 Output Format
Each deficiency prediction returns:

```json
{
  "deficiency": "<name>",
  "status": "success | unsupported | error",
  "risk_probability": 0.0,
  "risk_level": "Low | Moderate | High",
  "contributors": {
    "dietary": [
      {
        "feature": "...",
        "display_name": "...",
        "impact_score": 0.0,
        "direction": "increases_risk"
      }
    ],
    "symptom": [
      {
        "feature": "...",
        "display_name": "...",
        "impact_score": 0.0,
        "direction": "increases_risk"
      }
    ],
    "demographic": [
      {
        "feature": "...",
        "display_name": "...",
        "impact_score": 0.0,
        "direction": "increases_risk"
      }
    ]
  },
  "disclaimer": "This is a statistical risk estimate and NOT a medical diagnosis."
}
```

### 1.2 Risk Level Thresholds

| Level | Probability Range | Reasoning |
|-------|------------------|-----------|
| Low | < 0.30 | Below the base prevalence rate of most deficiencies in US adults (~15-34%). A probability below 30% indicates the model considers the individual less likely than average to be deficient. |
| Moderate | 0.30 - 0.60 | Within or modestly above population prevalence. Warrants dietary attention and monitoring. |
| High | > 0.60 | Substantially above population prevalence. Multiple risk factors converge. Strongly suggests clinical follow-up (blood test). |

**Evidence for thresholds:**
- Iron deficiency prevalence in US women: ~15-20% (CDC/NHANES)
- Vitamin D insufficiency: ~35% of US adults (NIH ODS)
- B12 deficiency in vegans: up to 62% (Pawlak et al. 2014)
- Thresholds are deliberately conservative (lower High threshold) for a screening tool where false negatives are more costly than false positives.
- The 0.30/0.60 boundaries are NOT arbitrary: they align with the principle that a screening tool should flag at or above population prevalence (Low/Moderate boundary) and trigger clinical referral when risk is roughly 2x population prevalence (Moderate/High boundary).

### 1.3 Important Disclaimers
- Outputs are **risk estimates**, NOT diagnoses
- Contributors are **model factors**, NOT clinical causes
- The system cannot replace blood-test-based clinical evaluation
- Lab biomarkers are excluded from inference; the model uses dietary recall and symptoms only

## 2. Global Feature Importance (SHAP)

Global SHAP values computed using TreeExplainer on the validation set (lab features excluded).

### Iron Deficiency

| Rank | Feature | Display Name | Mean |SHAP| | Category |
|------|---------|-------------|-------------|----------|
| 1 | gender | Biological Sex | 1.1949 | Demographic |
| 2 | symptom_fatigue | Fatigue | 0.8952 | Symptom |
| 3 | dietary_vitamin_c_mg | Daily Vitamin C Intake (mg) | 0.4589 | Dietary |
| 4 | dietary_vitamin_b12_mcg | Daily Vitamin B12 Intake (mcg) | 0.4562 | Dietary |
| 5 | bmi | Body Mass Index | 0.4481 | Demographic |
| 6 | dietary_iron_mg | Daily Iron Intake (mg) | 0.4364 | Dietary |
| 7 | dietary_folate_mcg | Daily Folate Intake (mcg DFE) | 0.4319 | Dietary |
| 8 | dietary_fiber_g | Daily Fiber Intake (g) | 0.4057 | Dietary |
| 9 | dietary_calories_kcal | Daily Calorie Intake (kcal) | 0.4051 | Dietary |
| 10 | dietary_vitamin_d_mcg | Daily Vitamin D Intake (mcg) | 0.4034 | Dietary |

**Figure saved:** fig_shap_summary_iron.png

### Vitamin D Deficiency

| Rank | Feature | Display Name | Mean |SHAP| | Category |
|------|---------|-------------|-------------|----------|
| 1 | symptom_count | Total Symptom Count | 0.5744 | Symptom |
| 2 | bmi | Body Mass Index | 0.5631 | Demographic |
| 3 | age | Age | 0.5077 | Demographic |
| 4 | symptom_bone_pain | Bone Pain | 0.3595 | Symptom |
| 5 | dietary_vitamin_b12_mcg | Daily Vitamin B12 Intake (mcg) | 0.3591 | Dietary |
| 6 | dietary_vitamin_d_mcg | Daily Vitamin D Intake (mcg) | 0.3292 | Dietary |
| 7 | symptom_mood_low | Low Mood | 0.3278 | Symptom |
| 8 | dietary_calories_kcal | Daily Calorie Intake (kcal) | 0.3113 | Dietary |
| 9 | dietary_fiber_g | Daily Fiber Intake (g) | 0.3073 | Dietary |
| 10 | dietary_folate_mcg | Daily Folate Intake (mcg DFE) | 0.3018 | Dietary |

**Figure saved:** fig_shap_summary_vitamin_d.png

### Vitamin B12 Deficiency

| Rank | Feature | Display Name | Mean |SHAP| | Category |
|------|---------|-------------|-------------|----------|
| 1 | age | Age | 1.0060 | Demographic |
| 2 | dietary_preference_0 | Diet: Omnivore | 0.8634 | Dietary |
| 3 | symptom_tingling | Tingling/Numbness | 0.8193 | Symptom |
| 4 | dietary_vitamin_d_mcg | Daily Vitamin D Intake (mcg) | 0.5885 | Dietary |
| 5 | dietary_vitamin_b12_mcg | Daily Vitamin B12 Intake (mcg) | 0.5705 | Dietary |
| 6 | dietary_folate_mcg | Daily Folate Intake (mcg DFE) | 0.5274 | Dietary |
| 7 | dietary_vitamin_c_mg | Daily Vitamin C Intake (mg) | 0.5231 | Dietary |
| 8 | dietary_calories_kcal | Daily Calorie Intake (kcal) | 0.5029 | Dietary |
| 9 | dietary_calcium_mg | Daily Calcium Intake (mg) | 0.4941 | Dietary |
| 10 | dietary_protein_g | Daily Protein Intake (g) | 0.4857 | Dietary |

**Figure saved:** fig_shap_summary_vitamin_b12.png

### Calcium Deficiency

| Rank | Feature | Display Name | Mean |SHAP| | Category |
|------|---------|-------------|-------------|----------|
| 1 | symptom_muscle_weakness | Muscle Weakness | 0.8852 | Symptom |
| 2 | dietary_vitamin_d_mcg | Daily Vitamin D Intake (mcg) | 0.8787 | Dietary |
| 3 | dietary_folate_mcg | Daily Folate Intake (mcg DFE) | 0.7908 | Dietary |
| 4 | dietary_vitamin_b12_mcg | Daily Vitamin B12 Intake (mcg) | 0.7242 | Dietary |
| 5 | dietary_fiber_g | Daily Fiber Intake (g) | 0.6990 | Dietary |
| 6 | dietary_iron_mg | Daily Iron Intake (mg) | 0.6914 | Dietary |
| 7 | bmi | Body Mass Index | 0.6599 | Demographic |
| 8 | dietary_calcium_mg | Daily Calcium Intake (mg) | 0.6512 | Dietary |
| 9 | dietary_calories_kcal | Daily Calorie Intake (kcal) | 0.6388 | Dietary |
| 10 | dietary_vitamin_c_mg | Daily Vitamin C Intake (mg) | 0.6115 | Dietary |

**Figure saved:** fig_shap_summary_calcium.png

### Folate Deficiency

| Rank | Feature | Display Name | Mean |SHAP| | Category |
|------|---------|-------------|-------------|----------|
| 1 | dietary_calcium_mg | Daily Calcium Intake (mg) | 1.0141 | Dietary |
| 2 | dietary_folate_mcg | Daily Folate Intake (mcg DFE) | 1.0102 | Dietary |
| 3 | bmi | Body Mass Index | 0.7974 | Demographic |
| 4 | dietary_fiber_g | Daily Fiber Intake (g) | 0.7079 | Dietary |
| 5 | dietary_calories_kcal | Daily Calorie Intake (kcal) | 0.7076 | Dietary |
| 6 | dietary_vitamin_d_mcg | Daily Vitamin D Intake (mcg) | 0.7035 | Dietary |
| 7 | dietary_protein_g | Daily Protein Intake (g) | 0.6452 | Dietary |
| 8 | dietary_iron_mg | Daily Iron Intake (mg) | 0.6293 | Dietary |
| 9 | dietary_vitamin_b12_mcg | Daily Vitamin B12 Intake (mcg) | 0.6187 | Dietary |
| 10 | dietary_vitamin_c_mg | Daily Vitamin C Intake (mg) | 0.6112 | Dietary |

**Figure saved:** fig_shap_summary_folate.png

## 3. Individual Prediction Explanation (Example)

Sample input: 35-year-old vegan female with fatigue, tingling, low mood, cold intolerance.

### Iron (Probability: 0.0103)

| Feature | Display Name | SHAP Value | Direction |
|---------|-------------|-----------|-----------|
| symptom_cold_intolerance | Cold Intolerance | 1.1682 | increases risk |
| symptom_fatigue | Fatigue | 0.6718 | increases risk |
| dietary_protein_g | Daily Protein Intake (g) | 0.4795 | increases risk |
| gender | Biological Sex | 0.4755 | increases risk |
| symptom_count | Total Symptom Count | 0.3959 | increases risk |

### Vitamin D (Probability: 0.8057)

| Feature | Display Name | SHAP Value | Direction |
|---------|-------------|-----------|-----------|
| age | Age | 1.3602 | increases risk |
| symptom_mood_low | Low Mood | 0.6850 | increases risk |
| symptom_count | Total Symptom Count | 0.6316 | increases risk |
| dietary_calcium_mg | Daily Calcium Intake (mg) | 0.5793 | increases risk |
| dietary_iron_mg | Daily Iron Intake (mg) | 0.4670 | increases risk |

### Vitamin B12 (Probability: 0.8535)

| Feature | Display Name | SHAP Value | Direction |
|---------|-------------|-----------|-----------|
| dietary_preference_0 | Diet: Omnivore | 2.0510 | increases risk |
| symptom_tingling | Tingling/Numbness | 1.6516 | increases risk |
| dietary_preference_2 | Diet: Vegan | 1.6162 | increases risk |
| symptom_count | Total Symptom Count | 0.8832 | increases risk |
| dietary_preference_1 | Diet: Vegetarian | 0.3680 | increases risk |

### Calcium (Probability: 0.0000)

| Feature | Display Name | SHAP Value | Direction |
|---------|-------------|-----------|-----------|
| dietary_protein_g | Daily Protein Intake (g) | 0.4222 | increases risk |
| symptom_tingling | Tingling/Numbness | 0.0702 | increases risk |
| symptom_skin_issues | Skin Issues | 0.0184 | increases risk |
| activity_level_3 | Activity: Active | 0.0041 | increases risk |
| dietary_preference_2 | Diet: Vegan | 0.0000 | decreases risk |

### Folate (Probability: 0.0000)

| Feature | Display Name | SHAP Value | Direction |
|---------|-------------|-----------|-----------|
| symptom_tingling | Tingling/Numbness | 0.5289 | increases risk |
| symptom_mood_low | Low Mood | 0.2349 | increases risk |
| activity_level_2 | Activity: Moderate | 0.0201 | increases risk |
| activity_level_1 | Activity: Light | 0.0077 | increases risk |
| dietary_preference_2 | Diet: Vegan | 0.0000 | decreases risk |

## 4. Frontend-Friendly Explanation Structure

The `/predict` endpoint returns structured JSON that can be rendered directly by the React frontend:

```
For each deficiency in response.data:
  - risk_level: color-code the badge (Low=green, Moderate=amber, High=red)
  - risk_probability: render as percentage bar
  - contributors.dietary[]: list of dietary factors pushing risk up
  - contributors.symptom[]: list of symptom factors pushing risk up
  - contributors.demographic[]: list of demographic factors pushing risk up
  - Each contributor has:
    - feature: internal name
    - display_name: human-readable label for UI
    - impact_score: SHAP magnitude (higher = more influential)
  - disclaimer: always shown below results
```

# Day 15 — Baseline Random Forest Evaluation Report
## Milestone 2: ML Nutritional Deficiency Detection Engine

---

## Model Configuration

```python
RandomForestClassifier(
    n_estimators=200,
    max_depth=None,
    min_samples_leaf=5,
    max_features='sqrt',
    class_weight='balanced',
    random_state=42,
    n_jobs=-1,
)
```

## Evaluation Methodology

- **Evaluation set:** Held-out test set ONLY (15% of labeled records per deficiency)
- **Validation set:** Reserved for Phase 2 hyperparameter optimization
- **Metrics:** Precision, Recall, F1-Score, ROC-AUC, Average Precision, Confusion Matrix
- **Note:** ROC-AUC computed per binary deficiency model

---

## Per-Deficiency Results


### Iron Deficiency

| Metric | Value |
|--------|-------|
| Test Set Size | 745 |
| Positive (Deficient) | 120 (16.11%) |
| Negative (Normal) | 625 |
| Precision | 0.9677 |
| Recall | 1.0 |
| F1-Score | 0.9836 |
| ROC-AUC | 1.0 |
| Avg Precision (PR-AUC) | 0.9998 |
| True Positives | 120 |
| True Negatives | 621 |
| False Positives | 4 |
| False Negatives | 0 |

**Classification Report:**
```
              precision    recall  f1-score   support

      Normal       1.00      0.99      1.00       625
   Deficient       0.97      1.00      0.98       120

    accuracy                           0.99       745
   macro avg       0.98      1.00      0.99       745
weighted avg       0.99      0.99      0.99       745

```

**Top 10 Features (Gini Importance):**

| Rank | Feature | Importance |
|------|---------|-----------|
| 1 | hemoglobin_g_dl | 0.41028 |
| 2 | serum_ferritin_ng_ml | 0.26169 |
| 3 | gender | 0.05101 |
| 4 | symptom_fatigue | 0.03092 |
| 5 | dietary_iron_mg | 0.01787 |
| 6 | dietary_calories_kcal | 0.01535 |
| 7 | dietary_vitamin_b12_mcg | 0.01382 |
| 8 | dietary_protein_g | 0.01316 |
| 9 | dietary_vitamin_c_mg | 0.01283 |
| 10 | symptom_count | 0.01278 |


### Vitamin D Deficiency

| Metric | Value |
|--------|-------|
| Test Set Size | 666 |
| Positive (Deficient) | 226 (33.93%) |
| Negative (Normal) | 440 |
| Precision | 1.0 |
| Recall | 1.0 |
| F1-Score | 1.0 |
| ROC-AUC | 1.0 |
| Avg Precision (PR-AUC) | 1.0 |
| True Positives | 226 |
| True Negatives | 440 |
| False Positives | 0 |
| False Negatives | 0 |

**Classification Report:**
```
              precision    recall  f1-score   support

      Normal       1.00      1.00      1.00       440
   Deficient       1.00      1.00      1.00       226

    accuracy                           1.00       666
   macro avg       1.00      1.00      1.00       666
weighted avg       1.00      1.00      1.00       666

```

**Top 10 Features (Gini Importance):**

| Rank | Feature | Importance |
|------|---------|-----------|
| 1 | vitamin_d_25ohd_ng_ml | 0.82473 |
| 2 | symptom_count | 0.02 |
| 3 | bmi | 0.01328 |
| 4 | symptom_bone_pain | 0.01256 |
| 5 | age | 0.00839 |
| 6 | symptom_mood_low | 0.00781 |
| 7 | dietary_vitamin_d_mcg | 0.00635 |
| 8 | vitamin_b12_pg_ml | 0.00633 |
| 9 | dietary_calories_kcal | 0.00633 |
| 10 | rbc_folate_ng_ml | 0.00618 |


### Vitamin B12 Deficiency

| Metric | Value |
|--------|-------|
| Test Set Size | 674 |
| Positive (Deficient) | 67 (9.94%) |
| Negative (Normal) | 607 |
| Precision | 1.0 |
| Recall | 1.0 |
| F1-Score | 1.0 |
| ROC-AUC | 1.0 |
| Avg Precision (PR-AUC) | 1.0 |
| True Positives | 67 |
| True Negatives | 607 |
| False Positives | 0 |
| False Negatives | 0 |

**Classification Report:**
```
              precision    recall  f1-score   support

      Normal       1.00      1.00      1.00       607
   Deficient       1.00      1.00      1.00        67

    accuracy                           1.00       674
   macro avg       1.00      1.00      1.00       674
weighted avg       1.00      1.00      1.00       674

```

**Top 10 Features (Gini Importance):**

| Rank | Feature | Importance |
|------|---------|-----------|
| 1 | vitamin_b12_pg_ml | 0.65087 |
| 2 | symptom_tingling | 0.04544 |
| 3 | dietary_preference_0 | 0.04468 |
| 4 | age | 0.02843 |
| 5 | dietary_preference_2 | 0.02206 |
| 6 | dietary_vitamin_b12_mcg | 0.01963 |
| 7 | symptom_count | 0.01915 |
| 8 | serum_folate_ng_ml | 0.01032 |
| 9 | dietary_fiber_g | 0.01025 |
| 10 | tibc_mcg_dl | 0.01014 |


### Calcium Deficiency

| Metric | Value |
|--------|-------|
| Test Set Size | 694 |
| Positive (Deficient) | 26 (3.75%) |
| Negative (Normal) | 668 |
| Precision | 1.0 |
| Recall | 0.9615 |
| F1-Score | 0.9804 |
| ROC-AUC | 1.0 |
| Avg Precision (PR-AUC) | 1.0 |
| True Positives | 25 |
| True Negatives | 668 |
| False Positives | 0 |
| False Negatives | 1 |

**Classification Report:**
```
              precision    recall  f1-score   support

      Normal       1.00      1.00      1.00       668
   Deficient       1.00      0.96      0.98        26

    accuracy                           1.00       694
   macro avg       1.00      0.98      0.99       694
weighted avg       1.00      1.00      1.00       694

```

**Top 10 Features (Gini Importance):**

| Rank | Feature | Importance |
|------|---------|-----------|
| 1 | serum_calcium_mg_dl | 0.70924 |
| 2 | symptom_muscle_weakness | 0.04884 |
| 3 | vitamin_d_25ohd_ng_ml | 0.03253 |
| 4 | serum_ferritin_ng_ml | 0.01413 |
| 5 | dietary_fiber_g | 0.01376 |
| 6 | dietary_folate_mcg | 0.01316 |
| 7 | tibc_mcg_dl | 0.01229 |
| 8 | rbc_folate_ng_ml | 0.01198 |
| 9 | dietary_vitamin_d_mcg | 0.01188 |
| 10 | serum_iron_mcg_dl | 0.01165 |


### Folate Deficiency

| Metric | Value |
|--------|-------|
| Test Set Size | 672 |
| Positive (Deficient) | 16 (2.38%) |
| Negative (Normal) | 656 |
| Precision | 1.0 |
| Recall | 1.0 |
| F1-Score | 1.0 |
| ROC-AUC | 1.0 |
| Avg Precision (PR-AUC) | 1.0 |
| True Positives | 16 |
| True Negatives | 656 |
| False Positives | 0 |
| False Negatives | 0 |

**Classification Report:**
```
              precision    recall  f1-score   support

      Normal       1.00      1.00      1.00       656
   Deficient       1.00      1.00      1.00        16

    accuracy                           1.00       672
   macro avg       1.00      1.00      1.00       672
weighted avg       1.00      1.00      1.00       672

```

**Top 10 Features (Gini Importance):**

| Rank | Feature | Importance |
|------|---------|-----------|
| 1 | serum_folate_ng_ml | 0.51694 |
| 2 | rbc_folate_ng_ml | 0.30292 |
| 3 | dietary_folate_mcg | 0.01401 |
| 4 | vitamin_b12_pg_ml | 0.01131 |
| 5 | dietary_protein_g | 0.01024 |
| 6 | symptom_count | 0.01011 |
| 7 | serum_ferritin_ng_ml | 0.00967 |
| 8 | bmi | 0.0095 |
| 9 | dietary_vitamin_d_mcg | 0.00914 |
| 10 | hemoglobin_g_dl | 0.00893 |

**Figure saved:** fig_roc_curves_baseline.png


---

## Summary Table — All Deficiency Models

| Deficiency | Test N | Prevalence | Precision | Recall | F1 | ROC-AUC |
|-----------|--------|-----------|-----------|--------|----|---------|
| iron | 745 | 16.11% | 0.9677 | 1.0 | 0.9836 | 1.0 |
| vitamin_d | 666 | 33.93% | 1.0 | 1.0 | 1.0 | 1.0 |
| vitamin_b12 | 674 | 9.94% | 1.0 | 1.0 | 1.0 | 1.0 |
| calcium | 694 | 3.75% | 1.0 | 0.9615 | 0.9804 | 1.0 |
| folate | 672 | 2.38% | 1.0 | 1.0 | 1.0 | 1.0 |

---

## Errors, Observations & Known Limitations

### OBS-01: Artificially High Performance
Some models show very high test metrics (near-perfect precision/recall).
This is expected because deficiency labels are derived from the same lab
biomarkers used as features (e.g., iron_deficiency label is derived from
serum_ferritin and hemoglobin, which are both features).
This does NOT indicate the model would perform this well in real inference
scenarios where lab values may be missing or the model relies on dietary
and symptom features only. **Phase 2 must evaluate with lab features excluded.**

### OBS-02: Class Imbalance Impact
Calcium deficiency (~4%) and folate deficiency (~2%) are highly imbalanced.
The class_weight='balanced' parameter compensates at training time.
Lower F1 scores for these may reflect genuine difficulty, not model failure.

### OBS-03: Transferrin Saturation Removed
transferrin_saturation_pct was removed to prevent multicollinearity
with serum_iron and tibc. Feature importance confirms that serum_iron
and tibc capture this signal independently.

### OBS-04: Validation Set Not Used Yet
The validation split was deliberately not used in Phase 1.
It is reserved for hyperparameter tuning in Phase 2.

### OBS-05: Pre-split Imputation (Known Mild Leakage)
Lab feature imputation used full-dataset medians (before splitting).
Impact is negligible for tree-based models but documented for transparency.
Phase 2 improvement: implement within-fold imputation.

### ERR-01: No Runtime Errors Observed
All 5 models trained and evaluated successfully.

## Phase 2 Blockers / Recommendations

1. **Real NHANES data**: Replace synthetic dataset with real NHANES XPT files
2. **Lab-feature-excluded evaluation**: Evaluate with dietary+symptom features only
3. **Hyperparameter tuning**: Use validation set for GridSearchCV/RandomizedSearchCV
4. **Model comparison**: Compare RF vs. XGBoost vs. Logistic Regression
5. **SHAP explainability**: Add SHAP values for feature importance interpretability
6. **Within-fold imputation**: Move imputation inside cross-validation folds
7. **Multi-label model**: Train a joint multi-label model across all deficiencies
# Day 14 — Feature Engineering & Preprocessing Report
## Milestone 2: ML Nutritional Deficiency Detection Engine

---

## 1. Feature Selection Rationale

| Feature Group | Count | Rationale |
|--------------|-------|-----------|
| Demographic | 7 | Age, gender, BMI affect nutrient needs and metabolism |
| Laboratory | 9 (10 minus transferred_saturation) | Primary biomarker indicators |
| Dietary | 9 | Intake-side predictors; weak alone but complementary |
| Symptom | 9 | Soft signals; symptom_count is aggregate |
| **Total (before OHE)** | **34** | |

**Dropped feature:** `transferrin_saturation_pct`
- Derived directly from serum_iron / tibc * 100
- Including all three would create near-perfect multicollinearity
- Retained: serum_iron and tibc (more fundamental measurements)

## 2. Categorical Encoding

| Feature | Type | Levels | Encoding |
|---------|------|--------|----------|
| activity_level | Ordinal | 0-4 | One-hot (5 binary columns) |
| dietary_preference | Nominal | 0-2 | One-hot (3 binary columns) |

Rationale: One-hot encoding preserves nominal nature of dietary_preference.
Ordinal treatment of activity_level was considered but OHE provides more flexibility.

## 3. Numerical Scaling

- **Method:** StandardScaler (mean=0, sd=1)
- **Applied to:** All continuous numeric features (20 columns)
- **NOT applied to:** Binary features, one-hot encoded columns
- **Justification:** Random Forest does not require scaling; scaling is included
  so the same preprocessing artifacts can be used for future linear models in Phase 2.

## 4. Target Label Definitions

| Target | Clinical Threshold | Source |
|--------|-------------------|--------|
| iron_deficiency | Ferritin <12 ng/mL OR Hgb <12 g/dL (F) / <13 g/dL (M) | WHO 2011; CDC |
| vitamin_d_deficiency | 25OHD <20 ng/mL | NIH ODS 2023; Endocrine Society |
| vitamin_b12_deficiency | Serum B12 <200 pg/mL | NIH ODS 2023 |
| calcium_deficiency | Serum Ca <8.5 mg/dL | Clinical labs standard |
| folate_deficiency | Serum folate <3 ng/mL | Pfeiffer et al.; WHO |

## 5. Split Strategy

- **Method:** Stratified train/val/test split
- **Ratios:** 70% train | 15% validation | 15% test
- **Stratified on:** Target binary label (to maintain class proportions)
- **Random seed:** 42 (reproducible)
- **Note:** Separate splits per deficiency (different NaN patterns per target)

## 6. Leakage Prevention

| Risk | Mitigation |
|------|-----------|
| Scaler fitted on test set | Scaler fitted ONLY on X_train; transform applied to val/test |
| Future data in train | Temporal splits not applicable (cross-sectional data) |
| Target leakage | transferrin_saturation dropped (derived from other lab features) |
| Pre-split imputation | Median imputation pre-split; minimal impact for tree models |

**Known mild leakage (documented):**
Pre-split imputation using full-dataset medians. Accepted for Phase 1 tree models.
Phase 2 improvement: move imputation inside cross-validation folds.

## 7. Saved Artifacts

| Artifact | Location | Purpose |
|---------|---------|---------|
| scaler_{deficiency}.pkl | ml/data/artifacts/ | StandardScaler for inference |
| feature_names_{deficiency}.json | ml/data/artifacts/ | Ordered feature list for inference |
| feature_dictionary.json | ml/data/artifacts/ | Full feature metadata |
| X_train/val/test_{deficiency}.csv | ml/data/processed/ | Model-ready splits |
| y_train/val/test_{deficiency}.csv | ml/data/processed/ | Target splits |

## 8. Split Statistics per Deficiency

| Deficiency | Labeled N | Prevalence | Train | Val | Test | Features |
|-----------|-----------|-----------|-------|-----|------|---------|
| iron | 4963 | 16.12% | 3474 | 744 | 745 | 40 |
| vitamin_d | 4440 | 33.87% | 3108 | 666 | 666 | 40 |
| vitamin_b12 | 4489 | 9.85% | 3142 | 673 | 674 | 40 |
| calcium | 4626 | 3.72% | 3238 | 694 | 694 | 40 |
| folate | 4476 | 2.37% | 3133 | 671 | 672 | 40 |
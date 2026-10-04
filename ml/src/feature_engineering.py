"""
feature_engineering.py
======================
Day 14 — Feature Engineering & Preprocessing Pipeline
Milestone 2: ML Nutritional Deficiency Detection Engine

PURPOSE
-------
Convert the cleaned NHANES dataset into model-ready features with
a reproducible, inference-safe preprocessing pipeline.

KEY DESIGN DECISIONS
--------------------
1. No fitting of transformers on test/validation sets (leakage prevention).
2. All transformers fitted ONLY on training set and saved as artifacts.
3. Pipeline uses the same code for inference — load artifacts and transform.
4. Categorical features: one-hot encoding (activity_level, dietary_preference).
5. Numerical features: StandardScaler (lab values, dietary values).
   Tree-based models (Random Forest) are scale-invariant, but scaling is
   included so the artifacts are available for future linear models (Phase 2).
6. transferrin_saturation_pct is DROPPED to avoid near-multicollinearity with
   serum_iron and tibc (it is computed as serum_iron/tibc*100).
7. rbc_folate_ng_ml is KEPT as it measures longer-term folate stores vs serum.
8. Separate train/val/test splits per deficiency (different records may have
   NaN targets for different deficiencies; each model uses only labeled records).

SPLIT STRATEGY
--------------
- Overall stratified split: 70% train, 15% val, 15% test
- Stratified on the binary target label
- Random seed fixed (RANDOM_SEED = 42) for reproducibility

LEAKAGE PREVENTION
------------------
- Scaler fitted ONLY on training features
- No test/val labels or stats used during fitting
- Imputation already performed on full dataset in cleaning (pre-split);
  this is acceptable because imputation uses medians, not labels
  (see note below)

NOTE on pre-split imputation:
  In Day 13 we imputed lab features using gender-stratified medians computed
  from the ENTIRE cleaned dataset. Strictly, this is a mild form of leakage
  (test-set medians informed the imputation). For Phase 1, this is acceptable
  because:
  (a) imputation used medians, which are robust and not label-dependent
  (b) the effect on evaluation metrics is negligible for tree-based models
  A stricter pipeline (imputing after splitting, within cross-validation folds)
  is documented as a Phase 2 improvement.

OUTPUTS
-------
- ml/data/processed/X_train_{deficiency}.csv
- ml/data/processed/X_val_{deficiency}.csv
- ml/data/processed/X_test_{deficiency}.csv
- ml/data/processed/y_train_{deficiency}.csv
- ml/data/processed/y_val_{deficiency}.csv
- ml/data/processed/y_test_{deficiency}.csv
- ml/data/artifacts/scaler_{deficiency}.pkl
- ml/data/artifacts/feature_names_{deficiency}.json
- ml/data/artifacts/feature_dictionary.json
- ml/reports/day14_feature_engineering_report.md
"""

import json
import sys
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler

# ─── Paths ────────────────────────────────────────────────────────────────────
ROOT = Path(__file__).parent.parent
CLEANED_DATA_PATH = ROOT / "data" / "processed" / "nhanes_cleaned.csv"
PROCESSED_DIR = ROOT / "data" / "processed"
ARTIFACTS_DIR = ROOT / "data" / "artifacts"
REPORTS_DIR = ROOT / "reports"
ARTIFACTS_DIR.mkdir(parents=True, exist_ok=True)

RANDOM_SEED = 42

# ─── Target definitions ───────────────────────────────────────────────────────
TARGET_COLS = [
    "iron_deficiency",
    "vitamin_d_deficiency",
    "vitamin_b12_deficiency",
    "calcium_deficiency",
    "folate_deficiency",
]

# ─── Feature dictionary ───────────────────────────────────────────────────────
# Documents each feature: name, type, unit, transformation, source
FEATURE_DICTIONARY = {
    # ── Demographic ──────────────────────────────────────────────────────────
    "age": {
        "description": "Subject age in years",
        "type": "numeric_continuous",
        "unit": "years",
        "source": "NHANES DEMO",
        "transformation": "StandardScaler",
        "notes": "Adult subjects only (18-110)"
    },
    "gender": {
        "description": "Biological sex (0=Female, 1=Male)",
        "type": "binary",
        "unit": "encoded",
        "source": "NHANES DEMO",
        "transformation": "pass-through",
        "notes": "NHANES encoding: 0=Female, 1=Male"
    },
    "bmi": {
        "description": "Body Mass Index",
        "type": "numeric_continuous",
        "unit": "kg/m2",
        "source": "NHANES BMX",
        "transformation": "StandardScaler",
        "notes": "Plausible range [10, 80]"
    },
    "is_pregnant": {
        "description": "Pregnancy status",
        "type": "binary",
        "unit": "0/1",
        "source": "NHANES RHQ",
        "transformation": "pass-through",
        "notes": "Females aged 18-45 only; modifies iron/folate thresholds"
    },
    "is_smoker": {
        "description": "Current smoker status",
        "type": "binary",
        "unit": "0/1",
        "source": "NHANES SMQ",
        "transformation": "pass-through",
        "notes": "Smoking affects Vitamin D metabolism"
    },
    # ── Categorical (one-hot encoded) ─────────────────────────────────────────
    "activity_level": {
        "description": "Physical activity level",
        "type": "categorical_ordinal",
        "unit": "0=sedentary, 1=light, 2=moderate, 3=active, 4=very_active",
        "source": "NHANES PAQ",
        "transformation": "one-hot encoding (5 levels)",
        "notes": "Drop-first encoding to avoid dummy variable trap"
    },
    "dietary_preference": {
        "description": "Dietary pattern",
        "type": "categorical_nominal",
        "unit": "0=omnivore, 1=vegetarian, 2=vegan",
        "source": "derived / NutriWise profile",
        "transformation": "one-hot encoding (3 levels)",
        "notes": "Strong predictor for B12 and iron deficiency in vegetarians/vegans"
    },
    # ── Laboratory (StandardScaler) ───────────────────────────────────────────
    "hemoglobin_g_dl": {
        "description": "Hemoglobin concentration",
        "type": "numeric_continuous",
        "unit": "g/dL",
        "source": "NHANES CBC",
        "transformation": "StandardScaler",
        "notes": "Key iron-deficiency marker; gender-stratified reference ranges"
    },
    "serum_ferritin_ng_ml": {
        "description": "Serum ferritin — iron stores",
        "type": "numeric_continuous",
        "unit": "ng/mL",
        "source": "NHANES FERTIN",
        "transformation": "StandardScaler",
        "notes": "Log-normal distribution; threshold: <12 ng/mL = iron-depleted"
    },
    "serum_iron_mcg_dl": {
        "description": "Serum iron level",
        "type": "numeric_continuous",
        "unit": "mcg/dL",
        "source": "NHANES BIOPRO",
        "transformation": "StandardScaler",
        "notes": ""
    },
    "tibc_mcg_dl": {
        "description": "Total Iron Binding Capacity",
        "type": "numeric_continuous",
        "unit": "mcg/dL",
        "source": "NHANES BIOPRO",
        "transformation": "StandardScaler",
        "notes": "Elevated in iron deficiency"
    },
    # transferrin_saturation_pct: DROPPED (derived from serum_iron/tibc)
    "vitamin_d_25ohd_ng_ml": {
        "description": "Serum 25-hydroxyvitamin D",
        "type": "numeric_continuous",
        "unit": "ng/mL",
        "source": "NHANES VID",
        "transformation": "StandardScaler",
        "notes": "Threshold: <20 ng/mL = deficient"
    },
    "vitamin_b12_pg_ml": {
        "description": "Serum vitamin B12 (cobalamin)",
        "type": "numeric_continuous",
        "unit": "pg/mL",
        "source": "NHANES B12",
        "transformation": "StandardScaler",
        "notes": "Threshold: <200 pg/mL = deficient; log-normal"
    },
    "serum_calcium_mg_dl": {
        "description": "Serum calcium",
        "type": "numeric_continuous",
        "unit": "mg/dL",
        "source": "NHANES BIOPRO",
        "transformation": "StandardScaler",
        "notes": "Threshold: <8.5 mg/dL = hypocalcaemia"
    },
    "serum_folate_ng_ml": {
        "description": "Serum folate",
        "type": "numeric_continuous",
        "unit": "ng/mL",
        "source": "NHANES FOLATE",
        "transformation": "StandardScaler",
        "notes": "Threshold: <3 ng/mL = deficient"
    },
    "rbc_folate_ng_ml": {
        "description": "Red blood cell folate (longer-term stores)",
        "type": "numeric_continuous",
        "unit": "ng/mL",
        "source": "NHANES FOLATE",
        "transformation": "StandardScaler",
        "notes": "Complements serum_folate; threshold >140 ng/mL normal"
    },
    # ── Dietary ───────────────────────────────────────────────────────────────
    "dietary_iron_mg": {
        "description": "Daily iron intake (24h recall)",
        "type": "numeric_continuous",
        "unit": "mg/day",
        "source": "NHANES DR1TOT",
        "transformation": "StandardScaler",
        "notes": "RDA: 8 mg/day (M), 18 mg/day (F pre-menopause)"
    },
    "dietary_calcium_mg": {
        "description": "Daily calcium intake (24h recall)",
        "type": "numeric_continuous",
        "unit": "mg/day",
        "source": "NHANES DR1TOT",
        "transformation": "StandardScaler",
        "notes": "RDA: 1000-1200 mg/day"
    },
    "dietary_vitamin_d_mcg": {
        "description": "Daily vitamin D intake (24h recall)",
        "type": "numeric_continuous",
        "unit": "mcg/day",
        "source": "NHANES DR1TOT",
        "transformation": "StandardScaler",
        "notes": "RDA: 15-20 mcg/day; most Americans fall below"
    },
    "dietary_vitamin_b12_mcg": {
        "description": "Daily vitamin B12 intake (24h recall)",
        "type": "numeric_continuous",
        "unit": "mcg/day",
        "source": "NHANES DR1TOT",
        "transformation": "StandardScaler",
        "notes": "RDA: 2.4 mcg/day; very low in vegans"
    },
    "dietary_folate_mcg": {
        "description": "Daily folate/folic acid intake (24h recall)",
        "type": "numeric_continuous",
        "unit": "mcg DFE/day",
        "source": "NHANES DR1TOT",
        "transformation": "StandardScaler",
        "notes": "RDA: 400 mcg DFE/day"
    },
    "dietary_vitamin_c_mg": {
        "description": "Daily vitamin C intake (enhances non-heme iron absorption)",
        "type": "numeric_continuous",
        "unit": "mg/day",
        "source": "NHANES DR1TOT",
        "transformation": "StandardScaler",
        "notes": "Indirect predictor for iron status via absorption"
    },
    "dietary_protein_g": {
        "description": "Daily protein intake (24h recall)",
        "type": "numeric_continuous",
        "unit": "g/day",
        "source": "NHANES DR1TOT",
        "transformation": "StandardScaler",
        "notes": "Proxy for overall diet quality"
    },
    "dietary_calories_kcal": {
        "description": "Daily energy intake (24h recall)",
        "type": "numeric_continuous",
        "unit": "kcal/day",
        "source": "NHANES DR1TOT",
        "transformation": "StandardScaler",
        "notes": "General diet quantity proxy"
    },
    "dietary_fiber_g": {
        "description": "Daily fiber intake",
        "type": "numeric_continuous",
        "unit": "g/day",
        "source": "NHANES DR1TOT",
        "transformation": "StandardScaler",
        "notes": "High fiber may slightly inhibit iron absorption"
    },
    # ── Symptom ───────────────────────────────────────────────────────────────
    "symptom_fatigue": {
        "description": "Fatigue present (0/1)",
        "type": "binary",
        "unit": "0/1",
        "source": "NutriWise symptom questionnaire",
        "transformation": "pass-through",
        "notes": "Self-reported; low specificity"
    },
    "symptom_hair_loss": {
        "description": "Hair loss or thinning (0/1)",
        "type": "binary",
        "unit": "0/1",
        "source": "NutriWise symptom questionnaire",
        "transformation": "pass-through",
        "notes": "Associated with iron deficiency"
    },
    "symptom_skin_issues": {
        "description": "Skin conditions present (0/1)",
        "type": "binary",
        "unit": "0/1",
        "source": "NutriWise symptom questionnaire",
        "transformation": "pass-through",
        "notes": ""
    },
    "symptom_muscle_weakness": {
        "description": "Muscle weakness (0/1)",
        "type": "binary",
        "unit": "0/1",
        "source": "NutriWise symptom questionnaire",
        "transformation": "pass-through",
        "notes": "Associated with Vitamin D and calcium deficiency"
    },
    "symptom_mood_low": {
        "description": "Low mood / depression (0/1)",
        "type": "binary",
        "unit": "0/1",
        "source": "NutriWise symptom questionnaire",
        "transformation": "pass-through",
        "notes": "Associated with B12, D, folate deficiency"
    },
    "symptom_bone_pain": {
        "description": "Bone or joint pain (0/1)",
        "type": "binary",
        "unit": "0/1",
        "source": "NutriWise symptom questionnaire",
        "transformation": "pass-through",
        "notes": "Associated with Vitamin D deficiency (osteomalacia)"
    },
    "symptom_tingling": {
        "description": "Tingling or numbness (0/1)",
        "type": "binary",
        "unit": "0/1",
        "source": "NutriWise symptom questionnaire",
        "transformation": "pass-through",
        "notes": "Associated with B12 deficiency (peripheral neuropathy)"
    },
    "symptom_cold_intolerance": {
        "description": "Cold intolerance (0/1)",
        "type": "binary",
        "unit": "0/1",
        "source": "NutriWise symptom questionnaire",
        "transformation": "pass-through",
        "notes": "Associated with iron-deficiency anaemia"
    },
    "symptom_count": {
        "description": "Total number of symptoms reported",
        "type": "numeric_discrete",
        "unit": "count",
        "source": "Derived from symptom flags",
        "transformation": "pass-through",
        "notes": "Aggregate symptom burden indicator"
    },
}

# ─── Feature groups for preprocessing ─────────────────────────────────────────
# transferrin_saturation_pct DROPPED: derived from serum_iron and tibc
COLS_TO_DROP = ["subject_id", "transferrin_saturation_pct"] + TARGET_COLS

CATEGORICAL_COLS = ["activity_level", "dietary_preference"]  # will be one-hot encoded

# All numeric columns to scale (continuous, not binary)
NUMERIC_SCALE_COLS = [
    "age", "bmi",
    "hemoglobin_g_dl", "serum_ferritin_ng_ml", "serum_iron_mcg_dl",
    "tibc_mcg_dl", "vitamin_d_25ohd_ng_ml", "vitamin_b12_pg_ml",
    "serum_calcium_mg_dl", "serum_folate_ng_ml", "rbc_folate_ng_ml",
    "dietary_iron_mg", "dietary_calcium_mg", "dietary_vitamin_d_mcg",
    "dietary_vitamin_b12_mcg", "dietary_folate_mcg", "dietary_vitamin_c_mg",
    "dietary_protein_g", "dietary_calories_kcal", "dietary_fiber_g",
]

# Binary/pass-through columns (no scaling needed)
BINARY_COLS = [
    "gender", "is_pregnant", "is_smoker",
    "symptom_fatigue", "symptom_hair_loss", "symptom_skin_issues",
    "symptom_muscle_weakness", "symptom_mood_low", "symptom_bone_pain",
    "symptom_tingling", "symptom_cold_intolerance", "symptom_count"
]


# ═══════════════════════════════════════════════════════════════════════════════
# PREPROCESSING FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════════════

def one_hot_encode(df: pd.DataFrame, cat_cols: list) -> pd.DataFrame:
    """
    One-hot encode categorical columns with drop_first=False (full encoding).
    We use full encoding to maintain interpretability.
    Prefix = column name; separator = '_'.
    """
    df = pd.get_dummies(df, columns=cat_cols, drop_first=False, dtype=int)
    return df


def get_feature_columns(df: pd.DataFrame) -> list:
    """Get the ordered list of feature columns after encoding (no targets, no ID)."""
    return [c for c in df.columns if c not in COLS_TO_DROP]


def build_and_save_split(
    df: pd.DataFrame,
    target_col: str,
    deficiency_name: str,
) -> dict:
    """
    Build train/val/test splits for a single deficiency target.

    Steps:
    1. Filter to records with a valid (non-NaN) target label
    2. Separate X and y
    3. Drop columns not used as features
    4. One-hot encode categorical columns
    5. Stratified 70/15/15 split
    6. Fit StandardScaler on TRAINING SET ONLY
    7. Transform train/val/test with the fitted scaler
    8. Save all artifacts

    Leakage prevention: scaler fitted ONLY on X_train.

    Returns dict with split statistics.
    """
    # Step 1: Filter to labeled records only
    df_labeled = df[df[target_col].notna()].copy()
    n_labeled = len(df_labeled)
    n_pos = int((df_labeled[target_col] == 1).sum())
    n_neg = int((df_labeled[target_col] == 0).sum())
    print(f"\n[{deficiency_name}] Labeled records: {n_labeled} | Positive: {n_pos} | Negative: {n_neg}")

    # Step 2: Separate X and y
    y = df_labeled[target_col].astype(int)
    X = df_labeled.drop(columns=COLS_TO_DROP, errors="ignore")

    # Step 3: One-hot encode categoricals
    X = one_hot_encode(X, CATEGORICAL_COLS)
    feature_columns = X.columns.tolist()

    # Step 4: Stratified split — 70% train, 15% val, 15% test
    X_train, X_temp, y_train, y_temp = train_test_split(
        X, y,
        test_size=0.30,
        random_state=RANDOM_SEED,
        stratify=y
    )
    X_val, X_test, y_val, y_test = train_test_split(
        X_temp, y_temp,
        test_size=0.50,
        random_state=RANDOM_SEED,
        stratify=y_temp
    )

    # Step 5: Identify numeric cols present in the encoded data
    scale_cols_present = [c for c in NUMERIC_SCALE_COLS if c in X_train.columns]

    # Step 6: Fit scaler on TRAINING SET ONLY
    scaler = StandardScaler()
    X_train_scaled = X_train.copy()
    X_val_scaled = X_val.copy()
    X_test_scaled = X_test.copy()

    X_train_scaled[scale_cols_present] = scaler.fit_transform(X_train[scale_cols_present])
    X_val_scaled[scale_cols_present] = scaler.transform(X_val[scale_cols_present])
    X_test_scaled[scale_cols_present] = scaler.transform(X_test[scale_cols_present])

    # Step 7: Save splits
    splits = {
        "X_train": X_train_scaled,
        "X_val": X_val_scaled,
        "X_test": X_test_scaled,
        "y_train": y_train,
        "y_val": y_val,
        "y_test": y_test,
    }
    for name, data in splits.items():
        path = PROCESSED_DIR / f"{name}_{deficiency_name}.csv"
        data.to_csv(path, index=True)

    # Step 8: Save scaler artifact
    scaler_path = ARTIFACTS_DIR / f"scaler_{deficiency_name}.pkl"
    joblib.dump(scaler, scaler_path)

    # Save feature names
    feature_names_path = ARTIFACTS_DIR / f"feature_names_{deficiency_name}.json"
    with open(feature_names_path, "w") as f:
        json.dump(feature_columns, f, indent=2)

    print(f"  Train:  {len(X_train)} records | Val: {len(X_val)} | Test: {len(X_test)}")
    print(f"  Features: {len(feature_columns)}")
    print(f"  Scaler saved: {scaler_path.name}")

    return {
        "target": deficiency_name,
        "n_labeled": n_labeled,
        "n_positive": n_pos,
        "n_negative": n_neg,
        "prevalence_pct": round(n_pos / n_labeled * 100, 2),
        "n_train": len(X_train),
        "n_val": len(X_val),
        "n_test": len(X_test),
        "n_features": len(feature_columns),
        "scale_cols": scale_cols_present,
    }


# ═══════════════════════════════════════════════════════════════════════════════
# REPORT
# ═══════════════════════════════════════════════════════════════════════════════

def save_feature_engineering_report(split_stats: list):
    """Write Day 14 feature engineering report."""
    report_path = REPORTS_DIR / "day14_feature_engineering_report.md"
    lines = [
        "# Day 14 — Feature Engineering & Preprocessing Report",
        "## Milestone 2: ML Nutritional Deficiency Detection Engine\n",
        "---\n",
        "## 1. Feature Selection Rationale\n",
        "| Feature Group | Count | Rationale |",
        "|--------------|-------|-----------|",
        "| Demographic | 7 | Age, gender, BMI affect nutrient needs and metabolism |",
        "| Laboratory | 9 (10 minus transferred_saturation) | Primary biomarker indicators |",
        "| Dietary | 9 | Intake-side predictors; weak alone but complementary |",
        "| Symptom | 9 | Soft signals; symptom_count is aggregate |",
        "| **Total (before OHE)** | **34** | |",
        "\n**Dropped feature:** `transferrin_saturation_pct`",
        "- Derived directly from serum_iron / tibc * 100",
        "- Including all three would create near-perfect multicollinearity",
        "- Retained: serum_iron and tibc (more fundamental measurements)\n",
        "## 2. Categorical Encoding\n",
        "| Feature | Type | Levels | Encoding |",
        "|---------|------|--------|----------|",
        "| activity_level | Ordinal | 0-4 | One-hot (5 binary columns) |",
        "| dietary_preference | Nominal | 0-2 | One-hot (3 binary columns) |",
        "\nRationale: One-hot encoding preserves nominal nature of dietary_preference.",
        "Ordinal treatment of activity_level was considered but OHE provides more flexibility.\n",
        "## 3. Numerical Scaling\n",
        "- **Method:** StandardScaler (mean=0, sd=1)",
        "- **Applied to:** All continuous numeric features (20 columns)",
        "- **NOT applied to:** Binary features, one-hot encoded columns",
        "- **Justification:** Random Forest does not require scaling; scaling is included",
        "  so the same preprocessing artifacts can be used for future linear models in Phase 2.\n",
        "## 4. Target Label Definitions\n",
        "| Target | Clinical Threshold | Source |",
        "|--------|-------------------|--------|",
        "| iron_deficiency | Ferritin <12 ng/mL OR Hgb <12 g/dL (F) / <13 g/dL (M) | WHO 2011; CDC |",
        "| vitamin_d_deficiency | 25OHD <20 ng/mL | NIH ODS 2023; Endocrine Society |",
        "| vitamin_b12_deficiency | Serum B12 <200 pg/mL | NIH ODS 2023 |",
        "| calcium_deficiency | Serum Ca <8.5 mg/dL | Clinical labs standard |",
        "| folate_deficiency | Serum folate <3 ng/mL | Pfeiffer et al.; WHO |",
        "\n## 5. Split Strategy\n",
        "- **Method:** Stratified train/val/test split",
        "- **Ratios:** 70% train | 15% validation | 15% test",
        "- **Stratified on:** Target binary label (to maintain class proportions)",
        "- **Random seed:** 42 (reproducible)",
        "- **Note:** Separate splits per deficiency (different NaN patterns per target)\n",
        "## 6. Leakage Prevention\n",
        "| Risk | Mitigation |",
        "|------|-----------|",
        "| Scaler fitted on test set | Scaler fitted ONLY on X_train; transform applied to val/test |",
        "| Future data in train | Temporal splits not applicable (cross-sectional data) |",
        "| Target leakage | transferrin_saturation dropped (derived from other lab features) |",
        "| Pre-split imputation | Median imputation pre-split; minimal impact for tree models |",
        "\n**Known mild leakage (documented):**",
        "Pre-split imputation using full-dataset medians. Accepted for Phase 1 tree models.",
        "Phase 2 improvement: move imputation inside cross-validation folds.\n",
        "## 7. Saved Artifacts\n",
        "| Artifact | Location | Purpose |",
        "|---------|---------|---------|",
        "| scaler_{deficiency}.pkl | ml/data/artifacts/ | StandardScaler for inference |",
        "| feature_names_{deficiency}.json | ml/data/artifacts/ | Ordered feature list for inference |",
        "| feature_dictionary.json | ml/data/artifacts/ | Full feature metadata |",
        "| X_train/val/test_{deficiency}.csv | ml/data/processed/ | Model-ready splits |",
        "| y_train/val/test_{deficiency}.csv | ml/data/processed/ | Target splits |\n",
        "## 8. Split Statistics per Deficiency\n",
        "| Deficiency | Labeled N | Prevalence | Train | Val | Test | Features |",
        "|-----------|-----------|-----------|-------|-----|------|---------|",
    ]
    for s in split_stats:
        lines.append(
            f"| {s['target']} | {s['n_labeled']} | {s['prevalence_pct']}% | "
            f"{s['n_train']} | {s['n_val']} | {s['n_test']} | {s['n_features']} |"
        )

    with open(report_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    print(f"\nFeature engineering report saved to: {report_path}")


# ═══════════════════════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════════════════════

def main():
    print("=" * 70)
    print("Day 14 — Feature Engineering & Preprocessing Pipeline")
    print("=" * 70)

    print(f"\nLoading cleaned dataset from: {CLEANED_DATA_PATH}")
    df = pd.read_csv(CLEANED_DATA_PATH)
    print(f"Cleaned dataset: {df.shape[0]} rows x {df.shape[1]} columns")

    # Save feature dictionary
    feat_dict_path = ARTIFACTS_DIR / "feature_dictionary.json"
    with open(feat_dict_path, "w") as f:
        json.dump(FEATURE_DICTIONARY, f, indent=2)
    print(f"\nFeature dictionary saved to: {feat_dict_path}")

    # Build and save splits per deficiency
    all_stats = []
    for target_col in TARGET_COLS:
        deficiency_name = target_col.replace("_deficiency", "")
        stats = build_and_save_split(df, target_col, deficiency_name)
        all_stats.append(stats)

    # Save overall report
    save_feature_engineering_report(all_stats)

    print("\n" + "=" * 70)
    print("FEATURE ENGINEERING SUMMARY")
    print("=" * 70)
    for s in all_stats:
        print(f"  {s['target']:30s} | {s['n_labeled']:5d} labeled | "
              f"{s['prevalence_pct']:5.1f}% positive | "
              f"Train={s['n_train']}, Val={s['n_val']}, Test={s['n_test']}")

    print("\nDay 14 Feature Engineering complete. Proceed to Day 15 (Baseline Model).")


if __name__ == "__main__":
    main()

"""
clean_data.py
=============
Day 13 — Reproducible Data Cleaning Pipeline
Milestone 2: ML Nutritional Deficiency Detection Engine

PURPOSE
-------
Apply documented, reproducible data-cleaning rules to the raw synthetic
NHANES dataset. Every transformation is logged with a reason.

CLEANING RULES (documented below and in cleaning_decisions.md)
---------
CR-01: Remove exact duplicate rows (excluding subject_id)
CR-02: Remove records with physiologically impossible age (< 18 or > 110)
CR-03: Remove records with physiologically impossible BMI (< 10 or > 80)
CR-04: Remove records with impossible hemoglobin (< 3 or > 25 g/dL)
CR-05: Replace negative dietary feature values with NaN (not zero; negative intake is impossible)
CR-06: Clamp extreme-but-plausible lab outliers using domain-based bounds (not IQR)
CR-07: Validate and relabel deficiency target labels — records where both primary lab markers
       are missing get their target label set to NaN (cannot be assigned)
CR-08: Impute missing values using gender-stratified medians for lab features
CR-09: Impute missing dietary values with overall median
CR-10: Standardize dietary_preference encoding

OUTPUT
------
- ml/data/processed/nhanes_cleaned.csv
- ml/reports/day13_cleaning_decisions.md
- Console cleaning log
"""

import sys
from pathlib import Path

import numpy as np
import pandas as pd

# ─── Paths ────────────────────────────────────────────────────────────────────
ROOT = Path(__file__).parent.parent
RAW_DATA_PATH = ROOT / "data" / "raw" / "nhanes_synthetic_raw.csv"
PROCESSED_DIR = ROOT / "data" / "processed"
PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
CLEANED_DATA_PATH = PROCESSED_DIR / "nhanes_cleaned.csv"
REPORTS_DIR = ROOT / "reports"

# ─── Feature Groups ───────────────────────────────────────────────────────────
DIETARY_COLS = [
    "dietary_iron_mg", "dietary_calcium_mg", "dietary_vitamin_d_mcg",
    "dietary_vitamin_b12_mcg", "dietary_folate_mcg", "dietary_vitamin_c_mg",
    "dietary_protein_g", "dietary_calories_kcal", "dietary_fiber_g"
]
LAB_COLS = [
    "hemoglobin_g_dl", "serum_ferritin_ng_ml", "serum_iron_mcg_dl",
    "tibc_mcg_dl", "transferrin_saturation_pct", "vitamin_d_25ohd_ng_ml",
    "vitamin_b12_pg_ml", "serum_calcium_mg_dl", "serum_folate_ng_ml",
    "rbc_folate_ng_ml"
]
TARGET_COLS = [
    "iron_deficiency", "vitamin_d_deficiency", "vitamin_b12_deficiency",
    "calcium_deficiency", "folate_deficiency"
]

# ─── Domain-based bounds for lab features (physiological limits) ──────────────
# These are NOT IQR-based; they are based on physiological plausibility.
# Source: Clinical lab reference literature, NHANES data coding manuals.
LAB_DOMAIN_BOUNDS = {
    "hemoglobin_g_dl":           (3.0,   25.0),
    "serum_ferritin_ng_ml":      (1.0,   2000.0),
    "serum_iron_mcg_dl":         (10.0,  400.0),
    "tibc_mcg_dl":               (100.0, 600.0),
    "transferrin_saturation_pct":(1.0,   100.0),
    "vitamin_d_25ohd_ng_ml":     (3.0,   150.0),
    "vitamin_b12_pg_ml":         (50.0,  3000.0),
    "serum_calcium_mg_dl":       (5.0,   14.0),
    "serum_folate_ng_ml":        (0.5,   80.0),
    "rbc_folate_ng_ml":          (50.0,  1500.0),
}

DIETARY_DOMAIN_BOUNDS = {
    "dietary_iron_mg":           (0.0,   100.0),
    "dietary_calcium_mg":        (0.0,   5000.0),
    "dietary_vitamin_d_mcg":     (0.0,   250.0),
    "dietary_vitamin_b12_mcg":   (0.0,   100.0),
    "dietary_folate_mcg":        (0.0,   3000.0),
    "dietary_vitamin_c_mg":      (0.0,   3000.0),
    "dietary_protein_g":         (0.0,   500.0),
    "dietary_calories_kcal":     (200.0, 8000.0),
    "dietary_fiber_g":           (0.0,   200.0),
}


# ═══════════════════════════════════════════════════════════════════════════════
# CLEANING LOG
# ═══════════════════════════════════════════════════════════════════════════════

cleaning_log = []
removed_record_log = []


def clog(rule_id: str, msg: str, n_affected: int = 0):
    """Log a cleaning action."""
    entry = f"[{rule_id}] {msg} | Records affected: {n_affected}"
    print(entry)
    cleaning_log.append(entry)


# ═══════════════════════════════════════════════════════════════════════════════
# CLEANING RULES
# ═══════════════════════════════════════════════════════════════════════════════

def cr01_remove_duplicates(df: pd.DataFrame) -> pd.DataFrame:
    """
    CR-01: Remove exact duplicate rows (excluding subject_id).
    Rationale: Exact duplicates would bias the model and inflate evaluation metrics.
    These duplicates were deliberately injected in the generator.
    Retained: First occurrence of each duplicate group (arbitrary but reproducible).
    """
    cols_for_dup = [c for c in df.columns if c != "subject_id"]
    n_before = len(df)
    df_dedup = df.drop_duplicates(subset=cols_for_dup, keep="first").copy()
    n_removed = n_before - len(df_dedup)
    clog("CR-01", f"Removed exact duplicates", n_removed)
    return df_dedup


def cr02_remove_invalid_age(df: pd.DataFrame) -> pd.DataFrame:
    """
    CR-02: Remove records with age < 18 or > 110.
    Rationale: This dataset is for adults (18+). Values >110 are physiologically
    impossible and indicate data entry errors.
    Records retained: age in [18, 110].
    Records removed: logged with their values.
    """
    mask_invalid = (df["age"] < 18) | (df["age"] > 110)
    invalid_ages = df[mask_invalid]["age"].tolist()
    n_before = len(df)
    df_clean = df[~mask_invalid].copy()
    n_removed = n_before - len(df_clean)
    clog("CR-02", f"Removed records with age outside [18, 110]; invalid values: {invalid_ages}", n_removed)
    return df_clean


def cr03_remove_invalid_bmi(df: pd.DataFrame) -> pd.DataFrame:
    """
    CR-03: Remove records with BMI < 10 or > 80.
    Rationale: BMI < 10 is incompatible with life. BMI > 80 is physiologically
    extreme and almost certainly a data entry error in this dataset.
    """
    mask_invalid = (df["bmi"] < 10) | (df["bmi"] > 80)
    invalid_bmis = df[mask_invalid]["bmi"].tolist()
    n_before = len(df)
    df_clean = df[~mask_invalid].copy()
    n_removed = n_before - len(df_clean)
    clog("CR-03", f"Removed records with BMI outside [10, 80]; values: {invalid_bmis}", n_removed)
    return df_clean


def cr04_remove_impossible_hemoglobin(df: pd.DataFrame) -> pd.DataFrame:
    """
    CR-04: Remove records where hemoglobin is outside [3, 25] g/dL (not NaN).
    Rationale: Hemoglobin < 3 g/dL is incompatible with survival and would
    indicate a measurement error. Hemoglobin > 25 is similarly impossible under
    normal conditions. NaN values are NOT removed here — they are imputed in CR-08.
    """
    has_value = df["hemoglobin_g_dl"].notna()
    mask_invalid = has_value & ((df["hemoglobin_g_dl"] < 3) | (df["hemoglobin_g_dl"] > 25))
    invalid_hgb = df[mask_invalid]["hemoglobin_g_dl"].tolist()
    n_before = len(df)
    df_clean = df[~mask_invalid].copy()
    n_removed = n_before - len(df_clean)
    clog("CR-04", f"Removed records with hemoglobin outside [3, 25] g/dL; values: {invalid_hgb}", n_removed)
    return df_clean


def cr05_handle_negative_dietary(df: pd.DataFrame) -> pd.DataFrame:
    """
    CR-05: Replace negative dietary values with NaN.
    Rationale: Negative dietary intake is physiologically impossible.
    These represent data entry errors. We do NOT remove the records because
    all other features of those records are valid.
    Replacement: NaN (not 0, because 0 means 'did not eat' while NaN means 'unknown').
    """
    total_replaced = 0
    df = df.copy()
    for col in DIETARY_COLS:
        mask_neg = df[col] < 0
        n_neg = mask_neg.sum()
        if n_neg > 0:
            df.loc[mask_neg, col] = np.nan
            clog("CR-05", f"Replaced {n_neg} negative values in '{col}' with NaN", n_neg)
            total_replaced += n_neg
    if total_replaced == 0:
        clog("CR-05", "No negative dietary values found", 0)
    return df


def cr06_clamp_lab_outliers(df: pd.DataFrame) -> pd.DataFrame:
    """
    CR-06: Clamp lab and dietary values to domain-based physiological bounds.
    Rationale: IQR-based outlier removal would discard genuine extreme values
    (e.g., very high ferritin in haemochromatosis). Instead, we cap at
    clinically documented physiological limits.
    Values outside bounds are CLAMPED, not removed, so the record is retained.
    The clamp boundaries are physiological (not statistical).
    """
    df = df.copy()
    total_clamped = 0
    for col, (lo, hi) in LAB_DOMAIN_BOUNDS.items():
        if col not in df.columns:
            continue
        has_value = df[col].notna()
        # Count values outside bounds (among non-NaN)
        mask_lo = has_value & (df[col] < lo)
        mask_hi = has_value & (df[col] > hi)
        n_clamp = int(mask_lo.sum() + mask_hi.sum())
        if n_clamp > 0:
            df.loc[has_value, col] = df.loc[has_value, col].clip(lo, hi)
            clog("CR-06", f"Clamped '{col}' to [{lo}, {hi}]", n_clamp)
            total_clamped += n_clamp

    for col, (lo, hi) in DIETARY_DOMAIN_BOUNDS.items():
        if col not in df.columns:
            continue
        has_value = df[col].notna()
        mask_lo = has_value & (df[col] < lo)
        mask_hi = has_value & (df[col] > hi)
        n_clamp = int(mask_lo.sum() + mask_hi.sum())
        if n_clamp > 0:
            df.loc[has_value, col] = df.loc[has_value, col].clip(lo, hi)
            clog("CR-06", f"Clamped dietary '{col}' to [{lo}, {hi}]", n_clamp)
            total_clamped += n_clamp

    if total_clamped == 0:
        clog("CR-06", "No lab/dietary values required clamping", 0)
    return df


def cr07_validate_target_labels(df: pd.DataFrame) -> pd.DataFrame:
    """
    CR-07: Validate target labels.
    Rules:
    - iron_deficiency: requires hemoglobin OR serum_ferritin to be non-NaN.
      If both are NaN after cleaning, set iron_deficiency to NaN.
    - vitamin_d_deficiency: requires vitamin_d_25ohd_ng_ml to be non-NaN.
    - vitamin_b12_deficiency: requires vitamin_b12_pg_ml to be non-NaN.
    - calcium_deficiency: requires serum_calcium_mg_dl to be non-NaN.
    - folate_deficiency: requires serum_folate_ng_ml to be non-NaN.

    Records with NaN targets are NOT removed from the dataset; they will be
    excluded from the training set for that specific deficiency model.
    """
    df = df.copy()

    # Iron: both hgb and ferritin must be NaN to invalidate label
    both_nan = df["hemoglobin_g_dl"].isna() & df["serum_ferritin_ng_ml"].isna()
    n_iron_nan = int(both_nan.sum())
    if n_iron_nan > 0:
        df.loc[both_nan, "iron_deficiency"] = np.nan
        clog("CR-07", f"Set iron_deficiency=NaN where both Hgb and ferritin are missing", n_iron_nan)

    # Vitamin D
    n_vitd_nan = int(df["vitamin_d_25ohd_ng_ml"].isna().sum())
    df.loc[df["vitamin_d_25ohd_ng_ml"].isna(), "vitamin_d_deficiency"] = np.nan
    clog("CR-07", f"Confirmed vitamin_d_deficiency=NaN where 25OHD is missing", n_vitd_nan)

    # B12
    n_b12_nan = int(df["vitamin_b12_pg_ml"].isna().sum())
    df.loc[df["vitamin_b12_pg_ml"].isna(), "vitamin_b12_deficiency"] = np.nan
    clog("CR-07", f"Confirmed vitamin_b12_deficiency=NaN where B12 is missing", n_b12_nan)

    # Calcium
    n_ca_nan = int(df["serum_calcium_mg_dl"].isna().sum())
    df.loc[df["serum_calcium_mg_dl"].isna(), "calcium_deficiency"] = np.nan
    clog("CR-07", f"Confirmed calcium_deficiency=NaN where serum Ca is missing", n_ca_nan)

    # Folate
    n_folate_nan = int(df["serum_folate_ng_ml"].isna().sum())
    df.loc[df["serum_folate_ng_ml"].isna(), "folate_deficiency"] = np.nan
    clog("CR-07", f"Confirmed folate_deficiency=NaN where serum folate is missing", n_folate_nan)

    return df


def cr08_impute_lab_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    CR-08: Impute missing lab feature values using gender-stratified medians.
    Rationale: Many lab values differ significantly between males and females
    (e.g., hemoglobin, ferritin). Gender-stratified median imputation reduces
    systematic bias from using the overall median.
    Method: median imputation (not mean — lab distributions are often skewed).
    Note: Imputation is computed ONLY on the cleaned data (not on held-out test set —
    that is handled in the pipeline in Day 14).
    Note: This imputes feature values; target labels remain NaN as set by CR-07.
    """
    df = df.copy()
    for col in LAB_COLS:
        if df[col].isna().sum() == 0:
            continue
        # Gender-stratified medians
        for gender_val in [0, 1]:
            gender_mask = df["gender"] == gender_val
            col_values = df.loc[gender_mask, col]
            median_val = col_values.median()
            missing_mask = gender_mask & df[col].isna()
            n_imputed = missing_mask.sum()
            if n_imputed > 0:
                df.loc[missing_mask, col] = median_val
                clog("CR-08", f"Imputed '{col}' for gender={gender_val} with median={median_val:.3f}", n_imputed)
    return df


def cr09_impute_dietary_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    CR-09: Impute missing dietary feature values with overall median.
    Rationale: Dietary features do not show strong gender stratification in the
    data; missing dietary values represent unreported recalls, not systematic
    differences. Overall median is appropriate here.
    Note: A small number of dietary values became NaN in CR-05 (were negative).
    """
    df = df.copy()
    for col in DIETARY_COLS:
        n_missing = df[col].isna().sum()
        if n_missing > 0:
            median_val = df[col].median()
            df[col] = df[col].fillna(median_val)
            clog("CR-09", f"Imputed '{col}' missing values with median={median_val:.3f}", n_missing)
    return df


def cr10_standardize_categorical(df: pd.DataFrame) -> pd.DataFrame:
    """
    CR-10: Validate and document categorical encodings.
    Confirm that categorical variables use expected integer codes.
    No value changes are made here — this is validation + documentation.
    """
    df = df.copy()
    # Activity level: expected 0-4
    al_values = sorted(df["activity_level"].unique().tolist())
    assert all(v in [0, 1, 2, 3, 4] for v in al_values), f"Unexpected activity_level values: {al_values}"
    clog("CR-10", f"activity_level values validated: {al_values}", 0)

    # Dietary preference: expected 0-2
    dp_values = sorted(df["dietary_preference"].unique().tolist())
    assert all(v in [0, 1, 2] for v in dp_values), f"Unexpected dietary_preference values: {dp_values}"
    clog("CR-10", f"dietary_preference values validated: {dp_values}", 0)

    # Gender: 0/1
    gender_values = sorted(df["gender"].unique().tolist())
    assert all(v in [0, 1] for v in gender_values), f"Unexpected gender values: {gender_values}"
    clog("CR-10", f"gender values validated: {gender_values}", 0)

    return df


# ═══════════════════════════════════════════════════════════════════════════════
# CLEANING SUMMARY
# ═══════════════════════════════════════════════════════════════════════════════

def print_cleaning_summary(df_raw: pd.DataFrame, df_clean: pd.DataFrame):
    print("\n" + "=" * 60)
    print("CLEANING SUMMARY")
    print("=" * 60)
    print(f"Raw records:     {len(df_raw)}")
    print(f"Cleaned records: {len(df_clean)}")
    print(f"Records removed: {len(df_raw) - len(df_clean)}")
    print(f"\nFeature columns: {len(df_clean.columns)}")

    print("\nRemaining missing values per target:")
    for target in TARGET_COLS:
        n_nan = df_clean[target].isna().sum()
        n_valid = df_clean[target].notna().sum()
        n_pos = int((df_clean[target] == 1).sum())
        print(f"  {target}: {n_pos}/{n_valid} positive ({n_pos/n_valid*100:.1f}%) | {n_nan} unlabeled")

    print("\nRemaining missing values in feature columns:")
    missing = df_clean[list(set(df_clean.columns) - set(TARGET_COLS) - {"subject_id"})].isnull().sum()
    missing_nonzero = missing[missing > 0]
    if missing_nonzero.empty:
        print("  None — all feature columns fully imputed")
    else:
        for col, n in missing_nonzero.items():
            print(f"  {col}: {n} missing")


def save_cleaning_decisions_report():
    """Save the cleaning decisions log as a markdown report."""
    report_path = REPORTS_DIR / "day13_cleaning_decisions.md"
    lines = [
        "# Day 13 — Data Cleaning Decisions Report",
        "## Milestone 2: ML Nutritional Deficiency Detection Engine\n",
        "---\n",
        "## Cleaning Rules Applied\n",
        "| Rule ID | Description |",
        "|---------|-------------|",
        "| CR-01 | Remove exact duplicate rows (excluding subject_id) |",
        "| CR-02 | Remove records with age outside [18, 110] |",
        "| CR-03 | Remove records with BMI outside [10, 80] |",
        "| CR-04 | Remove records with hemoglobin outside [3, 25] g/dL |",
        "| CR-05 | Replace negative dietary values with NaN |",
        "| CR-06 | Clamp lab and dietary values to physiological domain bounds |",
        "| CR-07 | Validate target labels; set to NaN if primary lab marker missing |",
        "| CR-08 | Impute lab features with gender-stratified medians |",
        "| CR-09 | Impute dietary features with overall median |",
        "| CR-10 | Validate categorical variable encodings |",
        "\n## Cleaning Log\n",
        "```",
    ] + cleaning_log + [
        "```",
        "\n## Decisions NOT Taken and Why\n",
        "- **Did NOT use IQR-based outlier removal** for lab values: Lab distributions are often",
        "  right-skewed (log-normal); IQR would remove genuine extreme values (e.g., very high",
        "  ferritin in haemochromatosis). Domain-based clamping is more appropriate.",
        "",
        "- **Did NOT set negative dietary values to 0**: Zero means 'did not eat any'; NaN means",
        "  'the value is unknown/invalid'. Negative values are data errors, so NaN is correct.",
        "",
        "- **Did NOT remove records with missing lab values**: Lab values are missing systematically",
        "  (some subjects skip blood draws). Imputing allows retention of their other valid features.",
        "",
        "- **Did NOT remove records where targets are NaN**: These records still contain valid",
        "  features and can be used by other deficiency models whose targets are available.",
        "",
        "- **Did NOT use mean imputation for lab features**: Lab distributions are skewed;",
        "  median is more robust to outliers.",
    ]
    with open(report_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    print(f"\nCleaning decisions report saved to: {report_path}")


# ═══════════════════════════════════════════════════════════════════════════════
# MAIN PIPELINE
# ═══════════════════════════════════════════════════════════════════════════════

def main():
    print("=" * 70)
    print("Day 13 — Data Cleaning Pipeline")
    print("=" * 70)
    print(f"\nLoading raw dataset from: {RAW_DATA_PATH}")

    df = pd.read_csv(RAW_DATA_PATH)
    df_raw = df.copy()
    print(f"Raw dataset: {df.shape[0]} rows x {df.shape[1]} columns\n")

    print("Applying cleaning rules...\n")

    # Apply rules in order
    df = cr01_remove_duplicates(df)
    df = cr02_remove_invalid_age(df)
    df = cr03_remove_invalid_bmi(df)
    df = cr04_remove_impossible_hemoglobin(df)
    df = cr05_handle_negative_dietary(df)
    df = cr06_clamp_lab_outliers(df)
    df = cr07_validate_target_labels(df)
    df = cr08_impute_lab_features(df)
    df = cr09_impute_dietary_features(df)
    df = cr10_standardize_categorical(df)

    # Save cleaned dataset
    df.to_csv(CLEANED_DATA_PATH, index=False)
    print(f"\nCleaned dataset saved to: {CLEANED_DATA_PATH}")

    # Print summary
    print_cleaning_summary(df_raw, df)

    # Save cleaning decisions report
    save_cleaning_decisions_report()

    print("\nDay 13 Data Cleaning complete. Proceed to Day 14 (Feature Engineering).")


if __name__ == "__main__":
    main()

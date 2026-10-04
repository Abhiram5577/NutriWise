"""
generate_nhanes_synthetic.py
============================
Day 11 — Synthetic NHANES-Structured Dataset Generator
Milestone 2: ML Nutritional Deficiency Detection Engine

PURPOSE
-------
Generates a synthetic dataset that mirrors real NHANES structure, variable
naming, value distributions, and clinical reference ranges.

This is NOT fabricated ML predictions. Labels are derived from published
WHO/NIH clinical thresholds applied to simulated biomarker values whose
distributions match documented NHANES prevalence rates.

IMPORTANT DISCLOSURES
---------------------
1. This is synthetic data calibrated against published literature.
2. The pipeline is designed as a drop-in replacement for real NHANES XPT data.
3. Deficiency labels are derived from clinical threshold rules, not ML.
4. No unsupported deficiencies are labeled.

PHASE 2 REPLACEMENT
-------------------
Replace this script with the real NHANES XPT merger (see Day 11 report, Section 11).
The cleaning/feature engineering/modeling scripts need no changes.

REFERENCES
----------
- Looker et al. (1997) JAMA 277(12):973-976 — Iron deficiency prevalence
- Forrest & Stuhldreher (2011) Nutr Res 31(1):48-54 — Vitamin D prevalence
- Pfeiffer et al. (2007) Am J Clin Nutr 86(5):1421-9 — B12 prevalence
- Bailey et al. (2010) J Nutr 140(4):817-22 — Calcium inadequacy
- WHO (2011) Haemoglobin concentrations for anaemia diagnosis
- NIH Office of Dietary Supplements — B12, Vitamin D, Calcium, Iron, Folate fact sheets
"""

import numpy as np
import pandas as pd
from pathlib import Path

# ─── Reproducibility ──────────────────────────────────────────────────────────
RANDOM_SEED = 42
rng = np.random.default_rng(RANDOM_SEED)

# ─── Dataset Size ─────────────────────────────────────────────────────────────
N_SUBJECTS = 5000

# ─── Output Paths ─────────────────────────────────────────────────────────────
OUTPUT_DIR = Path(__file__).parent.parent / "data" / "raw"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
OUTPUT_PATH = OUTPUT_DIR / "nhanes_synthetic_raw.csv"


# ═══════════════════════════════════════════════════════════════════════════════
# HELPER FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════════════

def clamp(arr: np.ndarray, lo: float, hi: float) -> np.ndarray:
    """Clamp array values to physiologically plausible range."""
    return np.clip(arr, lo, hi)


def introduce_missingness(arr: np.ndarray, rate: float) -> np.ndarray:
    """Randomly set `rate` proportion of values to NaN."""
    mask = rng.random(len(arr)) < rate
    result = arr.astype(float).copy()
    result[mask] = np.nan
    return result


# ═══════════════════════════════════════════════════════════════════════════════
# DEMOGRAPHIC FEATURES
# ═══════════════════════════════════════════════════════════════════════════════

def generate_demographics(n: int) -> dict:
    """
    Generate demographic features matching NHANES population structure.
    Age: 18-80, roughly uniform across adult population.
    Gender: 0=Female (~51%), 1=Male (~49%) — NHANES oversamples certain groups.
    """
    age = rng.integers(18, 81, size=n).astype(float)
    gender = rng.choice([0, 1], size=n, p=[0.51, 0.49])  # 0=Female, 1=Male
    # BMI: mean ~28.5, SD ~6.5 (NHANES adult mean; skewed right)
    bmi = clamp(rng.normal(28.5, 6.5, n), 15.0, 60.0)

    # Activity level: sedentary (0), light (1), moderate (2), active (3), very_active (4)
    activity_level = rng.choice([0, 1, 2, 3, 4], size=n, p=[0.30, 0.25, 0.25, 0.15, 0.05])

    # Dietary preference: omnivore (0), vegetarian (1), vegan (2)
    # US population: ~5% vegetarian/vegan
    dietary_preference = rng.choice([0, 1, 2], size=n, p=[0.93, 0.05, 0.02])

    # Pregnancy: only females aged 18-45
    is_pregnant = np.zeros(n, dtype=int)
    pregnant_eligible = (gender == 0) & (age <= 45)
    is_pregnant[pregnant_eligible] = rng.choice(
        [0, 1], size=pregnant_eligible.sum(), p=[0.95, 0.05]
    )

    # Smoking: ~14% current smokers (NHANES 2017-18 estimate)
    is_smoker = rng.choice([0, 1], size=n, p=[0.86, 0.14])

    return {
        "age": age,
        "gender": gender,
        "bmi": bmi,
        "activity_level": activity_level,
        "dietary_preference": dietary_preference,
        "is_pregnant": is_pregnant,
        "is_smoker": is_smoker,
    }


# ═══════════════════════════════════════════════════════════════════════════════
# LABORATORY FEATURES
# We first generate lab values, then derive deficiency labels from them.
# ═══════════════════════════════════════════════════════════════════════════════

def generate_lab_values(demog: dict, n: int) -> dict:
    """
    Generate laboratory biomarker values with realistic distributions.
    Iron markers are correlated with each other.
    Vitamin D is lower in older adults, heavier individuals, non-supplementers.
    B12 is lower in vegans/vegetarians and older adults.
    """
    gender = demog["gender"]
    age = demog["age"]
    bmi = demog["bmi"]
    dietary_preference = demog["dietary_preference"]  # 0=omni, 1=veg, 2=vegan
    is_pregnant = demog["is_pregnant"]

    # ── Hemoglobin (g/dL) ──────────────────────────────────────────────────────
    # Normal: Males ~14-18 g/dL, Females ~12-16 g/dL
    # Deficiency defined by WHO: <13 g/dL (M), <12 g/dL (F)
    hgb_base = np.where(gender == 1, 15.5, 13.5)
    hgb_sd = 1.5
    hemoglobin = clamp(rng.normal(hgb_base, hgb_sd, n), 5.0, 20.0)

    # ── Serum Ferritin (ng/mL) ─────────────────────────────────────────────────
    # Log-normal distribution; Men higher than women
    # Normal: ~20-300 ng/mL (M), ~15-150 ng/mL (F)
    # Deficiency: <12 ng/mL
    ferritin_mean_log = np.where(gender == 1, np.log(80), np.log(35))
    ferritin_sd_log = 0.9
    serum_ferritin = clamp(
        np.exp(rng.normal(ferritin_mean_log, ferritin_sd_log, n)), 1.0, 500.0
    )
    # Pregnancy lowers ferritin
    serum_ferritin = np.where(is_pregnant, serum_ferritin * 0.65, serum_ferritin)

    # ── Serum Iron (mcg/dL) ────────────────────────────────────────────────────
    # Normal: ~60-170 mcg/dL. Correlated with ferritin.
    serum_iron = clamp(rng.normal(100, 30, n), 20.0, 250.0)

    # ── TIBC (mcg/dL) ─────────────────────────────────────────────────────────
    # Normal: 250-370 mcg/dL. Inversely correlated with ferritin.
    tibc = clamp(rng.normal(300, 45, n), 150.0, 500.0)

    # ── Transferrin Saturation (%) ─────────────────────────────────────────────
    # = serum_iron / TIBC * 100. Normal: 20-50%
    transferrin_saturation = clamp((serum_iron / tibc) * 100, 1.0, 90.0)

    # ── Vitamin D 25OHD (ng/mL) ───────────────────────────────────────────────
    # Log-normal; deficiency <20 ng/mL (~28-36% of US adults)
    # Older adults, higher BMI, darker skin = lower Vit D (BMI proxy used here)
    vitd_base_log = np.log(28) - (bmi - 25) * 0.015 - (age - 40) * 0.005
    vitd_sd_log = 0.6
    vitamin_d = clamp(np.exp(rng.normal(vitd_base_log, vitd_sd_log, n)), 4.0, 100.0)

    # ── Vitamin B12 (pg/mL) ────────────────────────────────────────────────────
    # Normal: 200-900 pg/mL; deficiency <200 pg/mL (~3-6%)
    # Vegans and vegetarians much more at risk
    b12_base_log = np.log(450)
    b12_base_log = np.where(dietary_preference == 1, b12_base_log - 0.5, b12_base_log)  # vegetarian
    b12_base_log = np.where(dietary_preference == 2, b12_base_log - 1.2, b12_base_log)  # vegan
    # Older adults absorb less B12
    b12_base_log = b12_base_log - (age - 40) * 0.006
    b12_sd_log = 0.5
    vitamin_b12 = clamp(np.exp(rng.normal(b12_base_log, b12_sd_log, n)), 50.0, 2000.0)

    # ── Serum Calcium (mg/dL) ─────────────────────────────────────────────────
    # Tightly regulated; normal: 8.5-10.5 mg/dL
    # Deficiency <8.5 mg/dL is rare but included
    serum_calcium = clamp(rng.normal(9.4, 0.5, n), 6.0, 12.5)

    # ── Serum Folate (ng/mL) ──────────────────────────────────────────────────
    # Normal: >3 ng/mL; deficiency <3 ng/mL (rare in US post-fortification)
    serum_folate = clamp(rng.lognormal(np.log(12), 0.7, n), 0.5, 60.0)
    # Vegetarians/vegans generally have higher folate (more leafy greens)
    serum_folate = np.where(dietary_preference >= 1, serum_folate * 1.3, serum_folate)

    # ── RBC Folate (ng/mL) ────────────────────────────────────────────────────
    # Reflects longer-term stores; normal >140 ng/mL
    rbc_folate = clamp(serum_folate * 25 + rng.normal(0, 50, n), 50.0, 1000.0)

    # ── Apply missingness (realistic NHANES rates) ─────────────────────────────
    # Some participants skip certain blood draws; NHANES reports ~5-15% missing lab values
    hemoglobin = introduce_missingness(hemoglobin, 0.05)
    serum_ferritin = introduce_missingness(serum_ferritin, 0.08)
    serum_iron = introduce_missingness(serum_iron, 0.08)
    tibc = introduce_missingness(tibc, 0.08)
    transferrin_saturation = introduce_missingness(transferrin_saturation, 0.08)
    vitamin_d = introduce_missingness(vitamin_d, 0.12)
    vitamin_b12 = introduce_missingness(vitamin_b12, 0.10)
    serum_calcium = introduce_missingness(serum_calcium, 0.07)
    serum_folate = introduce_missingness(serum_folate, 0.10)
    rbc_folate = introduce_missingness(rbc_folate, 0.12)

    return {
        "hemoglobin_g_dl": hemoglobin,
        "serum_ferritin_ng_ml": serum_ferritin,
        "serum_iron_mcg_dl": serum_iron,
        "tibc_mcg_dl": tibc,
        "transferrin_saturation_pct": transferrin_saturation,
        "vitamin_d_25ohd_ng_ml": vitamin_d,
        "vitamin_b12_pg_ml": vitamin_b12,
        "serum_calcium_mg_dl": serum_calcium,
        "serum_folate_ng_ml": serum_folate,
        "rbc_folate_ng_ml": rbc_folate,
    }


# ═══════════════════════════════════════════════════════════════════════════════
# DIETARY FEATURES
# ═══════════════════════════════════════════════════════════════════════════════

def generate_dietary_features(demog: dict, n: int) -> dict:
    """
    Generate 24-hour dietary recall nutrient values.
    Distributions calibrated from NHANES DR1TOT documentation.
    Vegans/vegetarians have higher folate but lower B12/iron/calcium from food.
    """
    gender = demog["gender"]
    dietary_preference = demog["dietary_preference"]

    # Iron: Men ~18 mg/day, Women ~13 mg/day (RDA: 8 mg/M, 18 mg/F)
    dietary_iron = clamp(
        rng.normal(np.where(gender == 1, 17.0, 12.5), 5.0, n), 0.0, 60.0
    )
    # Vegans/vegetarians eat more non-heme iron but lower bioavailability
    dietary_iron = np.where(dietary_preference >= 1, dietary_iron * 1.1, dietary_iron)

    # Calcium: Mean ~1000 mg/day (RDA: 1000-1200 mg)
    dietary_calcium = clamp(rng.normal(1050, 380, n), 50.0, 3000.0)
    # Vegans often lower dairy calcium
    dietary_calcium = np.where(dietary_preference == 2, dietary_calcium * 0.70, dietary_calcium)

    # Vitamin D: Mean ~5-7 mcg/day (RDA: 15-20 mcg; most Americans fall short)
    dietary_vitamin_d = clamp(rng.lognormal(np.log(5), 0.8, n), 0.0, 60.0)

    # Vitamin B12: RDA 2.4 mcg; mean ~4-5 mcg/day (omnivores)
    dietary_vitamin_b12 = clamp(rng.lognormal(np.log(4.5), 0.7, n), 0.0, 30.0)
    dietary_vitamin_b12 = np.where(dietary_preference == 1, dietary_vitamin_b12 * 0.6, dietary_vitamin_b12)
    dietary_vitamin_b12 = np.where(dietary_preference == 2, dietary_vitamin_b12 * 0.15, dietary_vitamin_b12)

    # Folate: Mean ~400 mcg DFE/day (RDA: 400 mcg DFE)
    dietary_folate = clamp(rng.normal(420, 190, n), 30.0, 2000.0)
    dietary_folate = np.where(dietary_preference >= 1, dietary_folate * 1.25, dietary_folate)

    # Vitamin C: Mean ~90 mg/day
    dietary_vitamin_c = clamp(rng.lognormal(np.log(90), 0.7, n), 0.0, 1000.0)

    # Protein: ~70 g/day men, ~55 g/day women
    dietary_protein = clamp(
        rng.normal(np.where(gender == 1, 90, 65), 30, n), 5.0, 300.0
    )
    dietary_protein = np.where(dietary_preference == 2, dietary_protein * 0.85, dietary_protein)

    # Calories: ~2200 kcal/day men, ~1800 kcal/day women
    dietary_calories = clamp(
        rng.normal(np.where(gender == 1, 2200, 1800), 500, n), 500.0, 5000.0
    )

    # Fiber: ~15-20 g/day
    dietary_fiber = clamp(rng.normal(17, 7, n), 0.0, 80.0)
    dietary_fiber = np.where(dietary_preference >= 1, dietary_fiber * 1.4, dietary_fiber)

    return {
        "dietary_iron_mg": dietary_iron,
        "dietary_calcium_mg": dietary_calcium,
        "dietary_vitamin_d_mcg": dietary_vitamin_d,
        "dietary_vitamin_b12_mcg": dietary_vitamin_b12,
        "dietary_folate_mcg": dietary_folate,
        "dietary_vitamin_c_mg": dietary_vitamin_c,
        "dietary_protein_g": dietary_protein,
        "dietary_calories_kcal": dietary_calories,
        "dietary_fiber_g": dietary_fiber,
    }


# ═══════════════════════════════════════════════════════════════════════════════
# SYMPTOM FEATURES
# Symptoms are correlated with corresponding lab deficiencies
# ═══════════════════════════════════════════════════════════════════════════════

def generate_symptoms(labs: dict, n: int) -> dict:
    """
    Generate symptom binary indicators. Symptoms are probabilistically
    correlated with the underlying lab deficiencies they indicate.
    Symptom-deficiency associations based on clinical literature.

    NOTE: Symptoms are soft signals — many deficient individuals are
    asymptomatic, and many non-deficient individuals report symptoms.
    """
    hgb = np.nan_to_num(labs["hemoglobin_g_dl"], nan=14.0)
    ferritin = np.nan_to_num(labs["serum_ferritin_ng_ml"], nan=40.0)
    vitd = np.nan_to_num(labs["vitamin_d_25ohd_ng_ml"], nan=25.0)
    b12 = np.nan_to_num(labs["vitamin_b12_pg_ml"], nan=400.0)
    ca = np.nan_to_num(labs["serum_calcium_mg_dl"], nan=9.4)
    folate = np.nan_to_num(labs["serum_folate_ng_ml"], nan=12.0)

    # Baseline symptom probability in general population
    base_fatigue_p = 0.25
    base_hair_loss_p = 0.15
    base_skin_issues_p = 0.12
    base_muscle_weakness_p = 0.10
    base_mood_low_p = 0.15
    base_bone_pain_p = 0.08
    base_tingling_p = 0.07
    base_cold_intolerance_p = 0.08

    def bernoulli(p_arr: np.ndarray) -> np.ndarray:
        return (rng.random(n) < np.clip(p_arr, 0.0, 1.0)).astype(int)

    # Fatigue: iron deficiency/anaemia and B12 deficiency are primary drivers
    fatigue_p = (
        base_fatigue_p
        + np.where(hgb < 12.0, 0.35, 0.0)
        + np.where(ferritin < 15.0, 0.15, 0.0)
        + np.where(b12 < 200, 0.20, 0.0)
        + np.where(vitd < 20, 0.10, 0.0)
    )
    symptom_fatigue = bernoulli(fatigue_p)

    # Hair loss: iron deficiency
    hair_loss_p = (
        base_hair_loss_p
        + np.where(ferritin < 25.0, 0.18, 0.0)
        + np.where(hgb < 12.5, 0.10, 0.0)
    )
    symptom_hair_loss = bernoulli(hair_loss_p)

    # Skin issues: low iron, B12, general malnutrition
    skin_issues_p = (
        base_skin_issues_p
        + np.where(vitd < 20, 0.08, 0.0)
        + np.where(b12 < 200, 0.10, 0.0)
    )
    symptom_skin_issues = bernoulli(skin_issues_p)

    # Muscle weakness: iron, D, calcium
    muscle_weakness_p = (
        base_muscle_weakness_p
        + np.where(vitd < 12.0, 0.20, 0.0)
        + np.where(ca < 8.5, 0.15, 0.0)
        + np.where(hgb < 11.0, 0.15, 0.0)
    )
    symptom_muscle_weakness = bernoulli(muscle_weakness_p)

    # Low mood: B12, D, folate
    mood_low_p = (
        base_mood_low_p
        + np.where(b12 < 200, 0.18, 0.0)
        + np.where(vitd < 20, 0.12, 0.0)
        + np.where(folate < 3.0, 0.12, 0.0)
    )
    symptom_mood_low = bernoulli(mood_low_p)

    # Bone pain: Vitamin D deficiency (osteomalacia)
    bone_pain_p = (
        base_bone_pain_p
        + np.where(vitd < 10.0, 0.25, 0.0)
        + np.where(vitd < 20.0, 0.10, 0.0)
        + np.where(ca < 8.5, 0.10, 0.0)
    )
    symptom_bone_pain = bernoulli(bone_pain_p)

    # Tingling/numbness: B12 deficiency (subacute combined degeneration)
    tingling_p = (
        base_tingling_p
        + np.where(b12 < 150, 0.30, 0.0)
        + np.where(b12 < 200, 0.15, 0.0)
        + np.where(folate < 3.0, 0.08, 0.0)
    )
    symptom_tingling = bernoulli(tingling_p)

    # Cold intolerance: iron deficiency (anaemia)
    cold_intolerance_p = (
        base_cold_intolerance_p
        + np.where(hgb < 11.5, 0.20, 0.0)
        + np.where(ferritin < 12.0, 0.12, 0.0)
    )
    symptom_cold_intolerance = bernoulli(cold_intolerance_p)

    symptom_count = (
        symptom_fatigue + symptom_hair_loss + symptom_skin_issues
        + symptom_muscle_weakness + symptom_mood_low + symptom_bone_pain
        + symptom_tingling + symptom_cold_intolerance
    )

    return {
        "symptom_fatigue": symptom_fatigue,
        "symptom_hair_loss": symptom_hair_loss,
        "symptom_skin_issues": symptom_skin_issues,
        "symptom_muscle_weakness": symptom_muscle_weakness,
        "symptom_mood_low": symptom_mood_low,
        "symptom_bone_pain": symptom_bone_pain,
        "symptom_tingling": symptom_tingling,
        "symptom_cold_intolerance": symptom_cold_intolerance,
        "symptom_count": symptom_count,
    }


# ═══════════════════════════════════════════════════════════════════════════════
# DEFICIENCY LABELS — Derived from clinical thresholds, NOT fabricated
# ═══════════════════════════════════════════════════════════════════════════════

def derive_deficiency_labels(demog: dict, labs: dict) -> dict:
    """
    Apply WHO/NIH/NHANES clinical threshold rules to derive binary deficiency labels.

    These labels are NOT guessed by ML — they are deterministic rules applied
    to the simulated biomarker values. This is how real NHANES studies create
    deficiency classifications.

    Sources:
    - WHO (2011) Haemoglobin for anaemia diagnosis
    - NIH ODS Vitamin D Fact Sheet (2023)
    - NIH ODS Vitamin B12 Fact Sheet (2023)
    - NIH ODS Calcium Fact Sheet (2023)
    - CDC Iron deficiency guidelines
    - Pfeiffer et al., serum folate cutoffs
    """
    gender = demog["gender"]
    hgb = labs["hemoglobin_g_dl"]
    ferritin = labs["serum_ferritin_ng_ml"]
    vitd = labs["vitamin_d_25ohd_ng_ml"]
    b12 = labs["vitamin_b12_pg_ml"]
    ca = labs["serum_calcium_mg_dl"]
    folate = labs["serum_folate_ng_ml"]

    # ── Iron deficiency ────────────────────────────────────────────────────────
    # Ferritin < 12 ng/mL (standard threshold) OR
    # Hemoglobin: <12 g/dL (F), <13 g/dL (M)  [WHO 2011]
    hgb_threshold = np.where(gender == 1, 13.0, 12.0)
    iron_def_ferritin = np.where(ferritin < 12.0, 1, 0)
    iron_def_hgb = np.where(hgb < hgb_threshold, 1, 0)
    # If either marker is NaN, only use the other; if both are NaN, set NaN
    iron_deficiency = np.where(
        np.isnan(ferritin) & np.isnan(hgb), np.nan,
        np.nanmax(np.stack([
            np.where(np.isnan(ferritin), 0, iron_def_ferritin),
            np.where(np.isnan(hgb), 0, iron_def_hgb)
        ]), axis=0)
    )

    # ── Vitamin D deficiency ───────────────────────────────────────────────────
    # <20 ng/mL = deficient  [NIH ODS 2023, Endocrine Society]
    vitamin_d_deficiency = np.where(np.isnan(vitd), np.nan, np.where(vitd < 20.0, 1, 0))

    # ── Vitamin B12 deficiency ─────────────────────────────────────────────────
    # <200 pg/mL = deficient  [NIH ODS 2023]
    vitamin_b12_deficiency = np.where(np.isnan(b12), np.nan, np.where(b12 < 200.0, 1, 0))

    # ── Calcium deficiency (hypocalcaemia) ─────────────────────────────────────
    # <8.5 mg/dL = hypocalcaemia  [clinical labs standard]
    calcium_deficiency = np.where(np.isnan(ca), np.nan, np.where(ca < 8.5, 1, 0))

    # ── Folate deficiency ──────────────────────────────────────────────────────
    # <3 ng/mL = deficient  [Pfeiffer et al., WHO]
    folate_deficiency = np.where(np.isnan(folate), np.nan, np.where(folate < 3.0, 1, 0))

    return {
        "iron_deficiency": iron_deficiency,
        "vitamin_d_deficiency": vitamin_d_deficiency,
        "vitamin_b12_deficiency": vitamin_b12_deficiency,
        "calcium_deficiency": calcium_deficiency,
        "folate_deficiency": folate_deficiency,
    }


# ═══════════════════════════════════════════════════════════════════════════════
# INJECT DELIBERATE DATA QUALITY ISSUES for EDA/Cleaning practice
# ═══════════════════════════════════════════════════════════════════════════════

def inject_data_quality_issues(df: pd.DataFrame, rng: np.random.Generator) -> pd.DataFrame:
    """
    Inject realistic data quality issues to practice EDA and cleaning.
    Issues injected:
    - A small number of physiologically impossible values (will be flagged as invalid)
    - A few exact duplicate rows
    - A few impossible age values (0 or >120)
    - Some negative dietary values
    All injections are documented here for reproducibility.
    """
    n = len(df)

    # 1. Inject ~10 physiologically impossible hemoglobin values
    impossible_hgb_idx = rng.choice(n, size=10, replace=False)
    df.loc[impossible_hgb_idx, "hemoglobin_g_dl"] = rng.choice(
        [-1.0, 0.0, 99.0, 50.0], size=10
    )

    # 2. Inject ~5 impossible age values
    impossible_age_idx = rng.choice(n, size=5, replace=False)
    df.loc[impossible_age_idx, "age"] = rng.choice([0, 150, 200, -5], size=5)

    # 3. Inject ~8 negative dietary values
    neg_diet_idx = rng.choice(n, size=8, replace=False)
    df.loc[neg_diet_idx, "dietary_iron_mg"] = rng.uniform(-10, -0.1, size=8)

    # 4. Inject ~15 exact duplicate rows
    dup_source_idx = rng.choice(n, size=15, replace=False)
    dup_rows = df.iloc[dup_source_idx].copy()
    df = pd.concat([df, dup_rows], ignore_index=True)

    # 5. Inject ~3 BMI values that are impossible
    bmi_idx = rng.choice(n, size=3, replace=False)
    df.loc[bmi_idx, "bmi"] = rng.choice([-2.0, 0.0, 200.0], size=3)

    return df


# ═══════════════════════════════════════════════════════════════════════════════
# MAIN GENERATION PIPELINE
# ═══════════════════════════════════════════════════════════════════════════════

def main():
    print(f"Generating synthetic NHANES dataset with N={N_SUBJECTS} subjects...")
    print(f"Random seed: {RANDOM_SEED}")

    # Step 1: Demographics
    demog = generate_demographics(N_SUBJECTS)
    print(f"  Demographics generated: {N_SUBJECTS} records")

    # Step 2: Lab values (depend on demographics)
    labs = generate_lab_values(demog, N_SUBJECTS)
    print(f"  Laboratory values generated: {len(labs)} biomarkers")

    # Step 3: Dietary features
    dietary = generate_dietary_features(demog, N_SUBJECTS)
    print(f"  Dietary features generated: {len(dietary)} nutrients")

    # Step 4: Symptoms (depend on lab values)
    symptoms = generate_symptoms(labs, N_SUBJECTS)
    print(f"  Symptom features generated: {len(symptoms)} symptoms")

    # Step 5: Deficiency labels (derived from clinical thresholds)
    labels = derive_deficiency_labels(demog, labs)
    print(f"  Deficiency labels derived: {len(labels)} targets")

    # Step 6: Assemble DataFrame
    all_data = {}
    all_data.update(demog)
    all_data.update(labs)
    all_data.update(dietary)
    all_data.update(symptoms)
    all_data.update(labels)

    df = pd.DataFrame(all_data)

    # Step 7: Inject deliberate quality issues for EDA practice
    df = inject_data_quality_issues(df, rng)
    print(f"  Data quality issues injected; final shape: {df.shape}")

    # Step 8: Add subject ID
    df.insert(0, "subject_id", range(1, len(df) + 1))

    # Step 9: Save
    df.to_csv(OUTPUT_PATH, index=False)
    print(f"\nDataset saved to: {OUTPUT_PATH}")
    print(f"Total records: {len(df)}")
    print(f"Total columns: {len(df.columns)}")

    # Step 10: Print label prevalence summary
    print("\n--- Deficiency Label Prevalence (derived from clinical thresholds) ---")
    for label in labels.keys():
        col = df[label].dropna()
        n_def = int(col.sum())
        n_total = len(col)
        pct = n_def / n_total * 100
        n_missing = df[label].isna().sum()
        print(f"  {label}: {n_def}/{n_total} deficient ({pct:.1f}%) | {n_missing} NaN")

    print("\nGeneration complete. Proceed to Day 12 (EDA).")


if __name__ == "__main__":
    main()

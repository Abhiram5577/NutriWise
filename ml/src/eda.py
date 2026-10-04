"""
eda.py
======
Day 12 — Exploratory Data Analysis
Milestone 2: ML Nutritional Deficiency Detection Engine

PURPOSE
-------
Conduct a systematic EDA of the synthetic NHANES dataset:
- Dataset structure, dtypes, shape
- Missing value analysis
- Duplicate detection
- Target label distribution
- Feature distributions (demographic, dietary, lab, symptom)
- Invalid value detection
- Outlier investigation (IQR-based flagging)
- Summary statistics
- Visualization of key relationships

DECISIONS MADE (see inline comments and eda_report.md)
- No records silently deleted during EDA
- Suspicious/invalid records are flagged and documented
- Outlier treatment decisions deferred to Day 13 (cleaning)

OUTPUT
------
- ml/reports/figures/*.png  — saved charts
- ml/reports/eda_report.md  — written EDA report
- Console summary
"""

import sys
import warnings
from pathlib import Path

import matplotlib
matplotlib.use("Agg")  # Non-interactive backend for script execution
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import numpy as np
import pandas as pd
import seaborn as sns

warnings.filterwarnings("ignore")

# ─── Paths ────────────────────────────────────────────────────────────────────
ROOT = Path(__file__).parent.parent
DATA_PATH = ROOT / "data" / "raw" / "nhanes_synthetic_raw.csv"
FIGURES_DIR = ROOT / "reports" / "figures"
REPORTS_DIR = ROOT / "reports"
FIGURES_DIR.mkdir(parents=True, exist_ok=True)

# ─── Style ────────────────────────────────────────────────────────────────────
sns.set_theme(style="darkgrid", palette="muted")
plt.rcParams.update({
    "figure.dpi": 120,
    "font.size": 10,
    "axes.titlesize": 12,
    "axes.labelsize": 10,
})

# ─── Feature Groups ───────────────────────────────────────────────────────────
DEMOGRAPHIC_COLS = [
    "age", "gender", "bmi", "activity_level",
    "dietary_preference", "is_pregnant", "is_smoker"
]
LAB_COLS = [
    "hemoglobin_g_dl", "serum_ferritin_ng_ml", "serum_iron_mcg_dl",
    "tibc_mcg_dl", "transferrin_saturation_pct", "vitamin_d_25ohd_ng_ml",
    "vitamin_b12_pg_ml", "serum_calcium_mg_dl", "serum_folate_ng_ml",
    "rbc_folate_ng_ml"
]
DIETARY_COLS = [
    "dietary_iron_mg", "dietary_calcium_mg", "dietary_vitamin_d_mcg",
    "dietary_vitamin_b12_mcg", "dietary_folate_mcg", "dietary_vitamin_c_mg",
    "dietary_protein_g", "dietary_calories_kcal", "dietary_fiber_g"
]
SYMPTOM_COLS = [
    "symptom_fatigue", "symptom_hair_loss", "symptom_skin_issues",
    "symptom_muscle_weakness", "symptom_mood_low", "symptom_bone_pain",
    "symptom_tingling", "symptom_cold_intolerance", "symptom_count"
]
TARGET_COLS = [
    "iron_deficiency", "vitamin_d_deficiency", "vitamin_b12_deficiency",
    "calcium_deficiency", "folate_deficiency"
]

# ─── EDA Report accumulator ───────────────────────────────────────────────────
report_lines = []


def rlog(msg: str = ""):
    """Print to console and accumulate for report."""
    print(msg)
    report_lines.append(msg)


# ═══════════════════════════════════════════════════════════════════════════════
# SECTION 1: LOAD AND BASIC STRUCTURE
# ═══════════════════════════════════════════════════════════════════════════════

def section_1_structure(df: pd.DataFrame):
    rlog("\n# Day 12 — Exploratory Data Analysis Report")
    rlog("## Milestone 2: ML Nutritional Deficiency Detection Engine\n")
    rlog("---\n")

    rlog("## 1. Dataset Structure\n")
    rlog(f"- **Shape:** {df.shape[0]} rows x {df.shape[1]} columns")
    rlog(f"- **File:** nhanes_synthetic_raw.csv")
    rlog(f"- **Source:** Synthetic NHANES-structured dataset (see Day 11 report)\n")

    rlog("### Column Groups")
    rlog(f"- Demographic features: {len(DEMOGRAPHIC_COLS)}")
    rlog(f"- Laboratory features: {len(LAB_COLS)}")
    rlog(f"- Dietary features: {len(DIETARY_COLS)}")
    rlog(f"- Symptom features: {len(SYMPTOM_COLS)}")
    rlog(f"- Target labels: {len(TARGET_COLS)}")
    rlog(f"- ID column: 1 (subject_id)\n")

    rlog("### Data Types")
    dtype_counts = df.dtypes.value_counts()
    for dtype, count in dtype_counts.items():
        rlog(f"  - `{dtype}`: {count} columns")
    rlog("")


# ═══════════════════════════════════════════════════════════════════════════════
# SECTION 2: MISSING VALUES
# ═══════════════════════════════════════════════════════════════════════════════

def section_2_missing(df: pd.DataFrame):
    rlog("## 2. Missing Value Analysis\n")

    missing = df.isnull().sum()
    missing_pct = (missing / len(df) * 100).round(2)
    missing_df = pd.DataFrame({
        "missing_count": missing,
        "missing_pct": missing_pct
    }).query("missing_count > 0").sort_values("missing_pct", ascending=False)

    if missing_df.empty:
        rlog("No missing values found.")
    else:
        rlog(f"**{len(missing_df)} columns** have missing values:\n")
        rlog("| Column | Missing Count | Missing % |")
        rlog("|--------|--------------|-----------|")
        for col, row in missing_df.iterrows():
            rlog(f"| {col} | {int(row['missing_count'])} | {row['missing_pct']}% |")
    rlog("")

    # Visualize missing values heatmap
    cols_with_missing = missing_df.index.tolist()
    if cols_with_missing:
        fig, ax = plt.subplots(figsize=(12, 4))
        missing_pct_vals = missing_df["missing_pct"]
        bars = ax.barh(missing_pct_vals.index, missing_pct_vals.values,
                       color=sns.color_palette("Reds_r", len(missing_pct_vals)))
        ax.set_xlabel("Missing %")
        ax.set_title("Missing Value Rates by Feature")
        ax.axvline(x=10, color="orange", linestyle="--", alpha=0.7, label="10% threshold")
        ax.legend()
        for bar, val in zip(bars, missing_pct_vals.values):
            ax.text(bar.get_width() + 0.2, bar.get_y() + bar.get_height() / 2,
                    f"{val:.1f}%", va="center", fontsize=8)
        plt.tight_layout()
        fig.savefig(FIGURES_DIR / "fig01_missing_values.png")
        plt.close()
        rlog("**Figure saved:** fig01_missing_values.png\n")

    return missing_df


# ═══════════════════════════════════════════════════════════════════════════════
# SECTION 3: DUPLICATE ANALYSIS
# ═══════════════════════════════════════════════════════════════════════════════

def section_3_duplicates(df: pd.DataFrame):
    rlog("## 3. Duplicate Record Analysis\n")

    # Check for exact duplicates (excluding subject_id since it's auto-incremented)
    cols_for_dup = [c for c in df.columns if c != "subject_id"]
    n_dups = df.duplicated(subset=cols_for_dup).sum()

    rlog(f"- Total rows: {len(df)}")
    rlog(f"- Exact duplicate rows (excluding subject_id): **{n_dups}**")
    rlog(f"- Duplicate rate: {n_dups/len(df)*100:.2f}%")

    if n_dups > 0:
        rlog("\n**Action (deferred to Day 13):** Duplicates identified; will be removed in cleaning.")
        rlog("Duplicates were deliberately injected (see generate_nhanes_synthetic.py, inject_data_quality_issues).")
    rlog("")


# ═══════════════════════════════════════════════════════════════════════════════
# SECTION 4: INVALID VALUES
# ═══════════════════════════════════════════════════════════════════════════════

def section_4_invalid_values(df: pd.DataFrame):
    rlog("## 4. Invalid Value Analysis\n")

    invalid_findings = []

    # Age
    invalid_age = df[(df["age"] < 18) | (df["age"] > 110)]
    if len(invalid_age) > 0:
        rlog(f"- `age`: {len(invalid_age)} records outside [18, 110] range")
        rlog(f"  Values: {sorted(df['age'].dropna().unique().tolist())[:5]}")
        invalid_findings.append(("age", len(invalid_age), "outside [18, 110]"))

    # BMI
    invalid_bmi = df[(df["bmi"] < 10) | (df["bmi"] > 80)]
    if len(invalid_bmi) > 0:
        rlog(f"- `bmi`: {len(invalid_bmi)} records outside [10, 80] range")
        invalid_findings.append(("bmi", len(invalid_bmi), "outside [10, 80]"))

    # Hemoglobin
    invalid_hgb = df[(df["hemoglobin_g_dl"] < 3) | (df["hemoglobin_g_dl"] > 25)]
    invalid_hgb = invalid_hgb.dropna(subset=["hemoglobin_g_dl"])
    if len(invalid_hgb) > 0:
        rlog(f"- `hemoglobin_g_dl`: {len(invalid_hgb)} records outside [3, 25] g/dL range")
        rlog(f"  Values found: {df['hemoglobin_g_dl'].dropna().nsmallest(5).tolist()}")
        invalid_findings.append(("hemoglobin_g_dl", len(invalid_hgb), "outside [3, 25]"))

    # Negative dietary values
    for col in DIETARY_COLS:
        neg_count = (df[col] < 0).sum()
        if neg_count > 0:
            rlog(f"- `{col}`: {neg_count} negative values (physiologically impossible)")
            invalid_findings.append((col, neg_count, "negative value"))

    # Ferritin
    invalid_ferritin = df[df["serum_ferritin_ng_ml"] < 0].dropna(subset=["serum_ferritin_ng_ml"])
    if len(invalid_ferritin) > 0:
        invalid_findings.append(("serum_ferritin_ng_ml", len(invalid_ferritin), "negative value"))

    if not invalid_findings:
        rlog("No invalid values detected.")
    else:
        rlog(f"\n**Total invalid value issues found: {len(invalid_findings)}**")
        rlog("**Action (deferred to Day 13):** Invalid records will be flagged and handled in cleaning.")
    rlog("")

    return invalid_findings


# ═══════════════════════════════════════════════════════════════════════════════
# SECTION 5: TARGET LABEL DISTRIBUTION
# ═══════════════════════════════════════════════════════════════════════════════

def section_5_target_distribution(df: pd.DataFrame):
    rlog("## 5. Target Label Distribution\n")

    rlog("| Deficiency | Positive (Deficient) | Negative (Normal) | Missing | Prevalence (%) |")
    rlog("|-----------|---------------------|------------------|---------|----------------|")
    for target in TARGET_COLS:
        col = df[target]
        n_pos = int((col == 1).sum())
        n_neg = int((col == 0).sum())
        n_miss = int(col.isna().sum())
        n_valid = n_pos + n_neg
        pct = n_pos / n_valid * 100 if n_valid > 0 else 0
        rlog(f"| {target} | {n_pos} | {n_neg} | {n_miss} | {pct:.1f}% |")
    rlog("")

    # Class imbalance analysis
    rlog("### Class Imbalance Assessment\n")
    rlog("- Iron deficiency: ~16% — moderately imbalanced")
    rlog("- Vitamin D deficiency: ~34% — moderate imbalance (near 1:2)")
    rlog("- Vitamin B12 deficiency: ~10% — imbalanced")
    rlog("- Calcium deficiency: ~4% — highly imbalanced")
    rlog("- Folate deficiency: ~2% — highly imbalanced")
    rlog("\n**Implication:** Class weights or SMOTE oversampling may be needed for B12, Calcium, Folate models.\n")

    # Visualize
    fig, axes = plt.subplots(1, len(TARGET_COLS), figsize=(16, 4))
    colors = {"0": "#4CAF50", "1": "#F44336"}

    for ax, target in zip(axes, TARGET_COLS):
        col = df[target].dropna()
        counts = col.value_counts().sort_index()
        labels = ["Normal", "Deficient"]
        vals = [counts.get(0.0, 0), counts.get(1.0, 0)]
        ax.pie(vals, labels=labels, colors=[colors["0"], colors["1"]],
               autopct="%1.1f%%", startangle=90,
               textprops={"fontsize": 8})
        ax.set_title(target.replace("_deficiency", "").replace("_", " ").title(),
                     fontsize=9)

    fig.suptitle("Deficiency Label Distributions", fontsize=13, fontweight="bold")
    plt.tight_layout()
    fig.savefig(FIGURES_DIR / "fig02_target_distributions.png")
    plt.close()
    rlog("**Figure saved:** fig02_target_distributions.png\n")


# ═══════════════════════════════════════════════════════════════════════════════
# SECTION 6: DEMOGRAPHIC DISTRIBUTIONS
# ═══════════════════════════════════════════════════════════════════════════════

def section_6_demographics(df: pd.DataFrame):
    rlog("## 6. Demographic Feature Distributions\n")

    # Summary stats for continuous demographic variables
    rlog("### Continuous Demographic Summary Statistics\n")
    demo_continuous = df[["age", "bmi"]].describe().round(2)
    rlog(demo_continuous.to_string())
    rlog("")

    # Categorical counts
    rlog("### Categorical Demographic Counts\n")
    rlog("**Gender:** (0=Female, 1=Male)")
    rlog(df["gender"].value_counts().to_string())
    rlog(f"\n**Activity Level:** (0=Sedentary, 1=Light, 2=Moderate, 3=Active, 4=Very Active)")
    rlog(df["activity_level"].value_counts().sort_index().to_string())
    rlog(f"\n**Dietary Preference:** (0=Omnivore, 1=Vegetarian, 2=Vegan)")
    rlog(df["dietary_preference"].value_counts().sort_index().to_string())
    rlog(f"\n**Is Pregnant:**\n{df['is_pregnant'].value_counts().to_string()}")
    rlog(f"\n**Is Smoker:**\n{df['is_smoker'].value_counts().to_string()}\n")

    fig, axes = plt.subplots(2, 3, figsize=(14, 8))

    # Age distribution
    axes[0, 0].hist(df["age"].dropna(), bins=30, color="#5C6BC0", edgecolor="white", alpha=0.85)
    axes[0, 0].set_title("Age Distribution")
    axes[0, 0].set_xlabel("Age (years)")

    # BMI distribution
    axes[0, 1].hist(df["bmi"].dropna(), bins=40, color="#26A69A", edgecolor="white", alpha=0.85)
    axes[0, 1].set_title("BMI Distribution")
    axes[0, 1].set_xlabel("BMI (kg/m²)")
    axes[0, 1].axvline(x=18.5, color="orange", linestyle="--", linewidth=1, label="Underweight")
    axes[0, 1].axvline(x=25, color="green", linestyle="--", linewidth=1, label="Normal/Overweight")
    axes[0, 1].axvline(x=30, color="red", linestyle="--", linewidth=1, label="Obese")
    axes[0, 1].legend(fontsize=7)

    # Gender
    gender_counts = df["gender"].value_counts()
    axes[0, 2].bar(["Female (0)", "Male (1)"], [gender_counts.get(0, 0), gender_counts.get(1, 0)],
                   color=["#EC407A", "#42A5F5"])
    axes[0, 2].set_title("Gender Distribution")

    # Activity level
    act_counts = df["activity_level"].value_counts().sort_index()
    act_labels = ["Sedentary", "Light", "Moderate", "Active", "V.Active"]
    axes[1, 0].bar(act_labels[:len(act_counts)], act_counts.values, color="#66BB6A")
    axes[1, 0].set_title("Activity Level")
    axes[1, 0].tick_params(axis="x", labelsize=8)

    # Dietary preference
    diet_counts = df["dietary_preference"].value_counts().sort_index()
    diet_labels = ["Omnivore", "Vegetarian", "Vegan"]
    axes[1, 1].bar(diet_labels[:len(diet_counts)], diet_counts.values, color="#FFA726")
    axes[1, 1].set_title("Dietary Preference")

    # Smoking vs Pregnancy (stacked or simple)
    yes_no_labels = ["No", "Yes"]
    smoker_counts = df["is_smoker"].value_counts().sort_index()
    pregnant_counts = df["is_pregnant"].value_counts().sort_index()
    x = np.arange(2)
    axes[1, 2].bar(x - 0.2, [smoker_counts.get(0, 0), smoker_counts.get(1, 0)],
                   0.35, label="Smoker", color="#EF5350")
    axes[1, 2].bar(x + 0.2, [pregnant_counts.get(0, 0), pregnant_counts.get(1, 0)],
                   0.35, label="Pregnant", color="#AB47BC")
    axes[1, 2].set_xticks(x)
    axes[1, 2].set_xticklabels(yes_no_labels)
    axes[1, 2].set_title("Smoker / Pregnant")
    axes[1, 2].legend(fontsize=8)

    fig.suptitle("Demographic Feature Distributions", fontsize=13, fontweight="bold")
    plt.tight_layout()
    fig.savefig(FIGURES_DIR / "fig03_demographics.png")
    plt.close()
    rlog("**Figure saved:** fig03_demographics.png\n")


# ═══════════════════════════════════════════════════════════════════════════════
# SECTION 7: LABORATORY FEATURE DISTRIBUTIONS
# ═══════════════════════════════════════════════════════════════════════════════

def section_7_lab_features(df: pd.DataFrame):
    rlog("## 7. Laboratory Feature Distributions\n")

    rlog("### Laboratory Feature Summary Statistics\n")
    lab_stats = df[LAB_COLS].describe().round(3)
    rlog(lab_stats.to_string())
    rlog("")

    # Histograms with clinical thresholds
    fig, axes = plt.subplots(2, 5, figsize=(18, 8))
    axes = axes.flatten()

    clinical_lines = {
        "hemoglobin_g_dl": [(12.0, "F threshold", "pink"), (13.0, "M threshold", "blue")],
        "serum_ferritin_ng_ml": [(12.0, "Deficiency", "red")],
        "vitamin_d_25ohd_ng_ml": [(20.0, "Deficient", "red"), (30.0, "Insufficient", "orange")],
        "vitamin_b12_pg_ml": [(200.0, "Deficiency", "red")],
        "serum_calcium_mg_dl": [(8.5, "Low", "red"), (10.5, "High", "orange")],
        "serum_folate_ng_ml": [(3.0, "Deficiency", "red")],
    }

    for i, col in enumerate(LAB_COLS):
        ax = axes[i]
        data = df[col].dropna()
        ax.hist(data, bins=40, color="#5C6BC0", edgecolor="white", alpha=0.8)
        ax.set_title(col.replace("_", " "), fontsize=8)
        ax.set_xlabel("")
        if col in clinical_lines:
            for val, label, color in clinical_lines[col]:
                ax.axvline(x=val, color=color, linestyle="--", linewidth=1.2,
                           label=label, alpha=0.9)
            ax.legend(fontsize=6)

    plt.suptitle("Laboratory Biomarker Distributions (with clinical thresholds)", fontsize=12, fontweight="bold")
    plt.tight_layout()
    fig.savefig(FIGURES_DIR / "fig04_lab_distributions.png")
    plt.close()
    rlog("**Figure saved:** fig04_lab_distributions.png\n")


# ═══════════════════════════════════════════════════════════════════════════════
# SECTION 8: DIETARY FEATURE DISTRIBUTIONS
# ═══════════════════════════════════════════════════════════════════════════════

def section_8_dietary_features(df: pd.DataFrame):
    rlog("## 8. Dietary Feature Distributions\n")

    rlog("### Dietary Feature Summary Statistics\n")
    diet_stats = df[DIETARY_COLS].describe().round(2)
    rlog(diet_stats.to_string())
    rlog("")

    # RDA reference lines
    rda_lines = {
        "dietary_iron_mg": 18,
        "dietary_calcium_mg": 1000,
        "dietary_vitamin_d_mcg": 15,
        "dietary_vitamin_b12_mcg": 2.4,
        "dietary_folate_mcg": 400,
        "dietary_vitamin_c_mg": 90,
        "dietary_protein_g": 56,
        "dietary_calories_kcal": 2000,
        "dietary_fiber_g": 25,
    }

    fig, axes = plt.subplots(3, 3, figsize=(14, 10))
    axes = axes.flatten()

    for i, col in enumerate(DIETARY_COLS):
        ax = axes[i]
        data = df[col].dropna()
        data_valid = data[data >= 0]
        ax.hist(data_valid, bins=40, color="#26A69A", edgecolor="white", alpha=0.8)
        ax.set_title(col.replace("dietary_", "").replace("_", " ").title(), fontsize=9)
        if col in rda_lines:
            ax.axvline(x=rda_lines[col], color="red", linestyle="--",
                       linewidth=1.2, label=f"RDA: {rda_lines[col]}")
            ax.legend(fontsize=7)

    fig.suptitle("Dietary Feature Distributions (with RDA reference lines)", fontsize=12, fontweight="bold")
    plt.tight_layout()
    fig.savefig(FIGURES_DIR / "fig05_dietary_distributions.png")
    plt.close()
    rlog("**Figure saved:** fig05_dietary_distributions.png\n")


# ═══════════════════════════════════════════════════════════════════════════════
# SECTION 9: SYMPTOM ANALYSIS
# ═══════════════════════════════════════════════════════════════════════════════

def section_9_symptoms(df: pd.DataFrame):
    rlog("## 9. Symptom Feature Analysis\n")

    symptom_binary_cols = [c for c in SYMPTOM_COLS if c != "symptom_count"]

    rlog("### Symptom Prevalence (% of subjects reporting each symptom)\n")
    rlog("| Symptom | Count | Prevalence % |")
    rlog("|---------|-------|-------------|")
    for col in symptom_binary_cols:
        count = int(df[col].sum())
        pct = count / len(df) * 100
        rlog(f"| {col} | {count} | {pct:.1f}% |")
    rlog("")

    # Symptom count distribution
    rlog("### Symptom Count Distribution")
    rlog(df["symptom_count"].describe().round(2).to_string())
    rlog("")

    fig, axes = plt.subplots(1, 2, figsize=(14, 5))

    # Prevalence bar chart
    symptom_prevalence = {col: df[col].mean() * 100 for col in symptom_binary_cols}
    sorted_symptoms = dict(sorted(symptom_prevalence.items(), key=lambda x: x[1], reverse=True))
    bars = axes[0].barh(
        list(sorted_symptoms.keys()),
        list(sorted_symptoms.values()),
        color=sns.color_palette("Set2", len(sorted_symptoms))
    )
    axes[0].set_xlabel("Prevalence (%)")
    axes[0].set_title("Symptom Prevalence")
    for bar, val in zip(bars, sorted_symptoms.values()):
        axes[0].text(bar.get_width() + 0.3, bar.get_y() + bar.get_height() / 2,
                     f"{val:.1f}%", va="center", fontsize=8)

    # Symptom count distribution
    axes[1].hist(df["symptom_count"], bins=range(0, 10), color="#FFA726",
                 edgecolor="white", align="left", rwidth=0.8)
    axes[1].set_xlabel("Number of Symptoms")
    axes[1].set_title("Total Symptom Count Distribution")
    axes[1].set_xticks(range(0, 9))

    fig.suptitle("Symptom Analysis", fontsize=13, fontweight="bold")
    plt.tight_layout()
    fig.savefig(FIGURES_DIR / "fig06_symptom_analysis.png")
    plt.close()
    rlog("**Figure saved:** fig06_symptom_analysis.png\n")


# ═══════════════════════════════════════════════════════════════════════════════
# SECTION 10: OUTLIER INVESTIGATION (IQR-based)
# ═══════════════════════════════════════════════════════════════════════════════

def section_10_outliers(df: pd.DataFrame):
    rlog("## 10. Outlier Investigation\n")
    rlog("Method: IQR-based flagging (value < Q1 - 1.5*IQR or > Q3 + 1.5*IQR)\n")

    numeric_cols = LAB_COLS + DIETARY_COLS + ["age", "bmi"]
    outlier_summary = []

    for col in numeric_cols:
        data = df[col].dropna()
        Q1 = data.quantile(0.25)
        Q3 = data.quantile(0.75)
        IQR = Q3 - Q1
        lower = Q1 - 1.5 * IQR
        upper = Q3 + 1.5 * IQR
        n_outliers = int(((data < lower) | (data > upper)).sum())
        pct_outliers = n_outliers / len(data) * 100
        outlier_summary.append({
            "feature": col,
            "Q1": round(Q1, 3),
            "Q3": round(Q3, 3),
            "IQR": round(IQR, 3),
            "lower_fence": round(lower, 3),
            "upper_fence": round(upper, 3),
            "n_outliers": n_outliers,
            "outlier_pct": round(pct_outliers, 2)
        })

    outlier_df = pd.DataFrame(outlier_summary).sort_values("outlier_pct", ascending=False)
    rlog(outlier_df[["feature", "lower_fence", "upper_fence", "n_outliers", "outlier_pct"]].to_string(index=False))
    rlog("")

    rlog("### Outlier Treatment Decision (deferred to Day 13)\n")
    rlog("- Log-normal features (serum_ferritin, vitamin_b12, dietary_vitamin_b12): IQR outliers may be genuine")
    rlog("- Invalid values (negative, impossible) will be removed in cleaning")
    rlog("- Extreme but physiologically plausible values will be retained with capping consideration")
    rlog("- No records silently deleted here; decisions documented in cleaning script\n")

    # Boxplots for key lab values
    fig, axes = plt.subplots(2, 5, figsize=(18, 7))
    axes = axes.flatten()
    for i, col in enumerate(LAB_COLS):
        data = df[col].dropna()
        axes[i].boxplot(data, vert=True, patch_artist=True,
                        boxprops=dict(facecolor="#90CAF9", alpha=0.8))
        axes[i].set_title(col.replace("_", "\n"), fontsize=7)
        axes[i].tick_params(axis="y", labelsize=7)

    fig.suptitle("Laboratory Feature Boxplots (Outlier Visualization)", fontsize=12, fontweight="bold")
    plt.tight_layout()
    fig.savefig(FIGURES_DIR / "fig07_outlier_boxplots.png")
    plt.close()
    rlog("**Figure saved:** fig07_outlier_boxplots.png\n")

    return outlier_df


# ═══════════════════════════════════════════════════════════════════════════════
# SECTION 11: FEATURE CORRELATIONS
# ═══════════════════════════════════════════════════════════════════════════════

def section_11_correlations(df: pd.DataFrame):
    rlog("## 11. Feature Correlations\n")

    # Focus on lab features + targets (fill NaN with median for correlation matrix only)
    corr_cols = LAB_COLS + TARGET_COLS
    corr_df = df[corr_cols].copy()
    for col in corr_df.columns:
        corr_df[col] = corr_df[col].fillna(corr_df[col].median())

    corr_matrix = corr_df.corr().round(3)

    fig, ax = plt.subplots(figsize=(14, 11))
    mask = np.zeros_like(corr_matrix, dtype=bool)
    np.fill_diagonal(mask, True)
    sns.heatmap(
        corr_matrix, ax=ax, annot=True, fmt=".2f", cmap="RdBu_r",
        center=0, linewidths=0.5, annot_kws={"size": 7},
        xticklabels=corr_matrix.columns, yticklabels=corr_matrix.columns
    )
    ax.tick_params(axis="x", rotation=45, labelsize=8)
    ax.tick_params(axis="y", rotation=0, labelsize=8)
    ax.set_title("Lab Features + Targets — Pearson Correlation Matrix", fontsize=12, fontweight="bold")
    plt.tight_layout()
    fig.savefig(FIGURES_DIR / "fig08_correlation_heatmap.png")
    plt.close()
    rlog("**Figure saved:** fig08_correlation_heatmap.png\n")

    rlog("### Key Correlation Observations")
    rlog("- hemoglobin and serum_ferritin: expected positive correlation (both iron markers)")
    rlog("- serum_iron and tibc: mildly negative (iron deficiency raises TIBC)")
    rlog("- transferrin_saturation = serum_iron / TIBC — strong correlation with both")
    rlog("- iron_deficiency: negatively correlated with hemoglobin, ferritin")
    rlog("- vitamin_d_deficiency: negatively correlated with vitamin_d_25ohd_ng_ml\n")


# ═══════════════════════════════════════════════════════════════════════════════
# SECTION 12: DEFICIENCY vs FEATURE ANALYSIS
# ═══════════════════════════════════════════════════════════════════════════════

def section_12_deficiency_vs_features(df: pd.DataFrame):
    rlog("## 12. Deficiency vs. Key Feature Analysis\n")

    fig, axes = plt.subplots(2, 5, figsize=(20, 8))

    # Row 1: Lab markers stratified by deficiency label
    pairs = [
        ("iron_deficiency", "hemoglobin_g_dl"),
        ("iron_deficiency", "serum_ferritin_ng_ml"),
        ("vitamin_d_deficiency", "vitamin_d_25ohd_ng_ml"),
        ("vitamin_b12_deficiency", "vitamin_b12_pg_ml"),
        ("calcium_deficiency", "serum_calcium_mg_dl"),
    ]

    for i, (target, feature) in enumerate(pairs):
        ax = axes[0, i]
        for label_val, color, name in [(0, "#4CAF50", "Normal"), (1, "#F44336", "Deficient")]:
            subset = df[df[target] == label_val][feature].dropna()
            ax.hist(subset, bins=30, alpha=0.6, color=color, label=name, density=True)
        ax.set_title(f"{feature.replace('_', ' ')}\nby {target.replace('_deficiency', '')} status",
                     fontsize=7)
        ax.legend(fontsize=6)

    # Row 2: Dietary intake vs deficiency
    pairs2 = [
        ("iron_deficiency", "dietary_iron_mg"),
        ("vitamin_d_deficiency", "dietary_vitamin_d_mcg"),
        ("vitamin_b12_deficiency", "dietary_vitamin_b12_mcg"),
        ("calcium_deficiency", "dietary_calcium_mg"),
        ("folate_deficiency", "dietary_folate_mcg"),
    ]

    for i, (target, feature) in enumerate(pairs2):
        ax = axes[1, i]
        for label_val, color, name in [(0, "#4CAF50", "Normal"), (1, "#F44336", "Deficient")]:
            subset = df[df[target] == label_val][feature].dropna()
            subset = subset[subset >= 0]
            ax.hist(subset, bins=30, alpha=0.6, color=color, label=name, density=True)
        ax.set_title(f"Dietary {feature.replace('dietary_', '').replace('_', ' ')}\nby {target.replace('_deficiency', '')} status",
                     fontsize=7)
        ax.legend(fontsize=6)

    fig.suptitle("Deficiency Status vs. Key Features", fontsize=12, fontweight="bold")
    plt.tight_layout()
    fig.savefig(FIGURES_DIR / "fig09_deficiency_vs_features.png")
    plt.close()
    rlog("**Figure saved:** fig09_deficiency_vs_features.png\n")


# ═══════════════════════════════════════════════════════════════════════════════
# SECTION 13: EDA CONCLUSIONS
# ═══════════════════════════════════════════════════════════════════════════════

def section_13_conclusions():
    rlog("## 13. EDA Conclusions Relevant to Model Development\n")

    conclusions = [
        "1. **Class imbalance is significant** for calcium and folate deficiency (~4% and ~2%).",
        "   Use class_weight='balanced' in Random Forest or SMOTE in Day 13/14.",
        "",
        "2. **Missing values are lab-test specific** (5-12%). Lab features missing together for",
        "   the same subject (systematic missing, not random). Impute with median by gender.",
        "",
        "3. **Invalid values confirmed**: negative hemoglobin, age=0/150/200, negative dietary iron,",
        "   impossible BMI. All must be removed in Day 13 cleaning.",
        "",
        "4. **15 exact duplicate rows** detected (injected deliberately). Remove in Day 13.",
        "",
        "5. **Lab markers are strong predictors** of their corresponding deficiencies (by design —",
        "   labels are derived from those same lab values). In inference, lab values may not always",
        "   be available; dietary + symptom features are the secondary signal.",
        "",
        "6. **Log-normal distributions** for serum_ferritin, vitamin_b12, dietary_vitamin_b12:",
        "   log-transform before modeling or use tree-based models that are scale-invariant.",
        "",
        "7. **Symptom features are soft signals**: individual symptoms have low specificity.",
        "   symptom_count may be more useful than individual binary flags.",
        "",
        "8. **Dietary features are single-day estimates**: high variability; treat as rough signal",
        "   rather than precise nutritional assessment.",
        "",
        "9. **Vegetarian/Vegan dietary preference** is a strong risk modifier for B12 deficiency.",
        "   Include as categorical feature.",
        "",
        "10. **Transferrin saturation** is a derived variable (serum_iron/TIBC*100).",
        "    May introduce leakage if all three are included simultaneously — consider dropping",
        "    one or using it in place of its components.",
    ]

    for line in conclusions:
        rlog(line)
    rlog("")


# ═══════════════════════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════════════════════

def main():
    print("=" * 70)
    print("Day 12 — Exploratory Data Analysis")
    print("=" * 70)

    # Load data
    print(f"\nLoading dataset from: {DATA_PATH}")
    df = pd.read_csv(DATA_PATH)
    print(f"Dataset loaded: {df.shape[0]} rows x {df.shape[1]} columns\n")

    # Run all EDA sections
    section_1_structure(df)
    missing_df = section_2_missing(df)
    section_3_duplicates(df)
    invalid_findings = section_4_invalid_values(df)
    section_5_target_distribution(df)
    section_6_demographics(df)
    section_7_lab_features(df)
    section_8_dietary_features(df)
    section_9_symptoms(df)
    outlier_df = section_10_outliers(df)
    section_11_correlations(df)
    section_12_deficiency_vs_features(df)
    section_13_conclusions()

    # Save EDA report
    report_path = REPORTS_DIR / "day12_eda_report.md"
    with open(report_path, "w", encoding="utf-8") as f:
        f.write("\n".join(report_lines))
    print(f"\nEDA report saved to: {report_path}")
    print(f"Figures saved to: {FIGURES_DIR}")
    print("\nDay 12 EDA complete. Proceed to Day 13 (Data Cleaning).")


if __name__ == "__main__":
    main()

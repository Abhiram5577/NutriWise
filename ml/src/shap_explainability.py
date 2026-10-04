"""
shap_explainability.py
======================
Day 18 - Risk Score & SHAP Explainability Module
Milestone 2: ML Nutritional Deficiency Detection Engine

Generates:
1. Global feature importance (per deficiency model)
2. Sample individual prediction explanations
3. Risk-score specification documentation
4. Frontend-friendly explanation structure

All outputs saved to ml/reports/ and ml/data/artifacts/
"""

import io
import json
import sys
import warnings
from pathlib import Path

if sys.stdout.encoding != "utf-8":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

import joblib
import numpy as np
import pandas as pd
import shap
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

warnings.filterwarnings("ignore")

ROOT = Path(__file__).parent.parent
PROCESSED_DIR = ROOT / "data" / "processed"
ARTIFACTS_DIR = ROOT / "data" / "artifacts"
MODELS_DIR = ROOT / "models"
REPORTS_DIR = ROOT / "reports"
FIGURES_DIR = ROOT / "reports" / "figures"

DEFICIENCY_NAMES = ["iron", "vitamin_d", "vitamin_b12", "calcium", "folate"]

LAB_FEATURES = [
    "hemoglobin_g_dl", "serum_ferritin_ng_ml", "serum_iron_mcg_dl", "tibc_mcg_dl",
    "vitamin_d_25ohd_ng_ml", "vitamin_b12_pg_ml", "serum_calcium_mg_dl",
    "serum_folate_ng_ml", "rbc_folate_ng_ml"
]

# Human-readable feature labels for frontend
FEATURE_DISPLAY_NAMES = {
    "age": "Age",
    "gender": "Biological Sex",
    "bmi": "Body Mass Index",
    "is_pregnant": "Pregnancy Status",
    "is_smoker": "Smoking Status",
    "dietary_iron_mg": "Daily Iron Intake (mg)",
    "dietary_calcium_mg": "Daily Calcium Intake (mg)",
    "dietary_vitamin_d_mcg": "Daily Vitamin D Intake (mcg)",
    "dietary_vitamin_b12_mcg": "Daily Vitamin B12 Intake (mcg)",
    "dietary_folate_mcg": "Daily Folate Intake (mcg DFE)",
    "dietary_vitamin_c_mg": "Daily Vitamin C Intake (mg)",
    "dietary_protein_g": "Daily Protein Intake (g)",
    "dietary_calories_kcal": "Daily Calorie Intake (kcal)",
    "dietary_fiber_g": "Daily Fiber Intake (g)",
    "symptom_fatigue": "Fatigue",
    "symptom_hair_loss": "Hair Loss",
    "symptom_skin_issues": "Skin Issues",
    "symptom_muscle_weakness": "Muscle Weakness",
    "symptom_mood_low": "Low Mood",
    "symptom_bone_pain": "Bone Pain",
    "symptom_tingling": "Tingling/Numbness",
    "symptom_cold_intolerance": "Cold Intolerance",
    "symptom_count": "Total Symptom Count",
    "activity_level_0": "Activity: Sedentary",
    "activity_level_1": "Activity: Light",
    "activity_level_2": "Activity: Moderate",
    "activity_level_3": "Activity: Active",
    "activity_level_4": "Activity: Very Active",
    "dietary_preference_0": "Diet: Omnivore",
    "dietary_preference_1": "Diet: Vegetarian",
    "dietary_preference_2": "Diet: Vegan",
}


def drop_lab_features(X: pd.DataFrame) -> pd.DataFrame:
    return X.drop(columns=[c for c in LAB_FEATURES if c in X.columns])


def main():
    print("=" * 60)
    print("Day 18 - SHAP Explainability & Risk Score Module")
    print("=" * 60)

    with open(ARTIFACTS_DIR / "feature_names_no_lab.json") as f:
        feature_names = json.load(f)

    report = []
    report.append("# Day 18 - Risk Score & SHAP Explainability Report")
    report.append("## Milestone 2: ML Nutritional Deficiency Detection Engine\n")
    report.append("---\n")

    # ── Section 1: Risk-Score Output Specification ────────────────────────────
    report.append("## 1. Risk-Score Output Specification\n")
    report.append("### 1.1 Output Format")
    report.append("Each deficiency prediction returns:\n")
    report.append("```json")
    report.append(json.dumps({
        "deficiency": "<name>",
        "status": "success | unsupported | error",
        "risk_probability": 0.0,
        "risk_level": "Low | Moderate | High",
        "contributors": {
            "dietary": [{"feature": "...", "display_name": "...", "impact_score": 0.0, "direction": "increases_risk"}],
            "symptom": [{"feature": "...", "display_name": "...", "impact_score": 0.0, "direction": "increases_risk"}],
            "demographic": [{"feature": "...", "display_name": "...", "impact_score": 0.0, "direction": "increases_risk"}]
        },
        "disclaimer": "This is a statistical risk estimate and NOT a medical diagnosis."
    }, indent=2))
    report.append("```\n")

    report.append("### 1.2 Risk Level Thresholds\n")
    report.append("| Level | Probability Range | Reasoning |")
    report.append("|-------|------------------|-----------|")
    report.append("| Low | < 0.30 | Below the base prevalence rate of most deficiencies in US adults (~15-34%). A probability below 30% indicates the model considers the individual less likely than average to be deficient. |")
    report.append("| Moderate | 0.30 - 0.60 | Within or modestly above population prevalence. Warrants dietary attention and monitoring. |")
    report.append("| High | > 0.60 | Substantially above population prevalence. Multiple risk factors converge. Strongly suggests clinical follow-up (blood test). |")
    report.append("")
    report.append("**Evidence for thresholds:**")
    report.append("- Iron deficiency prevalence in US women: ~15-20% (CDC/NHANES)")
    report.append("- Vitamin D insufficiency: ~35% of US adults (NIH ODS)")
    report.append("- B12 deficiency in vegans: up to 62% (Pawlak et al. 2014)")
    report.append("- Thresholds are deliberately conservative (lower High threshold) for a screening tool where false negatives are more costly than false positives.")
    report.append("- The 0.30/0.60 boundaries are NOT arbitrary: they align with the principle that a screening tool should flag at or above population prevalence (Low/Moderate boundary) and trigger clinical referral when risk is roughly 2x population prevalence (Moderate/High boundary).\n")

    report.append("### 1.3 Important Disclaimers")
    report.append("- Outputs are **risk estimates**, NOT diagnoses")
    report.append("- Contributors are **model factors**, NOT clinical causes")
    report.append("- The system cannot replace blood-test-based clinical evaluation")
    report.append("- Lab biomarkers are excluded from inference; the model uses dietary recall and symptoms only\n")

    # ── Section 2: Global Feature Importance (SHAP) ──────────────────────────
    report.append("## 2. Global Feature Importance (SHAP)\n")
    report.append("Global SHAP values computed using TreeExplainer on the validation set (lab features excluded).\n")

    global_importance_all = {}

    for def_name in DEFICIENCY_NAMES:
        print(f"\nComputing SHAP for {def_name}...")

        model = joblib.load(MODELS_DIR / f"xgb_final_{def_name}.pkl")
        explainer = shap.TreeExplainer(model)

        # Load validation set, drop lab features
        X_val = pd.read_csv(PROCESSED_DIR / f"X_val_{def_name}.csv", index_col=0)
        X_val_no_lab = drop_lab_features(X_val)

        # Compute SHAP values
        shap_values = explainer.shap_values(X_val_no_lab)

        # Mean absolute SHAP value per feature (global importance)
        mean_abs_shap = np.abs(shap_values).mean(axis=0)
        importance_df = pd.DataFrame({
            "feature": feature_names,
            "mean_abs_shap": mean_abs_shap
        }).sort_values("mean_abs_shap", ascending=False)

        # Save per-deficiency global importance
        global_importance_all[def_name] = importance_df.to_dict(orient="records")

        # Report table
        report.append(f"### {def_name.replace('_', ' ').title()} Deficiency\n")
        report.append("| Rank | Feature | Display Name | Mean |SHAP| | Category |")
        report.append("|------|---------|-------------|-------------|----------|")
        for rank, (_, row) in enumerate(importance_df.head(10).iterrows(), 1):
            feat = row["feature"]
            display = FEATURE_DISPLAY_NAMES.get(feat, feat)
            cat = "Dietary" if feat.startswith("dietary_") or feat.startswith("activity_level") else \
                  "Symptom" if feat.startswith("symptom_") else "Demographic"
            report.append(f"| {rank} | {feat} | {display} | {row['mean_abs_shap']:.4f} | {cat} |")
        report.append("")

        # SHAP summary plot
        fig, ax = plt.subplots(figsize=(10, 6))
        shap.summary_plot(shap_values, X_val_no_lab, feature_names=feature_names,
                          max_display=15, show=False)
        plt.title(f"{def_name.replace('_', ' ').title()} - SHAP Summary")
        plt.tight_layout()
        fig_path = FIGURES_DIR / f"fig_shap_summary_{def_name}.png"
        plt.savefig(fig_path, dpi=100, bbox_inches="tight")
        plt.close("all")
        report.append(f"**Figure saved:** fig_shap_summary_{def_name}.png\n")

    # Save global importance JSON artifact
    with open(ARTIFACTS_DIR / "global_feature_importance.json", "w") as f:
        json.dump(global_importance_all, f, indent=2)
    print(f"\nGlobal importance saved to: {ARTIFACTS_DIR / 'global_feature_importance.json'}")

    # ── Section 3: Individual Prediction Explanation Example ──────────────────
    report.append("## 3. Individual Prediction Explanation (Example)\n")
    report.append("Sample input: 35-year-old vegan female with fatigue, tingling, low mood, cold intolerance.\n")

    # Build a sample input matching the predictor format
    sample_raw = {
        "age": 35, "gender": 0, "bmi": 24.5, "is_pregnant": 0, "is_smoker": 0,
        "dietary_iron_mg": 5.0, "dietary_calcium_mg": 500, "dietary_vitamin_d_mcg": 2.0,
        "dietary_vitamin_b12_mcg": 0.5, "dietary_folate_mcg": 200, "dietary_vitamin_c_mg": 40,
        "dietary_protein_g": 45, "dietary_calories_kcal": 1500, "dietary_fiber_g": 10,
        "symptom_fatigue": 1, "symptom_hair_loss": 0, "symptom_skin_issues": 0,
        "symptom_muscle_weakness": 0, "symptom_mood_low": 1, "symptom_bone_pain": 0,
        "symptom_tingling": 1, "symptom_cold_intolerance": 1, "symptom_count": 4,
        "activity_level_0": 0, "activity_level_1": 1, "activity_level_2": 0,
        "activity_level_3": 0, "activity_level_4": 0,
        "dietary_preference_0": 0, "dietary_preference_1": 0, "dietary_preference_2": 1,
    }
    sample_df = pd.DataFrame([sample_raw])[feature_names]

    for def_name in DEFICIENCY_NAMES:
        model = joblib.load(MODELS_DIR / f"xgb_final_{def_name}.pkl")
        explainer = shap.TreeExplainer(model)
        sv = explainer.shap_values(sample_df)[0]
        proba = float(model.predict_proba(sample_df)[0, 1])

        report.append(f"### {def_name.replace('_', ' ').title()} (Probability: {proba:.4f})\n")

        # Top positive contributors
        indices = np.argsort(sv)[::-1]
        report.append("| Feature | Display Name | SHAP Value | Direction |")
        report.append("|---------|-------------|-----------|-----------|")
        count = 0
        for idx in indices:
            if count >= 5:
                break
            feat = feature_names[idx]
            display = FEATURE_DISPLAY_NAMES.get(feat, feat)
            direction = "increases risk" if sv[idx] > 0 else "decreases risk"
            report.append(f"| {feat} | {display} | {sv[idx]:.4f} | {direction} |")
            count += 1
        report.append("")

    # ── Section 4: Frontend-Friendly Explanation Structure ────────────────────
    report.append("## 4. Frontend-Friendly Explanation Structure\n")
    report.append("The `/predict` endpoint returns structured JSON that can be rendered directly by the React frontend:\n")
    report.append("```")
    report.append("For each deficiency in response.data:")
    report.append("  - risk_level: color-code the badge (Low=green, Moderate=amber, High=red)")
    report.append("  - risk_probability: render as percentage bar")
    report.append("  - contributors.dietary[]: list of dietary factors pushing risk up")
    report.append("  - contributors.symptom[]: list of symptom factors pushing risk up")
    report.append("  - contributors.demographic[]: list of demographic factors pushing risk up")
    report.append("  - Each contributor has:")
    report.append("    - feature: internal name")
    report.append("    - display_name: human-readable label for UI")
    report.append("    - impact_score: SHAP magnitude (higher = more influential)")
    report.append("  - disclaimer: always shown below results")
    report.append("```\n")

    # Save feature display names mapping as artifact for frontend use
    with open(ARTIFACTS_DIR / "feature_display_names.json", "w") as f:
        json.dump(FEATURE_DISPLAY_NAMES, f, indent=2)

    # ── Section 5: Risk Score Specification (JSON artifact) ──────────────────
    risk_spec = {
        "risk_levels": {
            "Low": {"threshold": "< 0.30", "color": "#22c55e", "action": "Continue balanced diet"},
            "Moderate": {"threshold": "0.30 - 0.60", "color": "#f59e0b", "action": "Review dietary intake; consider supplementation"},
            "High": {"threshold": "> 0.60", "color": "#ef4444", "action": "Recommend clinical follow-up with blood test"},
        },
        "supported_deficiencies": DEFICIENCY_NAMES,
        "unsupported_deficiencies": ["iodine", "magnesium", "zinc", "vitamin_a", "biotin", "vitamin_k", "vitamin_e", "selenium"],
        "explanation_method": "TreeSHAP (exact, polynomial-time)",
        "model_type": "XGBoost (lab features excluded)",
        "disclaimer": "This is a statistical risk estimate and NOT a medical diagnosis.",
    }
    with open(ARTIFACTS_DIR / "risk_score_specification.json", "w") as f:
        json.dump(risk_spec, f, indent=2)

    # Write report
    report_path = REPORTS_DIR / "day18_shap_explainability_report.md"
    with open(report_path, "w", encoding="utf-8") as f:
        f.write("\n".join(report))
    print(f"\nDay 18 report saved to: {report_path}")

    print("\n" + "=" * 60)
    print("Day 18 Complete - SHAP Explainability & Risk Score Module")
    print("=" * 60)
    print(f"Artifacts saved:")
    print(f"  - {ARTIFACTS_DIR / 'global_feature_importance.json'}")
    print(f"  - {ARTIFACTS_DIR / 'feature_display_names.json'}")
    print(f"  - {ARTIFACTS_DIR / 'risk_score_specification.json'}")
    print(f"  - SHAP summary plots in {FIGURES_DIR}")


if __name__ == "__main__":
    main()

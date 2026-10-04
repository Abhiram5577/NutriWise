import json
import warnings
from pathlib import Path
from typing import Dict, List, Any

import joblib
import numpy as np
import pandas as pd
import shap

warnings.filterwarnings("ignore")

ROOT = Path(__file__).parent.parent
ARTIFACTS_DIR = ROOT / "data" / "artifacts"
MODELS_DIR = ROOT / "models"

SUPPORTED_DEFICIENCIES = ["iron", "vitamin_d", "vitamin_b12", "calcium", "folate"]
UNSUPPORTED_DEFICIENCIES = ["iodine", "magnesium", "zinc", "vitamin_a", "biotin", "vitamin_k", "vitamin_e", "selenium"]

# 20 continuous numeric features expected by the Day 14 StandardScaler
NUMERIC_SCALE_COLS = [
    "age", "bmi",
    "hemoglobin_g_dl", "serum_ferritin_ng_ml", "serum_iron_mcg_dl",
    "tibc_mcg_dl", "vitamin_d_25ohd_ng_ml", "vitamin_b12_pg_ml",
    "serum_calcium_mg_dl", "serum_folate_ng_ml", "rbc_folate_ng_ml",
    "dietary_iron_mg", "dietary_calcium_mg", "dietary_vitamin_d_mcg",
    "dietary_vitamin_b12_mcg", "dietary_folate_mcg", "dietary_vitamin_c_mg",
    "dietary_protein_g", "dietary_calories_kcal", "dietary_fiber_g",
]

class NutritionalRiskPredictor:
    def __init__(self):
        self.models = {}
        self.scalers = {}
        self.explainers = {}
        
        # Load feature names
        with open(ARTIFACTS_DIR / "feature_names_no_lab.json", "r") as f:
            self.final_feature_names = json.load(f)
            
        # Load models, scalers, and initialize SHAP explainers
        for def_name in SUPPORTED_DEFICIENCIES:
            # Models
            model_path = MODELS_DIR / f"xgb_final_{def_name}.pkl"
            if model_path.exists():
                self.models[def_name] = joblib.load(model_path)
                # Initialize SHAP explainer for XGBoost
                self.explainers[def_name] = shap.TreeExplainer(self.models[def_name])
                
            # Scalers (from Day 14, one per deficiency since they were trained on different missing-target splits)
            scaler_path = ARTIFACTS_DIR / f"scaler_{def_name}.pkl"
            if scaler_path.exists():
                self.scalers[def_name] = joblib.load(scaler_path)

    def _preprocess_input(self, input_data: Dict[str, Any], def_name: str) -> pd.DataFrame:
        """Apply the identical preprocessing used during training."""
        
        # 1. Base values mapping
        # Convert dictionary to DataFrame for easier manipulation
        df = pd.DataFrame([input_data])
        
        # Ensure categorical variables have fallback
        df["activity_level"] = df.get("activity_level", 0).fillna(0).astype(int)
        df["dietary_preference"] = df.get("dietary_preference", 0).fillna(0).astype(int)
        
        # Calculate symptom count if not provided directly
        symptom_cols = [c for c in df.columns if c.startswith("symptom_") and c != "symptom_count"]
        if "symptom_count" not in df.columns and symptom_cols:
            df["symptom_count"] = df[symptom_cols].sum(axis=1)
            
        # 2. Scale continuous features (using dummy cols for lab data to satisfy the scaler)
        # Create a df with the 20 columns expected by the scaler
        scale_df = pd.DataFrame(0.0, index=df.index, columns=NUMERIC_SCALE_COLS)
        for col in NUMERIC_SCALE_COLS:
            if col in df.columns:
                scale_df[col] = df[col].astype(float)
        
        scaler = self.scalers[def_name]
        scaled_values = scaler.transform(scale_df)
        
        # Put scaled values back into our main df
        for i, col in enumerate(NUMERIC_SCALE_COLS):
            df[col] = scaled_values[:, i]
            
        # 3. One-hot encoding mapping based on final_feature_names
        # We manually map the OHE columns instead of pd.get_dummies to ensure consistency
        final_df = pd.DataFrame(0.0, index=df.index, columns=self.final_feature_names)
        
        for col in self.final_feature_names:
            if col.startswith("activity_level_"):
                val = int(col.split("_")[-1])
                final_df[col] = (df["activity_level"] == val).astype(float)
            elif col.startswith("dietary_preference_"):
                val = int(col.split("_")[-1])
                final_df[col] = (df["dietary_preference"] == val).astype(float)
            elif col in df.columns:
                final_df[col] = df[col].astype(float)
                
        return final_df

    def _determine_risk_level(self, probability: float) -> str:
        """
        Map probability to a qualitative risk level.
        Thresholds reasoned by distribution of predicted probabilities from XGBoost:
        < 30% : Low Risk
        30-60%: Moderate Risk
        > 60% : High Risk
        """
        if probability < 0.30:
            return "Low"
        elif probability < 0.60:
            return "Moderate"
        else:
            return "High"
            
    def _get_top_contributors(self, shap_values: np.ndarray, feature_names: List[str], top_n: int = 3) -> Dict[str, List[Dict[str, Any]]]:
        """Categorize SHAP impacts into dietary, symptom, and demographic groups."""
        # Load display names for frontend-friendly labels
        display_names_path = ARTIFACTS_DIR / "feature_display_names.json"
        display_map = {}
        if display_names_path.exists():
            with open(display_names_path) as f:
                display_map = json.load(f)

        contributors = {"dietary": [], "symptom": [], "demographic": []}
        
        for i, feat in enumerate(feature_names):
            impact = float(shap_values[i])
            if impact <= 0:
                continue # We only want positive contributors to the risk
                
            item = {
                "feature": feat,
                "display_name": display_map.get(feat, feat.replace("_", " ").title()),
                "impact_score": round(impact, 4),
                "direction": "increases_risk"
            }
            
            if feat.startswith("dietary_") or feat.startswith("activity_level_"):
                contributors["dietary"].append(item)
            elif feat.startswith("symptom_"):
                contributors["symptom"].append(item)
            else:
                contributors["demographic"].append(item)
                
        # Sort and take top N
        for category in contributors:
            contributors[category] = sorted(contributors[category], key=lambda x: x["impact_score"], reverse=True)[:top_n]
            
        return contributors

    def predict(self, user_data: Dict[str, Any], requested_targets: List[str] = None) -> Dict[str, Any]:
        """Predict multi-label deficiency risks."""
        if requested_targets is None:
            requested_targets = SUPPORTED_DEFICIENCIES + UNSUPPORTED_DEFICIENCIES
            
        results = {}
        
        for target in requested_targets:
            target_key = target.lower().replace(" ", "_")
            
            if target_key in UNSUPPORTED_DEFICIENCIES:
                results[target_key] = {
                    "status": "unsupported",
                    "message": "Nutrient not supported due to lack of reliable clinical biomarker data in training set.",
                    "risk_probability": None,
                    "risk_level": None
                }
                continue
                
            if target_key not in SUPPORTED_DEFICIENCIES:
                results[target_key] = {
                    "status": "error",
                    "message": f"Unknown target '{target}'",
                    "risk_probability": None,
                    "risk_level": None
                }
                continue
                
            # It's a supported deficiency
            model = self.models.get(target_key)
            explainer = self.explainers.get(target_key)
            
            if not model:
                results[target_key] = {"status": "error", "message": "Model artifact missing"}
                continue
                
            # 1. Preprocess
            X_df = self._preprocess_input(user_data, target_key)
            
            # 2. Predict Probability
            proba = float(model.predict_proba(X_df)[0, 1])
            risk_level = self._determine_risk_level(proba)
            
            # 3. Explainability (SHAP)
            shap_values = explainer.shap_values(X_df)[0]
            contributors = self._get_top_contributors(shap_values, self.final_feature_names)
            
            results[target_key] = {
                "status": "success",
                "risk_probability": round(proba, 4),
                "risk_level": risk_level,
                "contributors": contributors,
                "disclaimer": "This is a statistical risk estimate and NOT a medical diagnosis."
            }
            
        return results

if __name__ == "__main__":
    # Quick test
    sample = {
        "age": 35, "gender": 0, "bmi": 24.5, "is_pregnant": 0, "is_smoker": 0,
        "activity_level": 1, "dietary_preference": 2, # vegan
        "dietary_iron_mg": 5.0, "dietary_calcium_mg": 500, "dietary_vitamin_d_mcg": 2.0,
        "dietary_vitamin_b12_mcg": 0.5, "dietary_folate_mcg": 200, "dietary_vitamin_c_mg": 40,
        "dietary_protein_g": 45, "dietary_calories_kcal": 1500, "dietary_fiber_g": 10,
        "symptom_fatigue": 1, "symptom_tingling": 1, "symptom_hair_loss": 0,
        "symptom_skin_issues": 0, "symptom_muscle_weakness": 0, "symptom_mood_low": 1,
        "symptom_bone_pain": 0, "symptom_cold_intolerance": 1
    }
    
    predictor = NutritionalRiskPredictor()
    res = predictor.predict(sample, ["iron", "vitamin_b12", "zinc"])
    print(json.dumps(res, indent=2))

import json
import sys
import warnings
from pathlib import Path
import joblib
import pandas as pd
from xgboost import XGBClassifier

warnings.filterwarnings("ignore")

ROOT = Path(__file__).parent.parent
PROCESSED_DIR = ROOT / "data" / "processed"
MODELS_DIR = ROOT / "models"
ARTIFACTS_DIR = ROOT / "data" / "artifacts"
MODELS_DIR.mkdir(parents=True, exist_ok=True)

DEFICIENCY_NAMES = ["iron", "vitamin_d", "vitamin_b12", "calcium", "folate"]
RANDOM_SEED = 42

LAB_FEATURES = [
    "hemoglobin_g_dl", "serum_ferritin_ng_ml", "serum_iron_mcg_dl", "tibc_mcg_dl",
    "vitamin_d_25ohd_ng_ml", "vitamin_b12_pg_ml", "serum_calcium_mg_dl",
    "serum_folate_ng_ml", "rbc_folate_ng_ml"
]

def drop_lab_features(X: pd.DataFrame) -> pd.DataFrame:
    cols_to_drop = [c for c in LAB_FEATURES if c in X.columns]
    return X.drop(columns=cols_to_drop)

def main():
    print("=" * 60)
    print("Training Final XGBoost Models (Lab Features Excluded)")
    print("=" * 60)
    
    feature_names_saved = False

    for def_name in DEFICIENCY_NAMES:
        print(f"\nTraining model for {def_name}...")
        
        # Load train data (we'll just use train, or train+val to maximize data for final model)
        # Using train set to keep validation set for any other tuning if needed
        X_train = pd.read_csv(PROCESSED_DIR / f"X_train_{def_name}.csv", index_col=0)
        y_train = pd.read_csv(PROCESSED_DIR / f"y_train_{def_name}.csv", index_col=0).iloc[:, 0].astype(int)
        
        # Drop lab features from the pre-scaled training data
        X_train_no_lab = drop_lab_features(X_train)
        
        if not feature_names_saved:
            # Save the final feature names used by the models
            final_features = X_train_no_lab.columns.tolist()
            with open(ARTIFACTS_DIR / "feature_names_no_lab.json", "w") as f:
                json.dump(final_features, f, indent=2)
            feature_names_saved = True
            
        # Handle severe class imbalance
        scale_pos_weight = (len(y_train) - y_train.sum()) / y_train.sum()
        
        clf = XGBClassifier(
            n_estimators=200, 
            scale_pos_weight=scale_pos_weight, 
            random_state=RANDOM_SEED, 
            n_jobs=-1, 
            eval_metric="logloss"
        )
        
        clf.fit(X_train_no_lab, y_train)
        
        model_path = MODELS_DIR / f"xgb_final_{def_name}.pkl"
        joblib.dump(clf, model_path)
        print(f"Saved {model_path.name}")
        
    print("\nAll models trained and saved successfully.")

if __name__ == "__main__":
    main()

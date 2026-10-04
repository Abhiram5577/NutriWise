import json
from typing import Dict, List, Optional
from pydantic import BaseModel, Field
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import warnings

warnings.filterwarnings("ignore")

# Local import
from predictor import NutritionalRiskPredictor, SUPPORTED_DEFICIENCIES

app = FastAPI(
    title="NutriWise ML Prediction Service",
    description="Provides nutritional deficiency risk estimates using diet and symptom inputs.",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

predictor = None

@app.on_event("startup")
def load_ml_artifacts():
    global predictor
    try:
        predictor = NutritionalRiskPredictor()
        print("ML models and preprocessing artifacts loaded successfully.")
    except Exception as e:
        print(f"Error loading ML artifacts: {e}")
        raise e

# --- Request Schemas ---

class PredictionRequest(BaseModel):
    # Demographic
    age: int = Field(..., ge=18, le=110, description="Age in years (18-110)")
    gender: int = Field(..., description="0=Female, 1=Male")
    bmi: float = Field(..., ge=10, le=80, description="Body Mass Index")
    is_pregnant: int = Field(0, description="0=No, 1=Yes")
    is_smoker: int = Field(0, description="0=No, 1=Yes")
    activity_level: int = Field(0, ge=0, le=4, description="0=sedentary to 4=very_active")
    dietary_preference: int = Field(0, ge=0, le=2, description="0=omnivore, 1=vegetarian, 2=vegan")
    
    # Dietary
    dietary_iron_mg: float = Field(0.0)
    dietary_calcium_mg: float = Field(0.0)
    dietary_vitamin_d_mcg: float = Field(0.0)
    dietary_vitamin_b12_mcg: float = Field(0.0)
    dietary_folate_mcg: float = Field(0.0)
    dietary_vitamin_c_mg: float = Field(0.0)
    dietary_protein_g: float = Field(0.0)
    dietary_calories_kcal: float = Field(0.0)
    dietary_fiber_g: float = Field(0.0)
    
    # Symptoms
    symptom_fatigue: int = Field(0)
    symptom_hair_loss: int = Field(0)
    symptom_skin_issues: int = Field(0)
    symptom_muscle_weakness: int = Field(0)
    symptom_mood_low: int = Field(0)
    symptom_bone_pain: int = Field(0)
    symptom_tingling: int = Field(0)
    symptom_cold_intolerance: int = Field(0)
    
    # Optional targets to limit prediction processing
    requested_targets: Optional[List[str]] = Field(None, description=f"List of targets. Supported: {', '.join(SUPPORTED_DEFICIENCIES)}")

@app.post("/predict")
async def predict_deficiencies(request: PredictionRequest):
    if predictor is None:
        raise HTTPException(status_code=503, detail="ML Models not loaded")
        
    try:
        user_data = request.model_dump()
        targets = user_data.pop("requested_targets", None)
        
        # Make prediction
        results = predictor.predict(user_data, requested_targets=targets)
        
        return {
            "status": "success",
            "message": "Risk estimates generated successfully",
            "data": results
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# --- Integration endpoint: accepts Milestone 1 data structures ---

class FoodDiaryItem(BaseModel):
    food_name: Optional[str] = None
    calories: Optional[float] = 0.0
    protein_g: Optional[float] = 0.0
    carbs_g: Optional[float] = 0.0
    fat_g: Optional[float] = 0.0
    fiber_g: Optional[float] = 0.0
    vitamin_a_mcg: Optional[float] = 0.0
    vitamin_c_mg: Optional[float] = 0.0
    calcium_mg: Optional[float] = 0.0
    iron_mg: Optional[float] = 0.0

class SymptomItem(BaseModel):
    symptom_name: str
    severity: str = "moderate"

class HealthProfileData(BaseModel):
    age: Optional[int] = 30
    gender: Optional[str] = "male"
    height_cm: Optional[float] = None
    weight_kg: Optional[float] = None
    activity_level: Optional[str] = "sedentary"
    dietary_preference: Optional[str] = "omnivore"

class IntegrationRequest(BaseModel):
    health_profile: HealthProfileData
    food_diary_entries: List[FoodDiaryItem] = []
    symptoms: List[SymptomItem] = []
    requested_targets: Optional[List[str]] = None

@app.post("/predict/from-app")
async def predict_from_app(request: IntegrationRequest):
    """
    Integration endpoint: accepts Milestone 1 data structures
    (health profile, food diary, symptoms) and converts them to ML input.
    """
    if predictor is None:
        raise HTTPException(status_code=503, detail="ML Models not loaded")
    
    try:
        from integration import build_prediction_request
        
        payload, data_gaps, field_mapping = build_prediction_request(
            health_profile=request.health_profile.model_dump(),
            food_diary_entries=[e.model_dump() for e in request.food_diary_entries],
            symptoms=[s.model_dump() for s in request.symptoms],
            requested_targets=request.requested_targets,
        )
        
        # Remove requested_targets from payload for predictor.predict
        targets = payload.pop("requested_targets", None)
        results = predictor.predict(payload, requested_targets=targets)
        
        return {
            "status": "success",
            "message": "Risk estimates generated from application data",
            "data": results,
            "data_gaps": data_gaps,
            "field_mapping": field_mapping,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={"status": "error", "message": f"An internal error occurred: {str(exc)}"}
    )

if __name__ == "__main__":
    uvicorn.run("api:app", host="0.0.0.0", port=8000, reload=True)


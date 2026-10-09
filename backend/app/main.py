from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from app.schemas.api_schemas import PredictionRequest, PredictionResponse, HealthResponse, ModelInfoResponse
from app.services.services import ModelService, AnalyticsService
import uvicorn
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="EV Charging Demand Prediction API",
    description="API for EV charging demand prediction and peak analytics.",
    version="1.0.0"
)

# CORS configuration for future React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all for development; restrict in prod
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup_event():
    """Load model and dataset into memory on startup."""
    try:
        ModelService.load_artifacts()
        AnalyticsService._get_data()  # Trigger data load
        logger.info("Successfully loaded ML model and analytics dataset.")
    except Exception as e:
        logger.error(f"Error loading artifacts: {e}")
        # We don't crash here so /api/health can report the failure properly.

@app.get("/api/health", response_model=HealthResponse)
async def health_check():
    """Check API health and model status."""
    is_loaded = ModelService._model is not None
    return HealthResponse(
        status="ok",
        model_loaded=is_loaded,
        api_version="1.0.0"
    )

@app.get("/api/model-info", response_model=ModelInfoResponse)
async def get_model_info():
    """Return model metadata and evaluation metrics."""
    try:
        manifest = ModelService.get_manifest()
        final_model = manifest.get('final_model', {})
        feature_info = manifest.get('feature_info', {})
        boundaries = feature_info.get('split_boundaries', {})
        
        return ModelInfoResponse(
            model_name=final_model.get('model_name', 'Unknown'),
            target=final_model.get('target', 'Demand'),
            expected_features=final_model.get('features', []),
            validation_metrics=final_model.get('validation_metrics', {}),
            test_metrics=final_model.get('test_metrics', {}),
            training_period=f"up to {boundaries.get('train_end')}",
            validation_period=f"{boundaries.get('val_start')} to {boundaries.get('val_end')}",
            test_period=f"{boundaries.get('test_start')} onwards"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch model info: {str(e)}")

@app.post("/api/predict", response_model=PredictionResponse)
async def predict(request: PredictionRequest):
    """Predict energy demand (kWh) for a charging session."""
    if ModelService._model is None:
        raise HTTPException(status_code=503, detail="Model is not loaded.")
        
    try:
        features_dict = request.model_dump()
        prediction = ModelService.predict(features_dict)
        
        return PredictionResponse(
            predicted_kwh=round(prediction, 2),
            model_name=ModelService.get_manifest()['final_model']['model_name']
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Prediction failed: {str(e)}")

# -------------------------------------------------------------------
# Analytics Endpoints
# -------------------------------------------------------------------

@app.get("/api/analytics/summary")
async def get_analytics_summary():
    try:
        return AnalyticsService.get_summary()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/analytics/hourly")
async def get_analytics_hourly():
    try:
        return AnalyticsService.get_hourly()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/analytics/location")
async def get_analytics_location():
    try:
        return AnalyticsService.get_location()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/analytics/monthly")
async def get_analytics_monthly():
    try:
        return AnalyticsService.get_monthly()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/analytics/peak")
async def get_analytics_peak():
    try:
        return AnalyticsService.get_peak()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/model-performance")
async def get_model_performance():
    try:
        manifest = ModelService.get_manifest()
        return {
            "validation": manifest.get('final_model', {}).get('validation_metrics', {}),
            "test": manifest.get('final_model', {}).get('test_metrics', {})
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

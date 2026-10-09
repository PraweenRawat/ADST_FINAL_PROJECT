from pydantic import BaseModel, Field, validator
from typing import Optional

class PredictionRequest(BaseModel):
    hour: int = Field(..., ge=0, le=23, description="Hour of the day (0-23)")
    day_of_week: int = Field(..., ge=0, le=6, description="Day of the week (0=Monday, 6=Sunday)")
    month: int = Field(..., ge=1, le=12, description="Month of the year (1-12)")
    is_weekend: int = Field(..., ge=0, le=1, description="1 if weekend, 0 otherwise")
    ChargerType: int = Field(..., ge=0, le=1, description="0 for Slow (AC), 1 for Fast (DC)")
    ChargerCompany: int = Field(..., ge=0, le=1, description="0 or 1 for charger company")
    Location: str = Field(..., description="Location category (e.g., apartment, public area, resort)")

class PredictionResponse(BaseModel):
    predicted_kwh: float = Field(..., description="Predicted total energy consumed in kWh")
    model_name: str = Field(..., description="The ML model used for prediction")

class HealthResponse(BaseModel):
    status: str
    model_loaded: bool
    api_version: str

class ModelInfoResponse(BaseModel):
    model_name: str
    target: str
    expected_features: list[str]
    validation_metrics: dict
    test_metrics: dict
    training_period: str
    validation_period: str
    test_period: str

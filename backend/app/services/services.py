import json
from pathlib import Path
from typing import Any
import pandas as pd
import joblib

# Paths
BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent
MODEL_PATH = BASE_DIR / 'models' / 'best_model_pipeline.joblib'
MANIFEST_PATH = BASE_DIR / 'reports' / 'results' / 'project_manifest.json'
CLEANED_DATA_PATH = BASE_DIR / 'data' / 'processed' / 'ChargingRecords_cleaned.csv'

class ModelService:
    _model = None
    _manifest = None
    
    @classmethod
    def load_artifacts(cls):
        if cls._model is None:
            if not MODEL_PATH.exists():
                raise FileNotFoundError(f"Model file not found at {MODEL_PATH}")
            cls._model = joblib.load(MODEL_PATH)
            
        if cls._manifest is None:
            if not MANIFEST_PATH.exists():
                raise FileNotFoundError(f"Manifest file not found at {MANIFEST_PATH}")
            with open(MANIFEST_PATH, 'r') as f:
                cls._manifest = json.load(f)
                
    @classmethod
    def get_model(cls):
        cls.load_artifacts()
        return cls._model
        
    @classmethod
    def get_manifest(cls) -> dict:
        cls.load_artifacts()
        return cls._manifest

    @classmethod
    def predict(cls, features_dict: dict) -> float:
        model = cls.get_model()
        df = pd.DataFrame([features_dict])
        prediction = model.predict(df)[0]
        return float(prediction)


class AnalyticsService:
    _df = None
    
    @classmethod
    def _get_data(cls) -> pd.DataFrame:
        if cls._df is None:
            if not CLEANED_DATA_PATH.exists():
                raise FileNotFoundError(f"Cleaned dataset not found at {CLEANED_DATA_PATH}")
            cls._df = pd.read_csv(CLEANED_DATA_PATH)
        return cls._df

    @classmethod
    def get_summary(cls) -> dict:
        manifest = ModelService.get_manifest()
        return manifest.get('analytics_summary', {})
        
    @classmethod
    def get_peak(cls) -> dict:
        manifest = ModelService.get_manifest()
        return manifest.get('peak_analytics', {})

    @classmethod
    def get_hourly(cls) -> list[dict]:
        df = cls._get_data()
        df['hour'] = pd.to_datetime(df['StartDatetime']).dt.hour
        hourly = df.groupby('hour').agg(
            sessions=('Demand', 'count'),
            total_demand_kwh=('Demand', 'sum'),
            avg_demand_kwh=('Demand', 'mean')
        ).reset_index()
        return hourly.round(2).to_dict(orient='records')
        
    @classmethod
    def get_monthly(cls) -> list[dict]:
        df = cls._get_data()
        df['year_month'] = pd.to_datetime(df['StartDatetime']).dt.to_period('M').astype(str)
        monthly = df.groupby('year_month').agg(
            sessions=('Demand', 'count'),
            total_demand_kwh=('Demand', 'sum'),
            avg_demand_kwh=('Demand', 'mean')
        ).reset_index()
        return monthly.round(2).to_dict(orient='records')

    @classmethod
    def get_location(cls) -> list[dict]:
        df = cls._get_data()
        location = df.groupby('Location').agg(
            sessions=('Demand', 'count'),
            total_demand_kwh=('Demand', 'sum'),
            avg_demand_kwh=('Demand', 'mean')
        ).reset_index().sort_values('total_demand_kwh', ascending=False)
        return location.round(2).to_dict(orient='records')

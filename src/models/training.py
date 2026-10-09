"""
Model Training for EV Charging Demand Project.

Models:
1. Linear Regression
2. Decision Tree Regressor (max_depth=10, min_samples_leaf=20)
3. Random Forest Regressor (n_estimators=200, max_depth=15, min_samples_leaf=10)

Each model is wrapped in a sklearn Pipeline with a ColumnTransformer
for preprocessing (OneHotEncoder for Location, passthrough for numericals).
"""
import numpy as np
import pandas as pd
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder
from sklearn.linear_model import LinearRegression
from sklearn.tree import DecisionTreeRegressor
from sklearn.ensemble import RandomForestRegressor
import joblib
from pathlib import Path

# Import feature definitions
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))
from src.features.engineering import NUMERICAL_FEATURES, CATEGORICAL_FEATURES


def build_preprocessor(location_categories: list[str] | None = None) -> ColumnTransformer:
    """
    Build the preprocessing ColumnTransformer.
    
    - OneHotEncoder for Location (categorical)
    - Passthrough for numerical features
    """
    if location_categories is not None:
        ohe = OneHotEncoder(
            categories=[location_categories],
            drop='first',
            sparse_output=False,
            handle_unknown='infrequent_if_exist'
        )
    else:
        ohe = OneHotEncoder(
            drop='first',
            sparse_output=False,
            handle_unknown='infrequent_if_exist'
        )
    
    preprocessor = ColumnTransformer(
        transformers=[
            ('cat', ohe, CATEGORICAL_FEATURES),
            ('num', 'passthrough', NUMERICAL_FEATURES),
        ],
        remainder='drop'
    )
    return preprocessor


def build_model_configs() -> dict:
    """Return model configurations."""
    return {
        'LinearRegression': {
            'model': LinearRegression(),
            'params': {},
        },
        'DecisionTreeRegressor': {
            'model': DecisionTreeRegressor(
                max_depth=10,
                min_samples_leaf=20,
                random_state=42
            ),
            'params': {
                'max_depth': 10,
                'min_samples_leaf': 20,
                'random_state': 42,
            },
        },
        'RandomForestRegressor': {
            'model': RandomForestRegressor(
                n_estimators=200,
                max_depth=15,
                min_samples_leaf=10,
                random_state=42,
                n_jobs=-1
            ),
            'params': {
                'n_estimators': 200,
                'max_depth': 15,
                'min_samples_leaf': 10,
                'random_state': 42,
                'n_jobs': -1,
            },
        },
    }


def train_models(
    X_train: pd.DataFrame,
    y_train: pd.Series,
    location_categories: list[str] | None = None
) -> dict:
    """
    Train all three models, each with its own preprocessing pipeline.
    
    Returns dict of {model_name: fitted_pipeline}.
    """
    configs = build_model_configs()
    pipelines = {}
    
    for name, config in configs.items():
        print(f"  Training {name}...")
        preprocessor = build_preprocessor(location_categories)
        pipeline = Pipeline([
            ('preprocessor', preprocessor),
            ('model', config['model']),
        ])
        pipeline.fit(X_train, y_train)
        pipelines[name] = pipeline
        print(f"  {name} trained successfully.")
    
    return pipelines


def save_pipeline(pipeline: Pipeline, path: str) -> None:
    """Save a fitted pipeline to disk using joblib."""
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(pipeline, path)


def load_pipeline(path: str) -> Pipeline:
    """Load a saved pipeline from disk."""
    return joblib.load(path)

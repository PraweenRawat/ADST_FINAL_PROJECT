"""
Model Evaluation for EV Charging Demand Project.

Metrics: MAE, RMSE, R²
"""
import numpy as np
import pandas as pd
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.pipeline import Pipeline


def evaluate_model(pipeline: Pipeline, X: pd.DataFrame, y: pd.Series) -> dict:
    """
    Evaluate a fitted pipeline on given data.
    Returns dict with MAE, RMSE, R².
    """
    y_pred = pipeline.predict(X)
    
    mae = mean_absolute_error(y, y_pred)
    rmse = np.sqrt(mean_squared_error(y, y_pred))
    r2 = r2_score(y, y_pred)
    
    return {
        'MAE': round(float(mae), 4),
        'RMSE': round(float(rmse), 4),
        'R2': round(float(r2), 4),
    }


def compare_models(
    pipelines: dict,
    X: pd.DataFrame,
    y: pd.Series,
    dataset_label: str = 'validation'
) -> pd.DataFrame:
    """
    Evaluate all models and return a comparison DataFrame.
    """
    results = []
    for name, pipeline in pipelines.items():
        metrics = evaluate_model(pipeline, X, y)
        metrics['Model'] = name
        metrics['Dataset'] = dataset_label
        results.append(metrics)
    
    df = pd.DataFrame(results)[['Model', 'Dataset', 'MAE', 'RMSE', 'R2']]
    return df


def select_best_model(comparison_df: pd.DataFrame, metric: str = 'MAE') -> str:
    """
    Select the best model based on a metric.
    For MAE/RMSE: lower is better.
    For R2: higher is better.
    """
    if metric == 'R2':
        best_idx = comparison_df[metric].idxmax()
    else:
        best_idx = comparison_df[metric].idxmin()
    
    return comparison_df.loc[best_idx, 'Model']


def get_feature_importances(pipeline: Pipeline, feature_names: list[str]) -> dict | None:
    """
    Extract feature importances from tree-based models.
    Returns None for models without feature_importances_.
    """
    model = pipeline.named_steps['model']
    
    if not hasattr(model, 'feature_importances_'):
        return None
    
    # Get transformed feature names from the preprocessor
    preprocessor = pipeline.named_steps['preprocessor']
    try:
        transformed_names = preprocessor.get_feature_names_out()
        transformed_names = [str(n) for n in transformed_names]
    except Exception:
        transformed_names = [f'feature_{i}' for i in range(len(model.feature_importances_))]
    
    importances = model.feature_importances_
    importance_dict = dict(zip(transformed_names, [round(float(v), 6) for v in importances]))
    
    # Sort by importance descending
    importance_dict = dict(sorted(importance_dict.items(), key=lambda x: x[1], reverse=True))
    
    return importance_dict

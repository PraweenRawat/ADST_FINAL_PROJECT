"""
Main Pipeline for EV Charging Demand Project.
Orchestrates Phase 2: Cleaning -> Features -> Training -> Evaluation -> Analytics
"""
import sys
import json
import traceback
import pandas as pd
import numpy as np
from pathlib import Path

class NumpyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.integer):
            return int(obj)
        if isinstance(obj, np.floating):
            return float(obj)
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        return super().default(obj)


# Add project root to sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from src.data.cleaning import run_cleaning_pipeline
from src.features.engineering import extract_temporal_features, chronological_split, prepare_features_target, get_feature_info
from src.models.training import train_models, save_pipeline
from src.evaluation.metrics import compare_models, select_best_model, evaluate_model, get_feature_importances
from src.analytics.peak_demand import run_full_analytics

def main():
    print("============================================================")
    print("PHASE 2: PROJECT PIPELINE EXECUTION")
    print("============================================================")
    
    paths = {
        'raw_data': str(PROJECT_ROOT / 'data' / 'raw' / 'ChargingRecords.csv'),
        'processed_data': str(PROJECT_ROOT / 'data' / 'processed' / 'ChargingRecords_cleaned.csv'),
        'best_model': str(PROJECT_ROOT / 'models' / 'best_model_pipeline.joblib'),
        'model_metadata': str(PROJECT_ROOT / 'models' / 'model_metadata.json'),
        'manifest': str(PROJECT_ROOT / 'reports' / 'results' / 'project_manifest.json')
    }
    
    # 1. Data Cleaning
    print("\n[1] Running Data Cleaning Pipeline...")
    df_clean, cleaning_stats = run_cleaning_pipeline(paths['raw_data'], paths['processed_data'])
    print(f"  Raw rows: {cleaning_stats['raw_rows']} -> Cleaned rows: {cleaning_stats['cleaned_rows']}")
    
    # 2. Peak Demand Analytics (on actual historical data)
    print("\n[2] Computing Peak Demand Analytics...")
    analytics_results = run_full_analytics(df_clean)
    
    # 3. Feature Engineering & Split
    print("\n[3] Feature Engineering & Chronological Split...")
    df_feat = extract_temporal_features(df_clean)
    train_df, val_df, test_df = chronological_split(df_feat)
    
    X_train, y_train = prepare_features_target(train_df)
    X_val, y_val = prepare_features_target(val_df)
    X_test, y_test = prepare_features_target(test_df)
    
    print(f"  Train: {len(X_train)} rows")
    print(f"  Val:   {len(X_val)} rows")
    print(f"  Test:  {len(X_test)} rows")
    
    # Extract unique location categories from training set to ensure consistent encoding
    location_cats = sorted(X_train['Location'].unique().tolist())
    
    # 4. Model Training
    print("\n[4] Training Models...")
    pipelines = train_models(X_train, y_train, location_cats)
    
    # 5. Validation & Model Selection
    print("\n[5] Evaluating on Validation Set...")
    val_comparison = compare_models(pipelines, X_val, y_val, dataset_label='validation')
    print("\nValidation Results:")
    print(val_comparison.to_string(index=False))
    
    best_model_name = select_best_model(val_comparison, metric='MAE')
    print(f"\n  Selected Best Model: {best_model_name}")
    
    # 6. Final Test Evaluation
    print("\n[6] Evaluating Best Model on Test Set...")
    best_pipeline = pipelines[best_model_name]
    test_metrics = evaluate_model(best_pipeline, X_test, y_test)
    print(f"  Test Metrics: {test_metrics}")
    
    # Feature Importances (if available)
    importances = get_feature_importances(best_pipeline, X_train.columns.tolist())
    
    # 7. Save Artifacts
    print("\n[7] Saving Artifacts...")
    save_pipeline(best_pipeline, paths['best_model'])
    print(f"  Saved model pipeline to {paths['best_model']}")
    
    feature_info = get_feature_info()
    model_metadata = {
        'model_name': best_model_name,
        'target': feature_info['target'],
        'features': feature_info['all_features'],
        'training_date': pd.Timestamp.now().isoformat(),
        'validation_metrics': val_comparison[val_comparison['Model'] == best_model_name].to_dict('records')[0],
        'test_metrics': test_metrics,
        'feature_importances': importances
    }
    
    with open(paths['model_metadata'], 'w') as f:
        json.dump(model_metadata, f, indent=2, cls=NumpyEncoder)
    print(f"  Saved model metadata to {paths['model_metadata']}")
    
    manifest = {
        'project': 'EV Charging Demand Prediction',
        'cleaning': cleaning_stats,
        'feature_info': feature_info,
        'model_selection': {
            'validation_results': val_comparison.to_dict('records'),
            'best_model': best_model_name
        },
        'final_model': model_metadata,
        'peak_analytics': analytics_results['peak_demand'],
        'analytics_summary': analytics_results['summary']
    }
    
    with open(paths['manifest'], 'w') as f:
        json.dump(manifest, f, indent=2, cls=NumpyEncoder)
    print(f"  Saved project manifest to {paths['manifest']}")
    
    print("\n============================================================")
    print("PIPELINE COMPLETE")
    print("============================================================")

if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        print(f"ERROR: {e}")
        traceback.print_exc()

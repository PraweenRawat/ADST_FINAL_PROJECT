"""
Generate Phase 2 Report from Project Manifest
"""
import json
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent

def generate_report():
    manifest_path = PROJECT_ROOT / 'reports' / 'results' / 'project_manifest.json'
    report_path = PROJECT_ROOT / 'PHASE_2_REPORT.md'
    
    with open(manifest_path, 'r') as f:
        data = json.load(f)
        
    cleaning = data['cleaning']
    features = data['feature_info']
    selection = data['model_selection']
    final = data['final_model']
    peak = data['peak_analytics']
    
    report = f"""# PHASE 2 REPORT — ML Pipeline Implementation

## 1. Data Cleaning Decisions & Results
- **Negative Duration Removed**: {cleaning['removed_negative_duration']} rows (EndDatetime < StartDatetime, physically impossible)
- **True Zero Duration Removed**: {cleaning['removed_true_zero_duration']} rows (Start==End AND Duration==0, trivial/failed sessions)
- **Exact Duplicates Removed**: {cleaning['removed_exact_duplicates']} rows (pipeline artifacts)
- **Invalid Demand Removed**: {cleaning['removed_invalid_demand']} rows (<= 0)
- **Row Counts**: Started with {cleaning['raw_rows']} raw rows -> Resulted in {cleaning['cleaned_rows']} cleaned rows.
- **Total Removed**: {cleaning['total_removed']} rows ({cleaning['removal_pct']}%)

## 2. Feature Engineering

### Final Feature List
- **Numerical/Ordinal**: {", ".join(features['numerical_features'])}
- **Categorical (One-Hot Encoded)**: {", ".join(features['categorical_features'])}
- **Target Variable**: `{features['target']}` (Total energy consumed in kWh per session)

### Excluded Features
"""
    for feat, reason in features['excluded_features'].items():
        report += f"- **`{feat}`**: {reason}\n"

    report += f"""
### Temporal Split Strategy
Chronological splitting by date:
- **Train**: up to {features['split_boundaries']['train_end']}
- **Validation**: {features['split_boundaries']['val_start']} to {features['split_boundaries']['val_end']}
- **Test**: {features['split_boundaries']['test_start']} onwards

## 3. EDA & Peak Demand Analytics
(Analytics computed from actual historical data, not ML predictions)

- **Peak Hour (Total Demand)**: {peak['peak_hour_by_total_demand']}:00 ({peak['peak_hour_by_total_demand_kwh']} kWh)
- **Busiest Hour (Sessions)**: {peak['busiest_hour_by_sessions']}:00 ({peak['busiest_hour_sessions_count']} sessions)
- **Peak Day of Week**: {peak['peak_day_of_week']} (Avg {peak['peak_day_avg_demand_kwh']} kWh/session)
- **Peak Date**: {peak['peak_date']} ({peak['peak_date_total_kwh']} kWh total)
- **Weekday vs Weekend**: Weekday average {peak['weekday_avg_demand_kwh']} kWh vs Weekend average {peak['weekend_avg_demand_kwh']} kWh

## 4. Model Configurations & Validation Results

Evaluated 3 models using standard configurations:
- Linear Regression (Baseline)
- Decision Tree Regressor (max_depth=10, min_samples_leaf=20)
- Random Forest Regressor (n_estimators=200, max_depth=15, min_samples_leaf=10)

### Validation Metrics
| Model | MAE | RMSE | R² |
|-------|-----|------|----|
"""
    for res in selection['validation_results']:
        report += f"| {res['Model']} | {res['MAE']:.4f} | {res['RMSE']:.4f} | {res['R2']:.4f} |\n"
        
    report += f"""
### Model Selection
**Selected Model**: {selection['best_model']}
**Justification**: Selected strictly based on the lowest Mean Absolute Error (MAE) on the untouched validation set. 

## 5. Final Test Evaluation
The selected model was evaluated exactly ONCE on the chronological test set (data after {features['split_boundaries']['test_start']}).

| Model | MAE | RMSE | R² |
|-------|-----|------|----|
| {final['model_name']} | {final['test_metrics']['MAE']:.4f} | {final['test_metrics']['RMSE']:.4f} | {final['test_metrics']['R2']:.4f} |

## 6. Feature Importances
"""
    if final.get('feature_importances'):
        for feat, imp in list(final['feature_importances'].items())[:10]:
            report += f"- **{feat}**: {imp:.4f}\n"
    else:
        report += "Feature importances not available for the selected model architecture.\n"

    report += """
## 7. Known Limitations
1. No explicit historical feature encoding used in baseline (ChargerID/UserID excluded) to avoid data leakage and memorization.
2. The ML model predicts energy demand based solely on session start context; it does not explicitly predict session duration, which would require a multi-task learning approach.
3. Lack of external data (weather, holidays, specific EV types) caps maximum achievable predictive performance.

## 8. Artifacts Generated
- **Cleaned Data**: `data/processed/ChargingRecords_cleaned.csv`
- **Saved Pipeline**: `models/best_model_pipeline.joblib` (Contains Preprocessor + Model)
- **Metadata**: `models/model_metadata.json`
- **Machine-Readable Manifest**: `reports/results/project_manifest.json`

(This concludes Phase 2. The pipeline is ready for backend API integration.)
"""

    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(report)
    print(f"Report written to {report_path}")

if __name__ == '__main__':
    generate_report()

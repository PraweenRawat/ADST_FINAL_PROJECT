# PHASE 2 REPORT — ML Pipeline Implementation

## 1. Data Cleaning Decisions & Results
- **Negative Duration Removed**: 17 rows (EndDatetime < StartDatetime, physically impossible)
- **True Zero Duration Removed**: 404 rows (Start==End AND Duration==0, trivial/failed sessions)
- **Exact Duplicates Removed**: 13 rows (pipeline artifacts)
- **Invalid Demand Removed**: 0 rows (<= 0)
- **Row Counts**: Started with 72856 raw rows -> Resulted in 72422 cleaned rows.
- **Total Removed**: 434 rows (0.596%)

## 2. Feature Engineering

### Final Feature List
- **Numerical/Ordinal**: hour, day_of_week, month, is_weekend, ChargerType, ChargerCompany
- **Categorical (One-Hot Encoded)**: Location
- **Target Variable**: `Demand` (Total energy consumed in kWh per session)

### Excluded Features
- **`UserID`**: High cardinality (2337), 43% anonymous, memorization risk, marginal predictive value (1.5 kWh diff)
- **`ChargerID`**: High cardinality (2119), 250 single-session chargers, excluded from baseline
- **`Duration`**: Only known after session ends — temporal leakage
- **`EndDay`**: Only known after session ends — temporal leakage
- **`EndTime`**: Only known after session ends — temporal leakage
- **`EndDatetime`**: Only known after session ends — temporal leakage
- **`StartDay`**: Raw string; replaced by extracted temporal features (month, day_of_week, is_weekend)
- **`StartTime`**: Raw string; replaced by extracted hour feature
- **`StartDatetime`**: Used as temporal key for splitting; not a model feature
- **`EndDatetime_parsed`**: Derived; excluded (leakage)
- **`StartDatetime_parsed`**: Used for splitting/feature extraction; not passed to model
- **`StartDay_parsed`**: Derived; used for splitting; not passed to model

### Temporal Split Strategy
Chronological splitting by date:
- **Train**: up to 2022-07-16
- **Validation**: 2022-07-17 to 2022-08-13
- **Test**: 2022-08-14 onwards

## 3. EDA & Peak Demand Analytics
(Analytics computed from actual historical data, not ML predictions)

- **Peak Hour (Total Demand)**: 18:00 (119276.41 kWh)
- **Busiest Hour (Sessions)**: 18:00 (6469 sessions)
- **Peak Day of Week**: Sunday (Avg 17.91 kWh/session)
- **Peak Date**: 2022-08-10 (5879.76 kWh total)
- **Weekday vs Weekend**: Weekday average 17.47 kWh vs Weekend average 17.71 kWh

## 4. Model Configurations & Validation Results

Evaluated 3 models using standard configurations:
- Linear Regression (Baseline)
- Decision Tree Regressor (max_depth=10, min_samples_leaf=20)
- Random Forest Regressor (n_estimators=200, max_depth=15, min_samples_leaf=10)

### Validation Metrics
| Model | MAE | RMSE | R² |
|-------|-----|------|----|
| LinearRegression | 10.5485 | 13.7431 | 0.0528 |
| DecisionTreeRegressor | 10.1315 | 13.2209 | 0.1234 |
| RandomForestRegressor | 9.9815 | 13.1248 | 0.1361 |

### Model Selection
**Selected Model**: RandomForestRegressor
**Justification**: Selected strictly based on the lowest Mean Absolute Error (MAE) on the untouched validation set. 

## 5. Final Test Evaluation
The selected model was evaluated exactly ONCE on the chronological test set (data after 2022-08-14).

| Model | MAE | RMSE | R² |
|-------|-----|------|----|
| RandomForestRegressor | 10.0264 | 13.2055 | 0.0747 |

## 6. Feature Importances
- **num__hour**: 0.4363
- **num__month**: 0.1461
- **num__day_of_week**: 0.0994
- **num__ChargerType**: 0.0510
- **num__ChargerCompany**: 0.0409
- **cat__Location_market**: 0.0369
- **cat__Location_hotel**: 0.0270
- **cat__Location_camping**: 0.0262
- **cat__Location_public area**: 0.0240
- **cat__Location_public institution**: 0.0205

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

# Machine Learning Methodology

## 1. Problem Formulation
*   **Target:** Predict the session-level energy consumption in **kWh** (`Demand`).
*   **Objective:** Establish a generalized baseline expectation of load based strictly on the time, date, and location properties available the exact moment an EV connects.

## 2. Feature Selection & Leakage Prevention
Preventing target leakage (using information that is physically impossible to know at inference time) was the highest priority.

### Final Included Features:
*   **Temporal Context:** `hour`, `day_of_week`, `month`, `is_weekend` (extracted strictly from `StartDatetime`).
*   **Station Context:** `ChargerType` (0=AC, 1=DC), `ChargerCompany`, `Location` (14 categorical locations).

### Excluded Features:
*   `Duration`, `EndDatetime`, `EndDay`: Target leakage. A model predicting energy consumption cannot mathematically know how long the driver will leave the car plugged in before the session ends.
*   `UserID`, `ChargerID`: Extremely high cardinality with high proportions of one-off users/chargers. Excluded to force the model to learn general patterns instead of memorizing historical IDs (which fails to generalize to new users).

## 3. Train / Validation / Test Split
To accurately simulate a real-world production deployment, a strict **chronological split** was utilized instead of random sampling.
*   **Train:** Data prior to July 17, 2022 (74.9%)
*   **Validation:** July 17 – Aug 13, 2022 (10.3%)
*   **Test:** Aug 14 – Sep 30, 2022 (14.8%)

## 4. Preprocessing Pipeline
The `scikit-learn` ColumnTransformer was configured as follows:
*   **Categorical:** `OneHotEncoder` applied to `Location`.
*   **Numerical:** `FunctionTransformer` applied as a direct passthrough to the remaining 6 numeric features.
*   *Note: Because tree-based regressors do not rely on Euclidean distance metrics or gradient descent, a StandardScaler was excluded as unnecessary.*

## 5. Model Evaluation
Evaluated entirely on the unseen validation dataset:
1.  **Linear Regression:** MAE: 10.55 kWh | RMSE: 13.74 kWh | R²: 0.0528
2.  **Decision Tree Regressor:** MAE: 10.13 kWh | RMSE: 13.22 kWh | R²: 0.1234
3.  **Random Forest Regressor:** MAE: 9.98 kWh | RMSE: 13.12 kWh | R²: 0.1361

**Selection:** Random Forest was selected for achieving the lowest MAE and highest explained variance on the Validation set.

## 6. Final Test Performance
Evaluated exactly once on the final chronological Test set:
*   **MAE:** 10.0264 kWh
*   **RMSE:** 13.2055 kWh
*   **R²:** 0.0747

## 7. Limitations & Interpretation
The current model should **not** be described as having high accuracy. The low R² metric (approx. 7.5% variance explained) is mathematically accurate and expected. The majority of the variance in EV energy demand is driven by the individual vehicle's starting battery state-of-charge (SoC) and the driver's planned travel distance. Because these variables are entirely untracked, the model can only identify broader temporal and geographical shifts, establishing a baseline expectation rather than a precise prediction.

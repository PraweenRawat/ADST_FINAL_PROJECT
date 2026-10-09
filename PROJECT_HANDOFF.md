# Project Handoff: EV Charging Demand Prediction

## 1. Project Title & Objectives
**Title:** EV Charging Demand Prediction and Peak Demand Analysis
**Problem Statement:** Commercial EV charging stations experience highly variable loads based on location, time, and charger type. Managing this grid load requires predicting session-level energy consumption and analyzing historical peak patterns.
**Objective:** Engineer a complete pipeline from a real-world dataset to a production-ready Web Application (FastAPI + React) that provides peak analytics and machine learning inference for session energy demand.

## 2. Dataset Description & Provenance
*   **Source:** Real-world commercial EV charging records (September 2021 – September 2022).
*   **Original Size:** 72,856 sessions.
*   **Cleaned Size:** 72,422 sessions.
*   **Cleaning Process:** Removed 434 physically impossible or pipeline-artifact rows (negative duration, exact duplicates, and true zero-duration failures). The raw data is preserved.

## 3. ML Methodology
### 3.1 Final Target & Features
*   **Target:** `Demand` (Total session-level energy consumption in **kWh**).
*   **Final Features (7):** `hour`, `day_of_week`, `month`, `is_weekend`, `ChargerType`, `ChargerCompany`, `Location`.
*   **Excluded Features:** 
    *   `Duration`, `EndDatetime`: Target leakage (only known *after* session ends).
    *   `UserID`, `ChargerID`: Extremely high cardinality, excluded to prevent model memorization and guarantee generalizability to unseen users/chargers.
*   **Preprocessing:** `OneHotEncoder` applied strictly to `Location`. Numeric features (`hour`, etc.) are passed through via `FunctionTransformer`. **There is NO StandardScaler.**

### 3.2 Splitting & Evaluation
*   **Split:** Strict chronological split to simulate production (Train: < 2022-07-16 | Val: < 2022-08-13 | Test: >= 2022-08-14).
*   **Models Evaluated:** Linear Regression, Decision Tree Regressor, Random Forest Regressor.
*   **Selected Model:** Random Forest Regressor (Lowest Validation MAE).
*   **Final Test Results (Unseen Data):**
    *   MAE = 10.0264 kWh
    *   RMSE = 13.2055 kWh
    *   R² = 0.0747
*   **Model Artifact:** `models/best_model_pipeline.joblib` (bundles the `ColumnTransformer` and the `RandomForestRegressor`).

## 4. System Architecture
### 4.1 FastAPI Backend
*   **Architecture:** Python + FastAPI + Uvicorn + Pydantic.
*   **Endpoints:**
    *   `GET /api/health`: Health status.
    *   `GET /api/model-info`, `GET /api/model-performance`: Model metadata and metrics.
    *   `POST /api/predict`: Serves the `.joblib` model. Model is loaded exactly once at application startup to avoid repeated disk loading/deserialization overhead per request.
    *   `GET /api/analytics/*`: Serves historical aggregation dynamically from the cleaned `.csv` or manifest.

### 4.2 React Frontend
*   **Architecture:** Vite + React + TypeScript + Tailwind CSS v4 + React Router v6.
*   **Pages:** Dashboard, Predict Demand, Peak Analytics, Model Performance, About.
*   **Integration:** Axios strictly fetches from FastAPI (no mocked data). Recharts visualizes historical hourly/location peaks.
*   **Prediction Flow:** User fills 7-feature form → Axios POST to FastAPI → FastAPI converts Pydantic schema to Pandas DataFrame → Joblib Model predicts kWh → FastAPI returns float → React renders `17.98 kWh/session`.

## 5. Limitations & Future Improvements
*   **Limitations:** The R² score (0.0747) reflects that baseline contextual features (time/location) explain a small fraction of variance. The physical demand is primarily driven by the driver's battery state-of-charge (SoC) and destination needs, which are untracked variables. The model establishes a generalized baseline load expectation rather than a psychic pinpoint prediction.
*   **Future Improvements:** 
    *   Integrate external Weather and Holiday APIs.
    *   Introduce recurrent/sequence models if UserID histories become viable/tracked.
    *   Add multi-task learning to predict `Duration` alongside `Demand`.

## 6. How to Run the Project
1.  **Backend:** Activate `.venv`, run `pip install -r backend/requirements.txt`, then run `python -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8000`.
2.  **Frontend:** Enter `frontend/`, run `npm install`, then run `npm run preview` or `npm run dev`.

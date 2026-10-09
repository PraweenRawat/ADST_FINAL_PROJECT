# EV Charging Demand Prediction & Analytics

![Project Status](https://img.shields.io/badge/Status-Complete-success)

A full-stack machine learning application designed to analyze commercial EV charging patterns, visualize peak demands, and predict session-level energy consumption using context-aware features.

## 📸 Screenshots
*(Insert Dashboard and Predict Demand UI screenshots here)*

## ✨ Features
*   **Peak Demand Analytics**: Identify busiest operational hours, locations, and monthly trends using historical data.
*   **Machine Learning Inference**: Predict energy demand (kWh) per session utilizing a serialized Random Forest Regressor pipeline.
*   **Strict Target Leakage Prevention**: Predictions rely entirely on variables known at the exact start of a session.
*   **Production-Ready Backend**: FastAPI serving a Pydantic-validated endpoint with application-startup model caching.
*   **Modern Interactive UI**: React SPA with Tailwind CSS v4 and Recharts.

## 🏗 Architecture & Tech Stack
*   **Data Science**: Python, Pandas, Scikit-Learn (`RandomForestRegressor`, `ColumnTransformer`, `OneHotEncoder`).
*   **Backend API**: FastAPI, Uvicorn, Pydantic.
*   **Frontend**: React, Vite, TypeScript, Tailwind CSS v4, React Router, Recharts, Axios.

## 🔬 ML Methodology & Results
*   **Target**: Session energy consumption (`Demand` in kWh).
*   **Split**: Chronological (Train: Sep '21–Jul '22 | Val: Jul '22–Aug '22 | Test: Aug '22–Sep '22).
*   **Final Features**: `hour`, `day_of_week`, `month`, `is_weekend`, `ChargerType`, `ChargerCompany`, `Location`.
*   **Final Test Results**:
    *   **MAE**: 10.0264 kWh
    *   **RMSE**: 13.2055 kWh
    *   **R²**: 0.0747

*Note: The model establishes a generalized baseline expectation based on time and location. The low R² accurately reflects that the majority of demand variance is driven by individual EV battery states (SoC) and driver intent, which are untracked to prevent memorization/leakage.*

## 🚀 Setup & Installation

### Prerequisites
*   Python 3.10+
*   Node.js 18+

### 1. Backend Startup
```bash
# From the project root, activate your virtual environment
# e.g., .\.venv\Scripts\Activate.ps1
pip install -r backend/requirements.txt
# Start the FastAPI server
python -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8000
```
*API Documentation will be available at `http://127.0.0.1:8000/docs`*

### 2. Frontend Startup
```bash
cd frontend
npm install
npm run dev
# The application will run on http://localhost:5173
```

## 🔌 API Usage Example
**POST `/api/predict`**
```bash
curl -X 'POST' \
  'http://127.0.0.1:8000/api/predict' \
  -H 'Content-Type: application/json' \
  -d '{
  "hour": 18,
  "day_of_week": 6,
  "month": 8,
  "is_weekend": 1,
  "ChargerType": 1,
  "ChargerCompany": 1,
  "Location": "public area"
}'
```
**Response:**
```json
{
  "predicted_kwh": 17.98,
  "model_name": "RandomForestRegressor"
}
```

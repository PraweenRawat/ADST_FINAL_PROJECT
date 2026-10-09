# API Contract — EV Charging Demand Predictor

## Base URL
`http://localhost:8000`

---

## 1. System Endpoints

### 1.1 `GET /api/health`
Checks backend health and model load status.

**Response (200 OK):**
```json
{
  "status": "ok",
  "model_loaded": true,
  "api_version": "1.0.0"
}
```

### 1.2 `GET /api/model-info`
Returns ML model metadata and evaluation contexts.

**Response (200 OK):**
```json
{
  "model_name": "RandomForestRegressor",
  "target": "Demand",
  "expected_features": [
    "hour", "day_of_week", "month", "is_weekend", "ChargerType", "ChargerCompany", "Location"
  ],
  "validation_metrics": { "MAE": 9.9815, "RMSE": 13.1248, "R2": 0.1361 },
  "test_metrics": { "MAE": 10.0264, "RMSE": 13.2055, "R2": 0.0747 },
  "training_period": "up to 2022-07-16",
  "validation_period": "2022-07-17 to 2022-08-13",
  "test_period": "2022-08-14 onwards"
}
```

### 1.3 `GET /api/model-performance`
Returns only the validation and test metrics.

---

## 2. Inference Endpoint

### 2.1 `POST /api/predict`
Predict the energy demand (kWh) for a charging session.

**Request Body:**
```json
{
  "hour": 18,
  "day_of_week": 6,
  "month": 8,
  "is_weekend": 1,
  "ChargerType": 1,
  "ChargerCompany": 1,
  "Location": "public area"
}
```

**Validation Rules:**
- `hour`: int (0-23)
- `day_of_week`: int (0-6)
- `month`: int (1-12)
- `is_weekend`: int (0-1)
- `ChargerType`: int (0-1) (0=Slow, 1=Fast)
- `ChargerCompany`: int (0-1)
- `Location`: string

**Response (200 OK):**
```json
{
  "predicted_kwh": 17.98,
  "model_name": "RandomForestRegressor"
}
```

**Response (422 Unprocessable Entity) - Validation Error:**
```json
{
  "detail": [
    {
      "loc": ["body", "hour"],
      "msg": "Input should be less than or equal to 23",
      "type": "less_than_equal"
    }
  ]
}
```

---

## 3. Analytics Endpoints

### 3.1 `GET /api/analytics/summary`
Overall historical statistics.

**Response (200 OK):**
```json
{
  "total_sessions": 72422,
  "total_demand_kwh": 1269736.39,
  "avg_demand_kwh": 17.53,
  "unique_chargers": 2116,
  "unique_locations": 14
}
```

### 3.2 `GET /api/analytics/hourly`
Aggregated stats by hour of day (0-23).

### 3.3 `GET /api/analytics/location`
Aggregated stats by location.

### 3.4 `GET /api/analytics/monthly`
Aggregated stats by month.

### 3.5 `GET /api/analytics/peak`
Pre-computed peak demand findings (busiest hour, peak dates).

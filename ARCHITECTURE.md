# System Architecture

This document maps the data flow and integration architecture across the three tiers of the EV Charging Demand project.

## 1. Machine Learning Pipeline Architecture

```mermaid
flowchart TD
    A[Raw Dataset: ChargingRecords.csv] --> B[Data Cleaning]
    B --> |Drop negative/zero duration| C[Cleaned Dataset]
    C --> D[Feature Engineering]
    
    subgraph scikit-learn Pipeline
    D --> |Target Leakage Excluded| E[Chronological Split]
    E --> |Train/Val/Test| F[ColumnTransformer]
    F --> |Location| G[OneHotEncoder]
    F --> |Numeric| H[FunctionTransformer passthrough]
    G --> I[RandomForestRegressor]
    H --> I
    end
    
    I --> J[best_model_pipeline.joblib]
    I --> K[project_manifest.json]
```

## 2. Inference Architecture

```mermaid
flowchart LR
    A[React Form] --> |JSON Payload| B[Axios HTTP POST]
    B --> C[FastAPI /api/predict]
    C --> |Pydantic Validation| D[Pandas DataFrame]
    
    subgraph Backend Memory
    E[best_model_pipeline.joblib] --> |Loaded at Startup| F[ModelService]
    end
    
    D --> F
    F --> |Float prediction| C
    C --> |JSON Response| A
```

## 3. Analytics Architecture

```mermaid
flowchart LR
    A[React Analytics Page] --> |HTTP GET| B[FastAPI /api/analytics/*]
    
    subgraph Backend Memory
    C[Cleaned Dataset .csv] --> |Loaded at Startup| D[AnalyticsService]
    E[project_manifest.json] --> D
    end
    
    D --> |Pandas GroupBy & Aggregation| B
    B --> |JSON Array| A
    A --> |Recharts Components| F[Rendered UI Charts]
```

## Architectural Design Decisions
1. **No Database:** Due to the static nature of the historical dataset, analytics are processed dynamically in memory using `pandas` rather than deploying an unnecessary relational database.
2. **Model Caching:** The `.joblib` model is deserialized into memory once during the Uvicorn application startup event. This prevents repeated disk I/O and deserialization penalties on every API request.
3. **Strict Boundaries:** The FastAPI layer acts strictly as a validation and communication bridge. It does not perform internal feature engineering. The `joblib` pipeline contains the mathematical transformations.

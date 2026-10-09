# Frontend Architecture

This document describes the structure and behavior of the React web application built in Phase 4.

## 1. Technology Stack
*   **Framework:** React 18
*   **Build Tool:** Vite
*   **Language:** TypeScript
*   **Styling:** Tailwind CSS v4 (via `@tailwindcss/postcss`)
*   **Routing:** React Router DOM v6
*   **Data Fetching:** Axios
*   **Visualizations:** Recharts
*   **Icons:** Lucide React

## 2. Directory Structure
```text
frontend/
├── src/
│   ├── api.ts                  # Axios configuration with VITE_API_BASE_URL
│   ├── App.tsx                 # Router definition and route mapping
│   ├── index.css               # Tailwind v4 @import entrypoint
│   ├── main.tsx                # React DOM render tree
│   ├── components/
│   │   └── Layout.tsx          # Responsive Sidebar and Mobile Header wrapper
│   └── pages/
│       ├── Dashboard.tsx       # Summary KPI cards
│       ├── Predict.tsx         # User input form and prediction output
│       ├── Analytics.tsx       # Recharts visualizations
│       ├── Performance.tsx     # ML metrics display
│       └── About.tsx           # Static methodology context
```

## 3. Data Integration Rules
*   **No Mock Data:** The frontend contains absolutely no hardcoded business logic or dataset statistics.
*   **Prediction Flow:** 
    1. The user fills out the strictly-typed form in `Predict.tsx`.
    2. Axios triggers a `POST` to `/api/predict`.
    3. The application intercepts standard errors (e.g. `HTTP 422` from Pydantic) or successful JSON payloads containing `predicted_kwh`.
    4. The UI renders the raw numerical result alongside the model's test MAE/R² fetched concurrently from `/api/model-performance`.
*   **Analytics Flow:** `Dashboard.tsx` and `Analytics.tsx` fire simultaneous `GET` requests using `Promise.all` to fetch aggregations dynamically from the FastAPI backend, updating state only when complete to safely manage loading/error boundaries.

## 4. UI States
Every API-dependent component properly manages three states to guarantee a stable user experience:
*   `loading`: Displays placeholder text/spinners while Axios promises are pending.
*   `error`: Catches and cleanly renders HTTP error details inside red alert boxes.
*   `data`: Safely renders Recharts or KPI cards only when the payload is confirmed non-null.

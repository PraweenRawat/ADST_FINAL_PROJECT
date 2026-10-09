# Docker Deployment Guide

This guide explains how to build and run the completely containerized EV Charging Demand Prediction stack using Docker Compose.

## 1. Prerequisites
*   **Docker Engine** (v20.10+ recommended)
*   **Docker Compose** (v2.0+ recommended)
*   Ensure ports `80` and `8000` are available on your host.

## 2. Architecture
The stack consists of two isolated containers:
1.  **backend**: Python 3.10 slim container running the FastAPI Uvicorn server on port 8000. It bundles the `joblib` model and cleaned dataset artifacts.
2.  **frontend**: Nginx Alpine container serving the React/Vite static production build on port 80, configured to reverse-proxy `/api` requests to the internal backend container.

## 3. Configuration & Environment Variables
*   **Frontend**: `VITE_API_BASE_URL` is set to `/api` at build time (via `.env.production`) to leverage the Nginx proxy, bypassing CORS and resolving correctly inside the browser.
*   **Backend**: `PYTHONUNBUFFERED=1` is injected to ensure Uvicorn logs stream instantly to the console.

## 4. Building the Stack
Run the following from the project root (where `docker-compose.yml` is located):
```bash
docker compose build
```
This will compile the React application via a multi-stage Node build and construct the Python environment without carrying over your local `.venv`.

## 5. Starting the Stack
```bash
docker compose up -d
```
*   The frontend dashboard will be available at: `http://localhost:80`
*   The backend API docs will be available at: `http://localhost:8000/docs`

## 6. Stopping the Stack
To stop and cleanly remove the containers and default bridge network:
```bash
docker compose down
```

## 7. Troubleshooting
*   **Port Conflicts**: If port `80` is in use, modify the `ports:` mapping under the `frontend` service in `docker-compose.yml` (e.g., `"8080:80"`).
*   **Model Not Found Error**: Ensure the `./models/best_model_pipeline.joblib` exists on your host *before* running `docker compose build`, as it is copied directly into the image.
*   **Empty Analytics**: Ensure `./data/processed/ChargingRecords_cleaned.csv` and `./reports/results/project_manifest.json` exist locally before building.

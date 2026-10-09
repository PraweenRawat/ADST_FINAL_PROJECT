# EV Charging Demand Backend

This is the FastAPI backend for the EV Charging Demand Prediction ML pipeline.

## Structure
- `app/main.py`: FastAPI entrypoint.
- `app/schemas/`: Pydantic input/output validation.
- `app/services/`: Loads the Phase 2 Joblib models and processes historical analytics.
- `tests/`: Pytest suite for the API endpoints.

## Setup
It is assumed you have Python 3.10+ and have already run the Phase 2 ML pipeline to generate the models and data.

1. Activate your virtual environment (e.g., `../.venv/Scripts/Activate.ps1`).
2. Install dependencies: `pip install -r requirements.txt`
3. Run the development server: `uvicorn app.main:app --reload`
4. Access the auto-generated Swagger UI at `http://localhost:8000/docs`.

## Tests
Run the test suite via `pytest`:
```bash
pytest tests/
```

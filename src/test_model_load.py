import sys
import pandas as pd
import joblib

def check_model():
    model_path = r"C:\Users\prawe\.gemini\antigravity\scratch\EV_Charging_Demand_Project\models\best_model_pipeline.joblib"
    try:
        pipeline = joblib.load(model_path)
        print("Model loaded successfully!")
        
        print("\nPipeline Steps:")
        for name, step in pipeline.named_steps.items():
            print(f"- {name}: {type(step).__name__}")
            
        preprocessor = pipeline.named_steps['preprocessor']
        
        # Get categorical/numerical columns from the transformers
        cat_cols = []
        num_cols = []
        for name, transformer, cols in preprocessor.transformers_:
            if name == 'cat':
                cat_cols = cols
            elif name == 'num':
                num_cols = cols
                
        print("\nExpected Input Columns:")
        print(f"Categorical: {cat_cols}")
        print(f"Numerical: {num_cols}")
        print(f"Total Columns Expected: {len(cat_cols) + len(num_cols)}")
        
        # Test prediction with a dummy row
        dummy_data = pd.DataFrame({
            'hour': [18],
            'day_of_week': [6],
            'month': [8],
            'is_weekend': [1],
            'ChargerType': [0],
            'ChargerCompany': [1],
            'Location': ['apartment']
        })
        
        pred = pipeline.predict(dummy_data)
        print(f"\nPrediction output type: {type(pred)}")
        print(f"Prediction output value: {pred[0]}")
        
    except Exception as e:
        print(f"Failed to load model or predict: {e}")

if __name__ == "__main__":
    check_model()

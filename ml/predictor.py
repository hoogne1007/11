import os
import joblib
import pandas as pd
import numpy as np
from ml.data_loader import load_and_preprocess_data

def get_latest_model_path():
    """Finds the most recently trained model file in the models directory."""
    model_dir = 'models'
    if not os.path.exists(model_dir):
        return None
    
    files = [f for f in os.listdir(model_dir) if f.endswith('.joblib')]
    if not files:
        return None
        
    latest_file = sorted(files, reverse=True)[0]
    return os.path.join(model_dir, latest_file)

def generate_prediction_data(num_months=6):
    """
    Loads the latest model and generates a forecast for a specified number of months.
    """
    # 1. Load the latest model
    model_path = get_latest_model_path()
    if not model_path:
        return {
            "error": "No trained model found. Please train a model first on the 'Prediction' tab.",
            "historical_x": [], "historical_y": [], "predicted_x": [], "predicted_y": [],
            "next_quarter_prediction": "N/A", "model_performance": {}, "feature_weights": {},
            "data_quality_score": 0
        }
    
    try:
        model_payload = joblib.load(model_path)
        model = model_payload['model']
        model_features = model_payload['features']
        scaler = model_payload.get('scaler')
        
        model_performance = model_payload.get('performance', {'RMSE': 'N/A'})
        feature_weights = model_payload.get('importances', {})
    except (EOFError, ValueError, KeyError) as e:
        print(f"Error loading model file {model_path}: {e}")
        return {
            "error": f"Corrupt model file found. Please retrain the model.",
            "historical_x": [], "historical_y": [], "predicted_x": [], "predicted_y": [],
            "next_quarter_prediction": "N/A", "model_performance": {}, "feature_weights": {},
            "data_quality_score": 0
        }
    
    # 2. Load historical data
    df_hist = load_and_preprocess_data()
    if df_hist is None:
        return {"error": "Could not load historical data."}

    # 3. Create future dates
    last_date = df_hist['Date'].max()
    future_dates = pd.date_range(start=last_date, periods=num_months + 1, freq='MS')[1:] 
    
    df_future = pd.DataFrame({'Date': future_dates})
    df_future['Year'] = df_future['Date'].dt.year
    df_future['Month'] = df_future['Date'].dt.month
    df_future['Quarter'] = df_future['Date'].dt.quarter
    df_future['DayOfYear'] = df_future['Date'].dt.dayofyear
    df_future['WeekOfYear'] = df_future['Date'].dt.isocalendar().week.astype(int)
    
    # --- Simple feature estimation for future (Updated here) ---
    df_future['MarketingSpend'] = df_hist['MarketingSpend'].mean() * 1.1 
    
    # Энд шинэ баганыг нэмэв: Түүхэн дунджаас 5% өсөлттэй байхаар тооцов
    if 'EmployeeBenefits' in df_hist.columns:
        df_future['EmployeeBenefits'] = df_hist['EmployeeBenefits'].mean() * 1.05
    else:
        df_future['EmployeeBenefits'] = 0 # Хэрэв багана байхгүй бол 0 утга өгнө
        
    df_future['IsHoliday'] = [1 if m in [1, 5, 7, 12] else 0 for m in df_future['Month']]
    # ----------------------------------------------------------
    
    # 4. Make predictions
    # model_features дотор 'EmployeeBenefits' орсон байх тул df_future-ээс шууд авна
    X_future_df = df_future[model_features]
    
    if scaler:
        X_future_scaled = scaler.transform(X_future_df)
        future_predictions = model.predict(X_future_scaled)
    else:
        future_predictions = model.predict(X_future_df.values)

    # For charting
    historical_x = np.arange(len(df_hist))
    predicted_x = np.arange(len(df_hist), len(df_hist) + len(df_future))
    
    next_q_val = sum(future_predictions[:3])
    
    return {
        "historical_x": historical_x,
        "historical_y": df_hist['Sales'],
        "predicted_x": predicted_x,
        "predicted_y": future_predictions,
        "next_quarter_prediction": f"{next_q_val/1000:.1f}K",
        "model_performance": model_performance,
        "feature_weights": feature_weights,
        "data_quality_score": 98,
        "error": None
    }
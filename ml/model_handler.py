import os
import time
import joblib
import numpy as np
from sklearn.neural_network import MLPRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import GradientBoostingRegressor, RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, r2_score
import itertools

from ml.data_loader import load_and_preprocess_data

FEATURE_MAP = {
    "Historical Sales Data": ["Year", "Month", "Quarter", "DayOfYear", "WeekOfYear"],
    "Economic Indicators": ["MarketingSpend"], # Placeholder for real economic data
    "Competitor Activity": ["IsHoliday"], # Placeholder
    "Website Traffic": [] # Placeholder
}

def train_model(selected_features_list, algorithm_choice, hyperparameters):
    """
    Trains a real machine learning model and saves it.
    """
    print("--- Starting Real Model Training ---")
    print(f"Algorithm: {algorithm_choice}")
    print(f"Features: {selected_features_list}")
    print(f"Hyperparameters: {hyperparameters}")
    
    # 1. Load Data
    df = load_and_preprocess_data()
    if df is None:
        return {"error": "Failed to load data."}
 # --- BUILD THE FEATURE LIST DYNAMICALLY ---
    features_to_use = []
    for feature_name in selected_features_list:
        features_to_use.extend(FEATURE_MAP.get(feature_name, []))
    
    # Remove duplicates
    features_to_use = sorted(list(set(features_to_use)))

    if not features_to_use:
        return {"error": "No features selected for training."}
    
    print(f"Model will use columns: {features_to_use}")
    
    target = 'Sales'
    X = df[features_to_use]
    y = df[target]

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, shuffle=False)
    
    # 1. Initialize the Scaler
    scaler = StandardScaler()
    
    # 2. Fit the scaler on the TRAINING data and transform it
    X_train_scaled = scaler.fit_transform(X_train)
    
    # 3. Transform the TEST data using the SAME fitted scaler
    X_test_scaled = scaler.transform(X_test)


    # --- SELECT MODEL BASED ON UI CHOICE ---
    if algorithm_choice == "Random Forest":
        model = RandomForestRegressor(
            n_estimators=hyperparameters.get('n_estimators', 100),
            random_state=42
        )
    elif algorithm_choice == "Neural Network":
        print("Training a Neural Network...")
        # MLPRegressor has different hyperparameters. Will use defaults for now.
        model = MLPRegressor(
            hidden_layer_sizes=(64, 32),
            max_iter=500,
            activation='relu',
            solver='adam',
            random_state=42
        )
    else:
        model = GradientBoostingRegressor(
            n_estimators=hyperparameters.get('n_estimators', 100),
            random_state=42
        )
    
    model.fit(X_train_scaled, y_train)
    print("Model fitting complete.")
    
    predictions = model.predict(X_test_scaled)
    rmse = np.sqrt(mean_squared_error(y_test, predictions))
    r2 = r2_score(y_test, predictions)
    print(f"Model evaluation RMSE: {rmse:.2f}, R2 Score: {r2:.2f}")

    # 5. Save the Trained Model
    model_dir = 'models'
    if not os.path.exists(model_dir):
        os.makedirs(model_dir)
    
    performance_metrics = {
        'RMSE': f"{rmse:,.0f}",
        'R2 Score': f"{r2:.2f}"
    }
    
    feature_importances = {}
    if hasattr(model, 'feature_importances_'):
        importances = model.feature_importances_
        # Pair feature names with their importance scores
        feature_importances = dict(zip(features_to_use, importances))
        # Sort by importance for better display
        feature_importances = {k: v for k, v in sorted(feature_importances.items(), key=lambda item: item[1], reverse=True)}
        
    model_payload = {
        'model': model,
        'features': features_to_use,
        'scaler': scaler,
        'performance': performance_metrics,
        'importances': feature_importances
    }
    
    timestamp = time.strftime("%Y%m%d-%H%M%S")
    model_filename = f"sales_model_{timestamp}.joblib"
    model_path = os.path.join(model_dir, model_filename)
    joblib.dump(model_payload, model_path)
    print(f"Model and features saved to {model_path}")

    # 6. Return results for the UI
    return {
        "rmse": f"{rmse:,.0f}",
        "model_id": model_filename,
        "features_used": features_to_use
    }
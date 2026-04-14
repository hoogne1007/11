import pandas as pd

def load_and_preprocess_data(filepath='data/historical_sales.csv'):
    """
    Loads sales data from a CSV and performs feature engineering.
    """
    try:
        df = pd.read_csv(filepath, parse_dates=['Date'])
    except FileNotFoundError:
        print(f"Error: Data file not found at {filepath}")
        return None

    # Feature Engineering from the date
    df['Year'] = df['Date'].dt.year
    df['Month'] = df['Date'].dt.month
    df['Quarter'] = df['Date'].dt.quarter
    df['DayOfYear'] = df['Date'].dt.dayofyear   
    df['WeekOfYear'] = df['Date'].dt.isocalendar().week.astype(int)

    
    print("Data loaded and preprocessed successfully.")
    return df
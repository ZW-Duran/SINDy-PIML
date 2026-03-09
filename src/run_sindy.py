import pandas as pd
import numpy as np
import pysindy as ps
import matplotlib.pyplot as plt
import sys
import glob
import os

def load_and_clean_data(filepath):
    print(f"Readfile: {filepath} ...")
    df = pd.read_csv(filepath)
    print(f"Loaded, shape: {df.shape}")
    return df

def run_sindy_analysis(df):
    state_cols = ['SPEED', 'G_LAT', 'G_LON', 'ROTY']
    control_cols = ['STEERANGLE', 'THROTTLE', 'BRAKE']
    
    missing = [c for c in state_cols + control_cols if c not in df.columns]
    if missing:
        print(f"Error: missing columns: {missing}")
        return None, None

    X = df[state_cols].values
    U = df[control_cols].values

    time_col = None
    for col in ['Time', 'time', 't', 'Timestamp']:
        if col in df.columns:
            time_col = col
            break
    
    if time_col:
        t = df[time_col].values
        print(f"Using column '{time_col}' as time axis.")
    else:
        dt = 0.005 # 200Hz sampling
        t = dt
        print(f"Time column not found, using default time step dt={dt}.")

    #aerodynamic terms often have small coefficients due to V^2 scaling, so we use a low threshold to retain them
    feature_library = ps.PolynomialLibrary(degree=2)
    optimizer = ps.STLSQ(threshold=1e-4)
    model = ps.SINDy(feature_library=feature_library, optimizer=optimizer)
    
    print("pySINDy is running：")
    model.fit(x=X, u=U, t=t)
    
    # Output
    print("\nvar:")
    print("--- IV (x) ---")
    for i, name in enumerate(state_cols):
        print(f"x{i} -> {name}")
    print("--- DV (u) ---")
    for i, name in enumerate(control_cols):
        print(f"u{i} -> {name}")

    print("\nrecognized functions:")
    model.print()
    
    # R^2
    score = model.score(X, u=U, t=t)
    print(f"\nModel R^2 score: {score:.4f}")
    
    return model, score

if __name__ == "__main__":
    # read pre-processed data
    # Allow passing file path via command line arguments
    file_path = None
    if len(sys.argv) > 1:
        file_path = sys.argv[1]
    else:
        # Default: try processed_data first
        processed_files = glob.glob('processed_data/*.csv')
        if processed_files:
            file_path = max(processed_files, key=os.path.getmtime)
        else:
            # Fallback: try data (raw)
            data_files = glob.glob('data/*.csv')
            if data_files:
                file_path = max(data_files, key=os.path.getmtime)
                print("Warning: run on original data")
            else:
                print("Error: No data found in ./processed_data or ./data")
                sys.exit(1)

    try:
        data = load_and_clean_data(file_path)
        model, score = run_sindy_analysis(data)
    except FileNotFoundError:
        print(f"Error: File not found {file_path}, please confirm the file path.")
    except Exception as e:
        print(f"error: {e}")
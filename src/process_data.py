import pandas as pd
import numpy as np
import os
import sys
import glob
from scipy.signal import savgol_filter

def load_raw_motec_data(filepath):
    print(f"read the file: {filepath} ...")
    
    # Title (Line 15)
    header_df = pd.read_csv(filepath, skiprows=14, nrows=1, header=None, sep=None, engine='python')
    columns = header_df.iloc[0].astype(str).str.strip().tolist()
    
    # Data (Line 19 onwards)
    df = pd.read_csv(filepath, skiprows=18, header=None, names=columns, sep=None, engine='python')
    
    df = df.apply(pd.to_numeric, errors='coerce')
    df.dropna(inplace=True)
    
    # Column selection
    target_cols = ['Time', 'STEERANGLE', 'THROTTLE', 'BRAKE', 'SPEED', 'G_LAT', 'G_LON', 'ROTY']
    existing_cols = [col for col in target_cols if col in df.columns]
    
    if not existing_cols:
        raise ValueError(f"Column not found, current columns: {df.columns.tolist()}") #for debugging
        
    df = df[existing_cols].copy()

    # unit conversion
    if 'STEERANGLE' in df.columns:
        df['STEERANGLE'] = df['STEERANGLE'] * (np.pi / 180.0) # deg -> rad
    if 'ROTY' in df.columns:
        df['ROTY'] = df['ROTY'] * (np.pi / 180.0) # deg/s -> rad/s
    if 'SPEED' in df.columns:
        df['SPEED'] = df['SPEED'] / 3.6 # km/h -> m/s

    return df

def apply_savgol_filter(df):
    """
    Apply Savitzky-Golay filter to smooth the data
    """
    #exclude time columns from filtering
    cols_to_filter = [c for c in df.columns if c not in ['Time', 'Timestamp', 't']]
    
    # 200Hz sampling, so window length should be odd and cover a reasonable time span (e.g., 0.1s -> 21 samples)
    window_length = 21
    polyorder = 3
    
    print(f"Applying Savitzky-Golay filter (Window={window_length}, Poly={polyorder}) to columns: {cols_to_filter}")
    
    for col in cols_to_filter:
        df[col] = savgol_filter(df[col], window_length, polyorder)
        
    return df

if __name__ == "__main__":
    # raw data file path
    if len(sys.argv) > 1:
        raw_file_path = sys.argv[1]
    else:
        # Default to the first file in ./data
        files = glob.glob('data/*.csv')
        if not files:
            print("Error: No .csv files found in ./data/")
            sys.exit(1)
        # Sort by modification time and pick the newest
        raw_file_path = max(files, key=os.path.getmtime)

    # output path for cleaned data
    output_dir = 'processed_data'
    filename = os.path.basename(raw_file_path)
    name, ext = os.path.splitext(filename)
    output_file = os.path.join(output_dir, f"{name}_cleaned{ext}")
    
    try:
        print(f"Processing file: {raw_file_path}")
        df = load_raw_motec_data(raw_file_path)
        df_clean = apply_savgol_filter(df)
        os.makedirs(output_dir, exist_ok=True)
        df_clean.to_csv(output_file, index=False)
        print(f"Processing complete! Data saved to: {output_file}")
        
    except Exception as e:
        print(f"Error: {e}")
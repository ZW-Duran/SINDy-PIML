import subprocess
import sys
import os
import glob

def run_task(step_name, script_path, args=None):
    print(f"\n{'='*20}")
    print(f"Execute: {step_name}")
    print(f"{'='*20}")

    abs_path = os.path.abspath(script_path)
    cmd = [sys.executable, abs_path]
    if args:
        cmd.extend(args)
    
    result = subprocess.run(cmd)
    
    if result.returncode == 0:
        print(f"{step_name} Finished！")
    else:
        print(f"Failed at {step_name} ")
        sys.exit(1)

if __name__ == "__main__":
    # 1. Determine the raw file path
    if len(sys.argv) > 1:
        raw_file_path = sys.argv[1]
    else:
        # Default: Find the newest file in ./data
        data_files = glob.glob('data/*.csv')
        if not data_files:
            print("Error: No .csv files found in ./data/")
            sys.exit(1)
        raw_file_path = max(data_files, key=os.path.getmtime)

    print(f"Target Raw File: {raw_file_path}")

    # 2. Determine the expected cleaned file path (must match logic in process_data.py)
    filename = os.path.basename(raw_file_path)
    name, ext = os.path.splitext(filename)
    cleaned_file_path = os.path.join('processed_data', f"{name}_cleaned{ext}")

    tasks = [
        ("SG_Filter", "src/process_data.py", [raw_file_path]),
        ("SINDy modeling", "src/run_sindy.py", [cleaned_file_path])
    ]

    for step_name, script_path, args in tasks:
        run_task(step_name, script_path, args)

    print("\n Done！")
import json
import os

# Path to the metrics file
file_path = r"c:/Users/Lenovo/OneDrive/Desktop/6TH SEM/case study/case study/EBPT_CRA/master_results_final/metrics_seed_0.json"
top_tier_path = r"c:/Users/Lenovo/OneDrive/Desktop/6TH SEM/case study/case study/EBPT_CRA/top_tier_results"

print(f"--- Inspecting {file_path} ---")
try:
    with open(file_path, 'r') as f:
        data = json.load(f)
        print("Keys:", data.keys())
        if 'rounds' in data:
            print(f"Number of rounds: {len(data['rounds'])}")
            # Check if there are other lists of the same length
            for key in data:
                if isinstance(data[key], list):
                    print(f"Key '{key}': List of length {len(data[key])}")
                    if len(data[key]) > 0:
                        print(f"  Sample values: {data[key][:5]}...")
        else:
            print("No 'rounds' key found.")
except Exception as e:
    print(f"Error reading file: {e}")

print(f"\n--- Inspecting {top_tier_path} ---")
try:
    if os.path.exists(top_tier_path):
        print(f"Directory exists. Contents:")
        for item in os.listdir(top_tier_path):
            print(f" - {item}")
    else:
        print("Directory does not exist.")
except Exception as e:
    print(f"Error listing directory: {e}")

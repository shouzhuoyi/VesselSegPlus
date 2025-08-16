import json
import os
from collections import defaultdict
import yaml

with open("config.yaml", "r", encoding="utf-8") as f:
    cfg = yaml.safe_load(f)

BASE_PATH = cfg["output_dir"]
MODEL_NAMES = ["unet", "unetpp", "wnet"]

def load_json(path):
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)

def calculate_global_averages(data):
    sums = defaultdict(float)
    counts = defaultdict(int)
    for image_name, image_metrics in data.items():
        for key, value in image_metrics.items():
            if value > 1000:
                continue
            sums[key] += value
            counts[key] += 1
    averages = {key: (sums[key] / counts[key]) if counts[key] > 0 else None for key in sums}
    return averages

def main():
    for model in MODEL_NAMES:
        input_file = os.path.join(BASE_PATH, f"deviation_3VV_from_csv_{model}.json")
        output_file = os.path.join(BASE_PATH, f"deviation_3VV_global_averages_1_{model}.json")

        print(f"\nProcessing model: {model}")
        data = load_json(input_file)
        avg_results = calculate_global_averages(data)

        for key, val in sorted(avg_results.items()):
            print(f"{key}: {val:.4f}")

        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(avg_results, f, indent=4, ensure_ascii=False)
        print(f"Averages saved to: {output_file}")

if __name__ == "__main__":
    main()
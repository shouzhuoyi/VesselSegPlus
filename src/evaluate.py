import json
import os
import math
import csv
import yaml

with open("config.yaml", "r", encoding="utf-8") as f:
    cfg = yaml.safe_load(f)

GROUPS_PATH = cfg["groups_path"]
OUTPUT_DIR = cfg["output_dir"]
MODEL_FILES = cfg["model_files"]

def load_json(path):
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_json(data, path):
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

def load_csv_measurements(path):
    results = {}
    with open(path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            filename = row['filename']
            results[filename] = {
                'diameter_AO': float(row['diameter_AO']),
                'diameter_PA': float(row['diameter_PA']),
                'AO_point1': (float(row['AO_point1_x']), float(row['AO_point1_y'])) if row['AO_point1_x'] and row['AO_point1_y'] else None,
                'AO_point2': (float(row['AO_point2_x']), float(row['AO_point2_y'])) if row['AO_point2_x'] and row['AO_point2_y'] else None,
                'PA_point1': (float(row['PA_point1_x']), float(row['PA_point1_y'])) if row['PA_point1_x'] and row['PA_point1_y'] else None,
                'PA_point2': (float(row['PA_point2_x']), float(row['PA_point2_y'])) if row['PA_point2_x'] and row['PA_point2_y'] else None,
            }
    return results

def euclidean_distance(p1, p2):
    return math.sqrt((p1[0] - p2[0]) ** 2 + (p1[1] - p2[1]) ** 2)

def pointwise_distance_error(gt_points, pred_points):
    d1 = euclidean_distance(gt_points[0], pred_points[0]) + euclidean_distance(gt_points[1], pred_points[1])
    d2 = euclidean_distance(gt_points[0], pred_points[1]) + euclidean_distance(gt_points[1], pred_points[0])
    return min(d1, d2)

def calculate_expert_errors(experts_data):
    pairs = [(1, 2), (1, 3), (2, 3)]
    errors = {}
    for (a, b) in pairs:
        key_a_red = f"expert{a}_red"
        key_b_red = f"expert{b}_red"
        key_a_green = f"expert{a}_green"
        key_b_green = f"expert{b}_green"

        if key_a_red in experts_data and key_b_red in experts_data:
            len_err_red = abs(
                euclidean_distance(*experts_data[key_a_red]) -
                euclidean_distance(*experts_data[key_b_red])
            )
            pt_err_red = euclidean_distance(experts_data[key_a_red][0], experts_data[key_b_red][0]) + \
                         euclidean_distance(experts_data[key_a_red][1], experts_data[key_b_red][1])
            errors[f"expert{a}vs{b}_length_aorta"] = len_err_red
            errors[f"expert{a}vs{b}_point_aorta"] = pt_err_red

        if key_a_green in experts_data and key_b_green in experts_data:
            len_err_green = abs(
                euclidean_distance(*experts_data[key_a_green]) -
                euclidean_distance(*experts_data[key_b_green])
            )
            pt_err_green = euclidean_distance(experts_data[key_a_green][0], experts_data[key_b_green][0]) + \
                           euclidean_distance(experts_data[key_a_green][1], experts_data[key_b_green][1])
            errors[f"expert{a}vs{b}_length_pulmonary_artery"] = len_err_green
            errors[f"expert{a}vs{b}_point_pulmonary_artery"] = pt_err_green

    return errors

def process_one_model(meas_path, model_name, groups, output_dir):
    meas_data = load_csv_measurements(meas_path)
    all_errors = {}

    for image_name in meas_data:
        try:
            image_key = os.path.splitext(image_name)[0]
            results = {}

            diameter_ao = meas_data[image_name]['diameter_AO']
            diameter_pa = meas_data[image_name]['diameter_PA']
            ao_model_pts = [meas_data[image_name]['AO_point1'], meas_data[image_name]['AO_point2']]
            pa_model_pts = [meas_data[image_name]['PA_point1'], meas_data[image_name]['PA_point2']]

            experts_data = {}

            for i in range(1, 4):
                group_key = f"group{i}"
                red_points = None
                green_points = None

                for item in groups[group_key]["items"]:
                    if isinstance(item, dict) and 'id' in item:
                        expert_image_key = os.path.basename(item['id']).split('/')[-1]
                        if expert_image_key in image_key or image_key in expert_image_key:
                            for annotation in item['annotations']:
                                if annotation['label_id'] == 0:
                                    pts = annotation['points']
                                    if len(pts) >= 4:
                                        green_points = [[pts[0], pts[1]], [pts[2], pts[3]]]
                                elif annotation['label_id'] == 1:
                                    pts = annotation['points']
                                    if len(pts) >= 4:
                                        red_points = [[pts[0], pts[1]], [pts[2], pts[3]]]

                if green_points:
                    experts_data[f"expert{i}_green"] = green_points
                if red_points:
                    experts_data[f"expert{i}_red"] = red_points

            for i in range(1, 4):
                if f"expert{i}_green" in experts_data:
                    gt_len_pa = euclidean_distance(*experts_data[f"expert{i}_green"])
                    results[f"meas2expert{i}_length_pulmonary_artery"] = abs(diameter_pa - gt_len_pa)
                    if pa_model_pts[0] and pa_model_pts[1]:
                        pt_err_pa = pointwise_distance_error(experts_data[f"expert{i}_green"], pa_model_pts)
                        results[f"meas2expert{i}_point_pulmonary_artery"] = pt_err_pa

                if f"expert{i}_red" in experts_data:
                    gt_len_ao = euclidean_distance(*experts_data[f"expert{i}_red"])
                    results[f"meas2expert{i}_length_aorta"] = abs(diameter_ao - gt_len_ao)
                    if ao_model_pts[0] and ao_model_pts[1]:
                        pt_err_ao = pointwise_distance_error(experts_data[f"expert{i}_red"], ao_model_pts)
                        results[f"meas2expert{i}_point_aorta"] = pt_err_ao

            results.update(calculate_expert_errors(experts_data))
            all_errors[image_name] = results

        except Exception as e:
            print(f"[{model_name}] Error processing {image_name}: {e}")

    save_path = os.path.join(output_dir, f"deviation_3VV_from_csv_{model_name}.json")
    save_json(all_errors, save_path)
    print(f"[{model_name}] results saved in {save_path}")

def main():
    groups = {
        "group1": load_json(os.path.join(GROUPS_PATH, "group1.json")),
        "group2": load_json(os.path.join(GROUPS_PATH, "group2.json")),
        "group3": load_json(os.path.join(GROUPS_PATH, "group3.json")),
    }
    for model_name, meas_path in MODEL_FILES.items():
        process_one_model(meas_path, model_name, groups, OUTPUT_DIR)

if __name__ == "__main__":
    main()
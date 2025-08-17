import os
import cv2
import numpy as np
import matplotlib.pyplot as plt
from skimage.morphology import skeletonize
from scipy.spatial.distance import cdist
import csv
import json
import yaml

with open("config.yaml", "r") as f:
    cfg = yaml.safe_load(f)

WORK_DIR = cfg["work_dir"]
INPUT_FOLDER = cfg["input_folder"]
OUTPUT_CSV = os.path.join(WORK_DIR, cfg["output_csv"])
OUTPUT_JSON = os.path.join(WORK_DIR, cfg["output_json"])
VISUALIZE = cfg["visualize"]
DIAM_LEN = cfg["diameter_search_length"]

def get_mask_from_rgb(img_rgb, color):
    return np.all(img_rgb == color, axis=-1)

def get_centerline(mask):
    skeleton = skeletonize(mask > 0)
    return np.column_stack(np.nonzero(skeleton))

def closest_point(centerline, ref_point):
    dists = cdist(centerline, ref_point[None])
    idx = np.argmin(dists)
    return centerline[idx], idx

def compute_normal(centerline, idx):
    if len(centerline) < 2:
        return np.array([1, 0])
    if idx == 0:
        p1, p2 = centerline[idx], centerline[idx + 1]
    elif idx == len(centerline) - 1:
        p1, p2 = centerline[idx - 1], centerline[idx]
    else:
        p1, p2 = centerline[idx - 1], centerline[idx + 1]
    tangent = p2 - p1
    normal = np.array([-tangent[1], tangent[0]])
    norm = np.linalg.norm(normal)
    return normal / norm if norm != 0 else np.array([1, 0])

def measure_diameter(mask, point, normal_dir, length=DIAM_LEN):
    y0, x0 = point.astype(int)
    coords = []
    for d in range(-length, length):
        x = int(x0 + d * normal_dir[1])
        y = int(y0 + d * normal_dir[0])
        if 0 <= y < mask.shape[0] and 0 <= x < mask.shape[1]:
            if mask[y, x]:
                coords.append((x, y))
    if len(coords) >= 2:
        p1, p2 = coords[0], coords[-1]
        return np.linalg.norm(np.array(p1) - np.array(p2)), p1, p2
    return 0, None, None

def process_image(path, visualize=False):
    img = cv2.imread(path)
    if img is None:
        print(f"Reading Files Error: {path}")
        return None, None, None, None, None, None
    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    mask_ao = get_mask_from_rgb(img_rgb, [255, 0, 0])
    mask_pa = get_mask_from_rgb(img_rgb, [0, 255, 0])
    mask_tra = get_mask_from_rgb(img_rgb, [0, 0, 255])
    pts_ao = get_centerline(mask_ao)
    pts_pa = get_centerline(mask_pa)
    pts_tra = np.column_stack(np.nonzero(mask_tra))
    if pts_ao.size == 0 or pts_pa.size == 0 or pts_tra.size == 0:
        return None, None, None, None, None, None
    center_tra = np.mean(pts_tra, axis=0)
    dists = cdist(pts_ao, center_tra[None])
    min_idx = np.argmin(dists)
    P_a = pts_ao[min_idx]
    normal_ao = compute_normal(pts_ao, min_idx)
    diam_ao, p1_ao, p2_ao = measure_diameter(mask_ao, P_a, normal_ao)
    dists_pa = cdist(pts_pa, P_a[None])
    min_idx_pa = np.argmin(dists_pa)
    P_p = pts_pa[min_idx_pa]
    normal_pa = compute_normal(pts_pa, min_idx_pa)
    diam_pa, p1_pa, p2_pa = measure_diameter(mask_pa, P_p, normal_pa)
    if visualize:
        plt.imshow(img_rgb)
        plt.scatter(center_tra[1], center_tra[0], c='blue', marker='x', label='TRA center')
        if p1_ao and p2_ao:
            plt.plot([p1_ao[0], p2_ao[0]], [p1_ao[1], p2_ao[1]], 'r-', label='AO diameter')
        if p1_pa and p2_pa:
            plt.plot([p1_pa[0], p2_pa[0]], [p1_pa[1], p2_pa[1]], 'g-', label='PA diameter')
        plt.title(os.path.basename(path))
        plt.legend()
        plt.savefig(os.path.join(os.path.dirname(path), os.path.basename(path).split('.')[0] + '_result.png'))
    return diam_ao, diam_pa, p1_ao, p2_ao, p1_pa, p2_pa

def process_folder(folder_path, visualize=False, output_csv=OUTPUT_CSV, output_json=OUTPUT_JSON):
    print("Folder:", folder_path)
    results = []
    for filename in os.listdir(folder_path):
        if filename.lower().endswith(('.png', '.jpg', '.jpeg')):
            file_path = os.path.join(folder_path, filename)
            try:
                diam_ao, diam_pa, p1_ao, p2_ao, p1_pa, p2_pa = process_image(file_path, visualize)
                result = {
                    'filename': filename,
                    'diameter_AO': float(f"{diam_ao:.2f}"),
                    'AO_point1_x': p1_ao[0] if p1_ao else '',
                    'AO_point1_y': p1_ao[1] if p1_ao else '',
                    'AO_point2_x': p2_ao[0] if p2_ao else '',
                    'AO_point2_y': p2_ao[1] if p2_ao else '',
                    'diameter_PA': float(f"{diam_pa:.2f}"),
                    'PA_point1_x': p1_pa[0] if p1_pa else '',
                    'PA_point1_y': p1_pa[1] if p1_pa else '',
                    'PA_point2_x': p2_pa[0] if p2_pa else '',
                    'PA_point2_y': p2_pa[1] if p2_pa else '',
                }
                results.append(result)
                print(f"{filename} --> AO diameter: {diam_ao:.2f}, PA diameter: {diam_pa:.2f}")
            except Exception as e:
                print(f"Processing {filename} failed: {e}")
    if results:
        with open(output_csv, 'w', newline='') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=results[0].keys())
            writer.writeheader()
            writer.writerows(results)
        print(f"Saving CSVs to {output_csv}")
    with open(output_json, 'w') as jsonfile:
        json.dump(results, jsonfile, indent=4)
    print(f"Saving JSON to {output_json}")

def main():
    os.chdir(WORK_DIR)
    process_folder(INPUT_FOLDER, visualize=VISUALIZE)

if __name__ == "__main__":
    main()
# medical_agent_project/plugin/utils/measurement.py

import cv2
import numpy as np
from skimage.morphology import skeletonize
from scipy.spatial.distance import cdist
from PIL import Image

# --- 您提供的所有辅助函数 ---
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
    if len(centerline) < 2: return np.array([1, 0])
    if idx == 0: p1, p2 = centerline[idx], centerline[idx + 1]
    elif idx == len(centerline) - 1: p1, p2 = centerline[idx - 1], centerline[idx]
    else: p1, p2 = centerline[idx - 1], centerline[idx + 1]
    tangent = p2 - p1
    normal = np.array([-tangent[1], tangent[0]])
    norm = np.linalg.norm(normal)
    return normal / norm if norm != 0 else np.array([1, 0])

def measure_diameter(mask, point, normal_dir, length=100): # Increased length for safety
    y0, x0 = point.astype(int)
    coords = []
    for d in range(-length, length):
        x = int(x0 + d * normal_dir[1])
        y = int(y0 + d * normal_dir[0])
        if 0 <= y < mask.shape[0] and 0 <= x < mask.shape[1] and mask[y, x]:
            coords.append((x, y))
    if len(coords) >= 2:
        p1, p2 = coords[0], coords[-1]
        return np.linalg.norm(np.array(p1) - np.array(p2)), p1, p2
    return 0, None, None

# --- 主入口函数 ---
def measure_from_color_mask(color_mask_pil: Image.Image):
    """
    接收一张彩色的PIL Image掩码，执行测量并返回结果。
    """
    img_rgb = np.array(color_mask_pil.convert("RGB"))

    mask_ao = get_mask_from_rgb(img_rgb, [255, 0, 0])
    mask_da = get_mask_from_rgb(img_rgb, [0, 255, 0])
    mask_tra = get_mask_from_rgb(img_rgb, [0, 0, 255])

    pts_ao = get_centerline(mask_ao)
    pts_da = get_centerline(mask_da)
    pts_tra = np.column_stack(np.nonzero(mask_tra))
    
    if pts_ao.size == 0 or pts_da.size == 0 or pts_tra.size == 0:
        print("警告: 测量失败，掩码中缺少必要的结构。")
        return None

    center_tra = np.mean(pts_tra, axis=0)
    dists = cdist(pts_ao, center_tra[None])
    min_idx = np.argmin(dists)
    P_a = pts_ao[min_idx]

    normal_ao = compute_normal(pts_ao, min_idx)
    diam_ao, _, _ = measure_diameter(mask_ao, P_a, normal_ao)

    dists_da = cdist(pts_da, P_a[None])
    min_idx_da = np.argmin(dists_da)
    P_d = pts_da[min_idx_da]

    normal_da = compute_normal(pts_da, min_idx_da)
    diam_da, _, _ = measure_diameter(mask_da, P_d, normal_da)

    return {
        'diameter_AO': float(f"{diam_ao:.2f}"),
        'diameter_DA': float(f"{diam_da:.2f}")
    }
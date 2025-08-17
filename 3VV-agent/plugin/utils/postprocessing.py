# medical_agent_project/plugin/utils/postprocessing.py

import numpy as np
from PIL import Image

# 定义类别ID到RGB颜色的映射
# 假设: 1=AO (红色), 2=DA (绿色), 3=TRA (蓝色)
CLASS_TO_COLOR = {
    1: [255, 0, 0],
    2: [0, 255, 0],
    3: [0, 0, 255]
}

def convert_label_to_color_mask(label_mask: np.ndarray) -> Image.Image:
    """
    将单通道的数字标签掩码转换为测量代码所需的RGB彩色掩码。
    """
    h, w = label_mask.shape
    color_mask_np = np.zeros((h, w, 3), dtype=np.uint8)

    for class_id, color in CLASS_TO_COLOR.items():
        color_mask_np[label_mask == class_id] = color
    
    return Image.fromarray(color_mask_np)
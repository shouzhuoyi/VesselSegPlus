# D:/Projects/3VV-agent/test_code/test_segmentation.py

import numpy as np
from PIL import Image
import os
import sys

sys.path.append('..') 
from plugin.utils.segmentation import SegmentationModel

MODEL_FOLDER_PATH = "../checkpoints/Dataset006_3VV_New/nnUNetTrainer__nnUNetPlans__2d"
TEST_IMAGE_PATH = "../test_images/946_0000.png" 
OUTPUT_VISUAL_PATH = "../segmentation_output.png"
OUTPUT_NUMPY_PATH = "../label_mask.npy"

def run_segmentation_test():
    print("="*50)
    print("【测试第一步】: 开始测试分割模块...")
    if not os.path.exists(TEST_IMAGE_PATH):
        print(f"错误：测试图片未找到...")
        return
    seg_model = SegmentationModel() 
    print(f"正在加载测试图片: {TEST_IMAGE_PATH}")
    image_pil = Image.open(TEST_IMAGE_PATH)
    try:
        label_mask_np = seg_model.predict(image_pil)
        if label_mask_np is not None and isinstance(label_mask_np, np.ndarray):
            print(f"分割成功！输出数字标签掩码的形状: {label_mask_np.shape}, 数据类型: {label_mask_np.dtype}")
            np.save(OUTPUT_NUMPY_PATH, label_mask_np)
            print(f"原始数字标签已保存到: {os.path.abspath(OUTPUT_NUMPY_PATH)}")
            visible_mask = (label_mask_np * 85).astype(np.uint8)
            output_image = Image.fromarray(visible_mask)
            output_image.save(OUTPUT_VISUAL_PATH)
            print(f"可视化预览图已保存到: {os.path.abspath(OUTPUT_VISUAL_PATH)}")
            print("\n【测试第一步】成功！")
        else:
            print("\n【测试第一步】失败：predict函数没有返回预期的Numpy数组。")
    except Exception as e:
        print(f"\n【测试第一步】失败：预测过程中出现问题。错误信息: {e}")
    print("="*50)

if __name__ == "__main__":
    run_segmentation_test()
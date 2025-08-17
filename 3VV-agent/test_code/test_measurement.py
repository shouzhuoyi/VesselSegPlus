# D:/Projects/3VV-agent/test_code/test_measurement.py

import numpy as np
from PIL import Image
import os
import sys

sys.path.append('..')
from plugin.utils.postprocessing import convert_label_to_color_mask
from plugin.utils.measurement import measure_from_color_mask

INPUT_NUMPY_PATH = "../label_mask.npy"
OUTPUT_COLOR_MASK_PATH = "../color_mask_visualization.png"

def run_measurement_test():
    print("="*50)
    print("【测试第二步】: 开始测试转换和测量模块...")
    if not os.path.exists(INPUT_NUMPY_PATH):
        print(f"错误：找不到输入文件 {INPUT_NUMPY_PATH}。请先成功运行第一步测试。")
        return
    try:
        print(f"正在加载数字标签文件: {INPUT_NUMPY_PATH}")
        label_mask_np = np.load(INPUT_NUMPY_PATH)
        print("正在将数字标签图转换为彩色图...")
        color_mask_pil = convert_label_to_color_mask(label_mask_np)
        color_mask_pil.save(OUTPUT_COLOR_MASK_PATH)
        print(f"转换后的彩色图已保存到: {os.path.abspath(OUTPUT_COLOR_MASK_PATH)}")
        print("正在对彩色图进行测量...")
        diameters = measure_from_color_mask(color_mask_pil)
        if diameters is not None:
            print("\n测量成功！结果如下:")
            print(diameters)
            print("\n【测试第二步】成功！")
        else:
            print("\n【测试第二步】失败：测量函数未能返回结果。")
    except Exception as e:
        print(f"\n【测试第二步】失败：处理过程中出现问题。错误信息: {e}")
    print("="*50)

if __name__ == "__main__":
    run_measurement_test()
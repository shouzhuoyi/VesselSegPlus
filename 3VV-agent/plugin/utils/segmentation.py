# medical_agent_project/plugin/utils/segmentation.py

from PIL import Image
import subprocess
import os
import shutil
import uuid
import numpy as np

# --- 配置部分 ---
DATASET_ID = 6
CONFIGURATION = "2d"
FOLD = 0
TEMP_FOLDER = os.path.abspath("./temp_io")
# --- 配置结束 ---

def segment_with_command_line(image_pil: Image.Image) -> np.ndarray:
    task_id = str(uuid.uuid4())
    input_dir = os.path.join(TEMP_FOLDER, f"input_{task_id}")
    output_dir = os.path.join(TEMP_FOLDER, f"output_{task_id}")

    os.makedirs(input_dir, exist_ok=True)
    os.makedirs(output_dir, exist_ok=True)

    try:
        image_pil_rgb = image_pil.convert("RGB")
        temp_input_filename = os.path.join(input_dir, "image_0000.png")
        image_pil_rgb.save(temp_input_filename)
        
        command = [
            "nnUNetv2_predict", "-i", input_dir, "-o", output_dir, "-d", str(DATASET_ID),
            "-c", CONFIGURATION, "-f", str(FOLD), "-chk", "checkpoint_best.pth",
            "-nps", "1", "--disable_tta"
        ]
        
        my_env = os.environ.copy()
        my_env["nnUNet_results"] = os.path.abspath('./checkpoints')
        
        print(f"正在执行命令: {' '.join(command)}")
        # 在Windows上使用 shell=True 来确保命令能被正确找到
        subprocess.run(command, check=True, env=my_env, shell=True)
        print("nnUNetv2_predict 命令已执行。")

        output_image_path = os.path.join(output_dir, "image.png")
        if not os.path.exists(output_image_path):
            print(f"错误：输出文件夹内容为: {os.listdir(output_dir)}")
            raise FileNotFoundError(f"在输出文件夹中未找到期望的 image.png 文件")
        
        print(f"已找到输出文件: {output_image_path}")
        # 加载这张PNG，并将其作为单通道的Numpy数组返回
        result_label_mask_pil = Image.open(output_image_path)
        result_label_mask_np = np.array(result_label_mask_pil)
        return result_label_mask_np
    finally:
        print("正在清理临时文件...")
        if os.path.exists(input_dir):
            shutil.rmtree(input_dir)
        if os.path.exists(output_dir):
            shutil.rmtree(output_dir)
        print("清理完毕。")


class SegmentationModel:
    def predict(self, image_pil: Image.Image) -> np.ndarray:
        return segment_with_command_line(image_pil)
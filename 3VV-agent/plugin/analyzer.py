# medical_agent_project/plugin/analyzer.py

import base64
from PIL import Image
from io import BytesIO
import traceback
from .utils.segmentation import SegmentationModel
from .utils.postprocessing import convert_label_to_color_mask
from .utils.measurement import measure_from_color_mask

seg_model = SegmentationModel()

def analyze_3vv_image(image_base64_string: str) -> dict:
    try:
        # 1. 解码原始图像
        image_data = base64.b64decode(image_base64_string)
        image_pil = Image.open(BytesIO(image_data)).convert('RGB')

        # 2. 调用分割模块，得到【数字标签掩码】
        label_mask_np = seg_model.predict(image_pil)

        # 3. 调用后处理模块，将数字标签掩码转换为【彩色掩码】
        color_mask_pil = convert_label_to_color_mask(label_mask_np)

        # 4. 调用测量模块，传入【彩色掩码】并得到最终结果
        diameters = measure_from_color_mask(color_mask_pil)
        
        if diameters is None:
             return {"status": "error", "message": "Measurement failed."}

        return {"status": "success", "data": diameters}

    except Exception as e:
        print(f"在analyzer.py中处理图像时出错: {e}")
        return {"status": "error", "message": str(e), "details": traceback.format_exc()}
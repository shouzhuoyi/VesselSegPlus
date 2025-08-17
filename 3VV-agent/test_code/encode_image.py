# encode_image.py
import base64
import sys

# 将使用第一个命令行参数作为图片路径，如果没有提供，则使用默认路径
DEFAULT_IMAGE = '../test_images/946_0000.png'
image_path = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_IMAGE

try:
    with open(image_path, "rb") as image_file:
        b64_string = base64.b64encode(image_file.read()).decode("utf-8")
    
    print("\n--- 请复制以下整段Base64字符串 ---")
    print(b64_string)
    print("--- 复制结束 ---\n")

except FileNotFoundError:
    print(f"\n错误：找不到文件 '{image_path}'。请检查路径是否正确。\n")
except Exception as e:
    print(f"\n发生错误: {e}\n")
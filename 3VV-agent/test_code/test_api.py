# test_api.py

import requests
import base64
import sys
import json

# --- 配置部分 ---
# 您的API服务地址
API_URL = "http://127.0.0.1:5000/analyze_3vv"

# 您要用于测试的图片路径
# 脚本会优先使用命令行传入的第一个参数作为路径，否则使用默认值
DEFAULT_IMAGE_PATH = '../test_images/946_0000.png'
# --- 配置结束 ---

def run_api_test():
    """
    执行对本地API服务的完整测试。
    """
    print("="*50)
    print("【API测试】: 开始测试Flask API服务...")
    
    image_path = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_IMAGE_PATH

    # 1. 检查并读取图片文件
    try:
        print(f"正在读取并编码图片: {image_path}")
        with open(image_path, "rb") as image_file:
            b64_string = base64.b64encode(image_file.read()).decode("utf-8")
    except FileNotFoundError:
        print(f"错误：找不到测试图片 '{image_path}'。请检查路径。")
        return
    except Exception as e:
        print(f"读取或编码图片时出错: {e}")
        return

    # 2. 准备要发送的JSON数据
    payload = {"image": b64_string}

    # 3. 发送POST请求到API服务器
    try:
        print(f"正在向 {API_URL} 发送请求...")
        # 设置一个较长的超时时间（例如5分钟），因为模型推理可能较慢
        response = requests.post(API_URL, json=payload, timeout=300)

        # 检查服务器是否返回了成功状态码 (例如 200 OK)
        response.raise_for_status()

        # 4. 打印成功的结果
        print("\n【API测试】成功！服务器返回结果如下:")
        # 使用json库美化打印输出
        result_json = response.json()
        print(json.dumps(result_json, indent=4, ensure_ascii=False))

    except requests.exceptions.ConnectionError:
        print("\n错误：无法连接到API服务器。")
        print("请确认您的 `python -m plugin.app` 服务是否正在另一个终端窗口中正常运行。")
    except requests.exceptions.RequestException as e:
        print(f"\n错误：请求失败。错误信息: {e}")
        # 如果服务器返回了错误信息，也打印出来
        try:
            print("服务器返回内容:", response.text)
        except NameError:
            pass
    
    print("="*50)


if __name__ == "__main__":
    run_api_test()
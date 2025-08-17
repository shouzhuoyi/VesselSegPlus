# medical_agent_project/plugin/app.py

from flask import Flask, request, jsonify
# --- 主要变化在这里 ---
# 我们在 analyzer 前面加了一个点(.)，表示从当前包导入
from .analyzer import analyze_3vv_image 
# --- 变化结束 ---

# 创建一个Flask应用实例
app = Flask(__name__)

@app.route('/analyze_3vv', methods=['POST'])
def handle_analyze_request():
    """
    定义一个API端点，它只接受POST请求。
    """
    if not request.is_json:
        return jsonify({"status": "error", "message": "请求必须为JSON格式"}), 400

    data = request.get_json()
    
    if 'image' not in data:
        return jsonify({"status": "error", "message": "JSON中缺少'image'字段"}), 400

    image_base64 = data['image']

    # 调用我们的核心分析函数
    result = analyze_3vv_image(image_base64)

    # 将函数的结果作为JSON响应返回
    return jsonify(result)

if __name__ == '__main__':
    # 启动这个Web服务器，监听本地的5000端口
    app.run(host='0.0.0.0', port=5000, debug=True)
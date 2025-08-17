# main_app.py (最终版 - 支持 report <路径>)

import base64
import requests
import json
from langchain_ollama.chat_models import ChatOllama
import os,yaml
with open("config.yaml", "r") as f:
    cfg = yaml.safe_load(f)



PLUGIN_API_URL = cfg["app"]["plugin_api_url"]
REPORT_GENERATION_MODEL = cfg["llm"]["report_generation_model"]
PROMPT_TEMPLATE_FILE = cfg["llm"]["prompt_template_file"]
CACHE_FILE = cfg["app"]["cache_file"]


# --- 缓存管理函数 (保持不变) ---
def load_cache() -> dict:
    if os.path.exists(CACHE_FILE):
        with open(CACHE_FILE, 'r') as f:
            print("(系统：缓存文件已加载)")
            return json.load(f)
    return {}

def save_cache(cache_data: dict):
    with open(CACHE_FILE, 'w') as f:
        json.dump(cache_data, f, indent=4)
    print("(系统：缓存文件已更新)")

# --- 插件调用函数 (保持不变) ---
def call_analysis_plugin(image_path: str) -> dict | None:
    print(f"\n>> 正在调用分析插件，输入: {image_path}")
    try:
        cleaned_path = image_path.strip().strip("'\"")
        with open(cleaned_path, "rb") as image_file:
            b64_string = base64.b64encode(image_file.read()).decode("utf-8")
        payload = {"image": b64_string}
        response = requests.post(PLUGIN_API_URL, json=payload, timeout=300)
        response.raise_for_status()
        result = response.json()
        print(f">> 插件返回成功: {result}")
        return result
    except Exception as e:
        print(f">> 插件调用失败: {e}")
        return None

# --- 新增：重构的数据获取函数 ---
def get_data_for_image(image_path: str, cache: dict) -> dict | None:
    """
    一个核心函数，负责为给定的图片路径获取测量数据。
    它会先检查缓存，如果未命中，则调用API插件。
    """
    if not os.path.exists(image_path):
        print(f"错误：找不到文件 '{image_path}'")
        return None

    image_abs_path = os.path.abspath(image_path)

    if image_abs_path in cache:
        print(f"命中缓存！直接从缓存中读取'{image_path}'的数据。")
        return cache[image_abs_path]
    else:
        print("未命中缓存，开始调用插件进行实时分析...")
        result = call_analysis_plugin(image_path)
        if result and result.get('status') == 'success':
            # 将新结果存入缓存，并保存到文件
            cache[image_abs_path] = result
            save_cache(cache)
            return result
        else:
            print("分析失败，请检查插件服务和错误信息。")
            return None

def main():
    """命令式交互的主执行函数"""
    print("="*50)
    print("智能诊断助手已启动 (最终版)。")
    print("请输入命令:")
    print("  - analyze <图片路径>")
    print("  - report [<图片路径>]")
    print("  - quit")
    print("="*50)

    llm = ChatOllama(model=REPORT_GENERATION_MODEL)
    cache = load_cache()
    last_measurement_data = None

    while True:
        try:
            user_input = input("\n命令 > ")
            parts = user_input.split()
            command = parts[0].lower() if parts else ""

            if command in ["quit", "exit", "退出"]:
                print("感谢使用，再见！")
                break

            elif command == "analyze":
                if len(parts) < 2:
                    print("错误：请提供图片路径。用法: analyze <图片路径>")
                    continue
                
                image_path = " ".join(parts[1:])
                # 调用重构后的数据获取函数
                last_measurement_data = get_data_for_image(image_path, cache)
                if last_measurement_data:
                     print(f"分析成功！数据为: {last_measurement_data.get('data')}")
                     print("现在可以使用 'report' 命令生成报告。")

            elif command == "report":
                data_to_report = None
                if len(parts) > 1:
                    # report <路径> 模式：直接获取指定图片的数据
                    print("检测到“一步到位”报告模式...")
                    image_path = " ".join(parts[1:])
                    data_to_report = get_data_for_image(image_path, cache)
                else:
                    # report 常规模式：使用上一次分析的数据
                    if not last_measurement_data:
                        print("错误：请先使用 'analyze' 命令或使用 'report <路径>' 指定一张图片。")
                        continue
                    data_to_report = last_measurement_data
                
                if not data_to_report:
                    print("无法生成报告，因为未能获取到有效的分析数据。")
                    continue

                print("\n正在根据已分析的数据生成报告...")
                try:
                    with open(PROMPT_TEMPLATE_FILE, 'r', encoding='utf-8') as f:
                        report_template = f.read()
                    
                    diameters = data_to_report.get('data', {})
                    ao_diam = diameters.get('diameter_AO', 'N/A')
                    da_diam = diameters.get('diameter_DA', 'N/A')

                    final_prompt = report_template.format(
                        report_type="3VV", diameter_AO=ao_diam, diameter_DA=da_diam
                    )
                    
                    final_report = llm.invoke(final_prompt)
                    
                    print("="*50)
                    print("\n报告生成完毕：\n")
                    print(final_report.content)
                    print("="*50)
                except Exception as e:
                    print(f"生成报告时出错: {e}")
            
            else:
                print("无效命令。可用命令: analyze, report, quit")

        except KeyboardInterrupt:
            print("\n程序已中断。感谢使用，再见！")
            break
        except Exception as e:
            print(f"\n发生了一个未知错误: {e}")

if __name__ == "__main__":
    main()
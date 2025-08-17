import base64
import requests
import json
import yaml
from langchain_ollama.chat_models import ChatOllama
from langchain.agents import tool, AgentExecutor, create_react_agent
from langchain import hub
from langchain_core.messages import HumanMessage, AIMessage
import os
with open("config.yaml", "r") as f:
    cfg = yaml.safe_load(f)

# --- 配置部分 ---
PLUGIN_API_URL = cfg["app"]["plugin_api_url"]
AGENT_MODEL = cfg["llm"]["agent_model"]
PROMPT_TEMPLATE_FILE = cfg["llm"]["prompt_template_file"]
CACHE_FILE = cfg["app"]["cache_file"]


# --- 缓存管理函数 ---
def load_cache() -> dict:
    if os.path.exists(CACHE_FILE):
        with open(CACHE_FILE, 'r') as f:
            return json.load(f)
    return {}

def save_cache(cache_data: dict):
    with open(CACHE_FILE, 'w') as f:
        json.dump(cache_data, f, indent=4)
# --- 缓存管理函数结束 ---


@tool
def analyze_fetal_heart_image(image_path: str) -> str:
    """
    当需要分析一张胎儿心脏超声图像以获取大血管直径时，请使用此工具。
    输入必须是一个指向本地图像文件的有效路径。
    这个工具会返回一个包含主动脉(AO)和动脉导管(DA)直径的JSON字符串。
    """
    print(f"\n>> 智能体决定调用工具: analyze_fetal_heart_image")
    print(f">> 工具输入: {image_path}")

    # --- 缓存逻辑 ---
    cache = load_cache()
    cleaned_path = image_path.strip().strip("'\"")
    image_abs_path = os.path.abspath(cleaned_path)

    if image_abs_path in cache:
        print(f">> 命中缓存！直接返回已存储的数据。")
        cached_result = cache[image_abs_path]
        return json.dumps(cached_result.get('data', {}))
    # --- 缓存逻辑结束 ---

    print(f">> 未命中缓存，正在调用API插件...")
    try:
        with open(cleaned_path, "rb") as image_file:
            b64_string = base64.b64encode(image_file.read()).decode("utf-8")
        payload = {"image": b64_string}
        response = requests.post(PLUGIN_API_URL, json=payload, timeout=300)
        response.raise_for_status()
        result = response.json()
        
        # 将成功的结果存入缓存
        if result and result.get('status') == 'success':
            cache[image_abs_path] = result
            save_cache(cache)
            print(f">> API调用成功，结果已存入缓存。")
        
        print(f">> 工具返回: {result}")
        return json.dumps(result.get('data', {}))
        
    except Exception as e:
        error_message = f"调用工具时出错: {e}"
        print(f">> 工具出错: {error_message}")
        return error_message

def main():
    """混合模式交互的主执行函数"""
    print("="*50)
    print(f"混合模式智能诊断助手已启动 (模型: {AGENT_MODEL})。")
    print("您可以输入明确命令，或直接与AI对话。")
    print("  - 命令: analyze <图片路径>")
    print("  - 命令: report")
    print("  - 命令: quit")
    print("="*50)

    # 初始化LLM和为“聊天模式”准备的智能体
    llm = ChatOllama(model=AGENT_MODEL)
    tools = [analyze_fetal_heart_image]
    prompt = hub.pull("hwchase17/react-chat")
    agent = create_react_agent(llm, tools, prompt)
    agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True, handle_parsing_errors=True)

    # 初始化“记忆”
    chat_history = []
    last_measurement_data = None

    while True:
        try:
            user_input = input("您 (You): ")
            parts = user_input.split()
            command = parts[0].lower() if parts else ""

            ai_response = ""

            # --- 混合模式的路由逻辑 ---
            if command == "quit":
                ai_response = "感谢使用，再见！"
                print(f"AI: {ai_response}")
                break

            elif command == "analyze":
                # --- 命令模式：精确执行分析 ---
                if len(parts) < 2:
                    ai_response = "错误：请提供图片路径。用法: analyze <图片路径>"
                else:
                    image_path = parts[1]
                    if not os.path.exists(image_path):
                        ai_response = f"错误：找不到文件 '{image_path}'"
                    else:
                        result_str = analyze_fetal_heart_image.invoke(image_path)
                        try:
                            last_measurement_data = json.loads(result_str)
                            ai_response = f"分析成功！获取到数据: {last_measurement_data}。现在可以使用 'report' 命令生成报告。"
                        except json.JSONDecodeError:
                            ai_response = f"分析失败，工具返回了无效的结果: {result_str}"
                print(f"AI: {ai_response}")

            elif command == "report":
                # --- 命令模式：精确执行报告生成 ---
                if not last_measurement_data:
                    ai_response = "错误：请先使用 'analyze' 命令成功分析一张图片。"
                else:
                    print("\nAI: 收到报告生成指令，正在为您准备报告...")
                    try:
                        with open(PROMPT_TEMPLATE_FILE, 'r', encoding='utf-8') as f:
                            report_template = f.read()
                        
                        final_prompt = report_template.format(
                            report_type="3VV", 
                            diameter_AO=last_measurement_data.get('diameter_AO', 'N/A'), 
                            diameter_DA=last_measurement_data.get('diameter_DA', 'N/A')
                        )
                        
                        final_report = llm.invoke(final_prompt)
                        ai_response = f"\n报告生成完毕：\n\n{final_report.content}"
                    except Exception as e:
                        ai_response = f"生成报告时出错: {e}"
                print(f"AI: {ai_response}")

            else:
                # --- 聊天模式：让智能体自由发挥 ---
                print("\nAI: (正在思考...)")
                result = agent_executor.invoke({
                    "input": user_input, "chat_history": chat_history
                })
                ai_response = result['output']
                
                # 同样尝试捕获数据
                try:
                    json_part = ai_response[ai_response.find('{'):ai_response.rfind('}')+1]
                    parsed_json = json.loads(json_part)
                    if isinstance(parsed_json, dict) and 'diameter_AO' in parsed_json:
                        last_measurement_data = parsed_json
                        print(f"(系统提示：已在对话中捕获并存储测量数据: {last_measurement_data})")
                except:
                    pass
                
                print(f"\nAI: {ai_response}\n")

            # 统一更新聊天记录
            chat_history.append(HumanMessage(content=user_input))
            chat_history.append(AIMessage(content=ai_response))

        except KeyboardInterrupt:
            print("\nAI: 对话已中断。感谢使用，再见！")
            break
        except Exception as e:
            print(f"\n发生了一个未知错误: {e}")

if __name__ == "__main__":
    main()
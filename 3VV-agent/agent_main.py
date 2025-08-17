# agent_main.py

import base64
import requests
import json
import yaml
from langchain_ollama.chat_models import ChatOllama
from langchain.agents import tool, AgentExecutor, create_react_agent
from langchain import hub

with open("config.yaml", "r") as f:
    cfg = yaml.safe_load(f)

TEST_IMAGE_PATH = cfg["testing"]["default_image_path"]
PLUGIN_API_URL = cfg["app"]["plugin_api_url"]
REPORT_GENERATION_MODEL = cfg["llm"]["agent_model"]
PROMPT_TEMPLATE_FILE = cfg["llm"]["prompt_template_file"]



@tool
def analyze_fetal_heart_image(image_path: str) -> str:
    """
    当需要分析一张胎儿心脏超声图像以获取大血管直径时，请使用此工具。
    输入必须是一个指向本地图像文件的有效路径。
    这个工具会返回一个包含主动脉(AO)和动脉导管(DA)直径的JSON字符串。
    """
    print(f"\n>> 智能体决定调用工具: analyze_fetal_heart_image")
    print(f">> 智能体提供的原始输入: '{image_path}'") # 打印原始输入以供调试

    # --- 主要变化在这里 ---
    # 清理输入路径，移除LLM可能添加的多余的空格和引号
    cleaned_path = image_path.strip().strip("'\"")
    print(f">> 清理后的工具输入: '{cleaned_path}'")
    # --- 变化结束 ---
    
    try:
        # 使用清理过的路径
        with open(cleaned_path, "rb") as image_file:
            b64_string = base64.b64encode(image_file.read()).decode("utf-8")
        
        payload = {"image": b64_string}
        response = requests.post(PLUGIN_API_URL, json=payload, timeout=300)
        response.raise_for_status()
        result = response.json()
        print(f">> 工具返回: {result}")
        return json.dumps(result)
        
    except Exception as e:
        error_message = f"调用工具时出错: {e}"
        print(f">> 工具出错: {error_message}")
        return error_message


def main():
    """主执行函数"""
    print("="*50)
    print("智能体主程序已启动...")

    llm = ChatOllama(model=REPORT_GENERATION_MODEL)
    tools = [analyze_fetal_heart_image]
    prompt_agent = hub.pull("hwchase17/react-chat")
    agent = create_react_agent(llm, tools, prompt_agent)
    agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True, handle_parsing_errors=True)

    # == 第一步：让智能体只负责调用工具获取数据 ==
    print("\n【第一步】: 指令智能体调用工具获取测量数据...")
    
    # --- 主要变化在这里 ---
    # 我们给出了更严格的指令，强制它只返回JSON
    agent_input = f"""
    请使用你的工具分析这张位于 '{TEST_IMAGE_PATH}' 的图像。
    分析完成后，你的最终答案**必须且只能**是工具返回的那个完整的、未经修改的JSON字符串。
    不要添加任何解释、总结或其他文字。
    """
    # --- 变化结束 ---
    
    agent_result = agent_executor.invoke({
        "input": agent_input,
        "chat_history": []
    })

    try:
        measurement_data = json.loads(agent_result['output'])
        print(f"\n【第一步】成功！获取到测量数据: {measurement_data}")
    except (json.JSONDecodeError, KeyError) as e:
        print(f"\n【第一步】失败！无法从智能体输出中解析JSON数据。输出为: {agent_result.get('output', 'N/A')}")
        return

    # == 第二步：使用获取到的数据，进行一次普通的LLM调用来生成报告 ==
    print("\n【第二步】: 填充模板并请求LLM生成最终报告...")
    try:
        with open(PROMPT_TEMPLATE_FILE, 'r', encoding='utf-8') as f:
            report_template = f.read()
    except FileNotFoundError:
        print(f"错误：找不到报告模板文件 {PROMPT_TEMPLATE_FILE}。")
        return

    diameters = measurement_data.get('data', {})
    ao_diam = diameters.get('diameter_AO', 'N/A')
    da_diam = diameters.get('diameter_DA', 'N/A')

    final_prompt_for_report = report_template.format(
        report_type="3VV",
        diameter_AO=ao_diam,
        diameter_DA=da_diam
    )
    
    final_report = llm.invoke(final_prompt_for_report)

    print("="*50)
    print("\n【第二步】成功！智能体执行完成！最终报告如下：\n")
    print(final_report.content)
    print("="*50)


if __name__ == "__main__":
    main()
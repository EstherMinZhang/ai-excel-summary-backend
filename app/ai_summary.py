import os  # 引入 os 模块，用于读取环境变量
import json  # 引入 json 模块，用于把 Python 对象转为 JSON 文本
from dotenv import load_dotenv  # 引入 load_dotenv，用于加载 .env 文件中的配置
from google import genai  # 引入 Google Gemini AI 客户端库

load_dotenv()  # 加载根目录下的 .env 文件，使环境变量可以通过 os.getenv 读取


def generate_ai_summary(structured_summary: dict) -> dict:
    # 从环境变量中读取 GEMINI_API_KEY，并创建 Gemini 客户端
    client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

    # 组织要发送给 Gemini 的提示语
    prompt = f"""
You are a data analyst. Please review this structured dataset summary and return:
1. A plain English summary of the dataset.
2. Any data quality issues.
3. Suggested next analysis steps.

Dataset summary:
{json.dumps(structured_summary, indent=2)}
"""

    # 调用 Gemini 模型生成文本结果
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt
    )

    # 返回一个字典，包含 AI 生成的自然语言摘要
    return {
        "plain_english_summary": response.text
    }

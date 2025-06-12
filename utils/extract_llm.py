import sys
import locale

# 强制设置默认编码为 UTF-8（仅对 Windows 上的 Python 3.6-3.10 有效）
sys.getdefaultencoding = lambda: "utf-8"
locale.getpreferredencoding = lambda: "utf-8"
import os
import json
from openai import OpenAI  # ✅ 新版用法：直接 import OpenAI 类
from dotenv import load_dotenv


load_dotenv()  # ✅ 加载 .env 文件中的变量
client = OpenAI(
    api_key=os.getenv("OPENROUTER_API_KEY"),
    base_url="https://openrouter.ai/api/v1"
)

def extract_fields(text):
    prompt = f"""
你是一名专业的临床研究助理。请从以下文本中提取如下字段（如果没有就填 null）：
- drug_name
- sponsor
- trial_sites（数字）
- enrollment（数字）
- start_date（格式：YYYY-MM-DD）
- completion_date（格式：YYYY-MM-DD）

请以 JSON 格式返回结果，不要包含解释、注释或换行。
内容如下：
{text[:2000]}
"""

    response = client.chat.completions.create(
        model="meta-llama/llama-3-8b-instruct",
        messages=[
            {"role": "user", "content": prompt}
        ],
        temperature=0.2
    )

    answer = response.choices[0].message.content
    try:
        return json.loads(answer)
    except Exception as e:
        print("解析失败，原始内容如下：\n", answer)
        return {
            "drug_name": "error",
            "sponsor": None,
            "trial_sites": None,
            "enrollment": None,
            "start_date": None,
            "completion_date": None
        }

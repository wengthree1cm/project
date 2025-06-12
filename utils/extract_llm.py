import os
import openai
import json




def extract_fields(text):
    prompt = f"""
你是一名专业的临床研究助理。请从以下文章中提取如下字段（如果没有就填 null）：
- drug_name
- sponsor
- trial_sites（数字）
- enrollment（数字）
- start_date（格式：YYYY-MM-DD）
- completion_date（格式：YYYY-MM-DD）

请以 JSON 格式返回结果，不要包含解释。
内容如下：
{text[:4000]}
"""

    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "你是一个临床试验信息提取助手"},
            {"role": "user", "content": prompt}
        ],
        temperature=0
    )

    answer = response.choices[0].message.content
    try:
        return json.loads(answer)
    except:
        return {
            "drug_name": None,
            "sponsor": None,
            "trial_sites": None,
            "enrollment": None,
            "start_date": None,
            "completion_date": None
        }

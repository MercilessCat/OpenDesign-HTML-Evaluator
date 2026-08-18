"""
Functional Judge

负责评价 HTML 页面功能是否满足需求

输入:
    html
    requirement

输出:
    score + reason
"""


from openai import OpenAI
import json

from config import API_KEY, BASE_URL, MODEL



client = OpenAI(
    api_key=API_KEY,
    base_url=BASE_URL
)



def evaluate_functionality(html, requirement):

    prompt = f"""
你是一个HTML质量评估专家。

请评价下面HTML页面的功能完成程度。

评价标准：

1. 页面是否能够正常运行
2. HTML结构是否完整
3. 是否实现用户需求
4. 是否存在明显功能缺陷


用户需求：

{requirement}


HTML代码：

{html}


请输出JSON格式：

{{
    "score": 0-10,
    "reason": "评价原因"
}}

不要输出其他内容。
"""


    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {
                "role":"system",
                "content":"你是专业HTML质量评估模型"
            },
            {
                "role":"user",
                "content":prompt
            }
        ],
        temperature=0.2
    )


    result = response.choices[0].message.content


    try:
        return json.loads(result)

    except:

        return {
            "score":0,
            "reason":result
        }
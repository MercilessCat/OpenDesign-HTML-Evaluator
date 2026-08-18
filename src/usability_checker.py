"""
Usability Checker

评价 HTML 页面用户体验

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



def evaluate_usability(html, requirement):


    prompt = f"""

你是一名专业的网页用户体验专家。

请评价下面HTML页面的可用性。


评价维度：

1. 用户是否容易理解页面目的

2. 页面信息结构是否清晰

3. 操作流程是否自然

4. 交互设计是否符合用户习惯

5. 是否方便完成目标任务


用户需求：

{requirement}


HTML代码：

{html}


请输出JSON：

{{
    "score": 0-10,
    "reason": "详细评价"
}}


不要输出其他内容。


"""


    response = client.chat.completions.create(

        model=MODEL,

        messages=[

            {
                "role":"system",
                "content":"你是专业UX设计评估专家"
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
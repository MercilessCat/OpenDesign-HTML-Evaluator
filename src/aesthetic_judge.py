"""
Aesthetic Judge

评价 HTML 页面视觉设计质量
加入截图视觉信息
"""


from openai import OpenAI
import json


from config import API_KEY, BASE_URL, MODEL

from image_analyzer import analyze_image



client = OpenAI(
    api_key=API_KEY,
    base_url=BASE_URL
)




def evaluate_aesthetic(
        html,
        requirement,
        screenshot=None
):


    # =========================
    # 分析截图
    # =========================


    if screenshot:


        visual_info = analyze_image(
            screenshot
        )


    else:


        visual_info = "没有截图信息"



    # =========================
    # Prompt
    # =========================


    prompt=f"""

你是一名专业网页视觉设计专家。

请评价下面HTML页面的视觉美学质量。



评价标准：

1. 页面整体视觉吸引力

2. 色彩搭配是否合理

3. 页面布局是否协调

4. 字体、间距、组件设计质量

5. CSS设计是否专业

6. 是否符合现代网页设计规范



用户需求：

{requirement}



HTML代码：

{html}



浏览器截图分析信息：

{visual_info}



请输出JSON格式：

{{
    "score":0-10,
    "reason":"详细视觉评价"
}}


不要输出其他内容。

"""



    response = client.chat.completions.create(


        model=MODEL,


        messages=[

            {
                "role":"system",
                "content":
                "你是专业UI视觉设计评价专家"
            },


            {
                "role":"user",
                "content":prompt
            }

        ],


        temperature=0.2

    )



    result=response.choices[0].message.content



    try:


        return json.loads(result)



    except:


        return {

            "score":0,

            "reason":result

        }
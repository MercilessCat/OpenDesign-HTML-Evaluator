"""
OpenDesign HTML Verifier

输入:
    HTML
    用户需求

输出:
    三维评分结果
"""


from functional_judge import evaluate_functionality
from usability_checker import evaluate_usability
from aesthetic_judge import evaluate_aesthetic


from html_renderer import render_html



import os



def verify_html(html, requirement):


    # ======================
    # 生成临时HTML
    # ======================


    temp_html="../temp.html"


    with open(
        temp_html,
        "w",
        encoding="utf-8"
    ) as f:

        f.write(html)



    # ======================
    # 浏览器截图
    # ======================


    screenshot=render_html(

        temp_html,

        "temp.png"

    )



    # ======================
    # 功能评分
    # ======================


    functional_result = evaluate_functionality(

        html,

        requirement

    )



    # ======================
    # 易用评分
    # ======================


    usability_result = evaluate_usability(

        html,

        requirement

    )



    # ======================
    # 美学评分（加入截图）
    # ======================


    aesthetic_result = evaluate_aesthetic(

        html,

        requirement,

        screenshot

    )



    # ======================
    # 综合评分
    # ======================


    overall_score=(

        functional_result["score"]

        +

        usability_result["score"]

        +

        aesthetic_result["score"]

    ) / 3



    return {


        "functional":
            functional_result,


        "usability":
            usability_result,


        "aesthetic":
            aesthetic_result,


        "overall_score":
            round(
                overall_score,
                2
            ),


        "screenshot":
            screenshot

    }
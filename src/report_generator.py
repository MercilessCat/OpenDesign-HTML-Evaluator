"""
HTML Verifier Report Generator

生成实验总结报告

输入:
    results/*.json
    agreement_report.json

输出:
    report/
"""


import os
import json
from datetime import datetime



RESULT_DIR="../results"

AGREEMENT_FILE="../agreement_report.json"

OUTPUT_DIR="../report"





def load_json(path):

    with open(
        path,
        "r",
        encoding="utf-8"
    ) as f:

        return json.load(f)





def generate_score_summary():



    files=os.listdir(
        RESULT_DIR
    )


    scores=[]



    for file in files:


        if not file.endswith(".json"):

            continue



        data=load_json(

            os.path.join(
                RESULT_DIR,
                file
            )

        )



        scores.append(

            {

            "html":data.get(
                "html",
                file
            ),


            "functional":
                data["functional"]["score"],


            "usability":
                data["usability"]["score"],


            "aesthetic":
                data["aesthetic"]["score"],


            "overall":
                data["overall_score"]

            }

        )



    return scores





def generate_markdown(
        scores,
        agreement
):



    text=""


    text+="# HTML Verifier 实验报告\n\n"


    text+=f"生成时间: {datetime.now()}\n\n"



    text+="## 1. 测试规模\n\n"

    text+=f"测试 HTML 数量: {len(scores)} 个\n\n"



    text+="## 2. Verifier 平均评分\n\n"



    avg_functional=sum(

        x["functional"]

        for x in scores

    )/len(scores)



    avg_usability=sum(

        x["usability"]

        for x in scores

    )/len(scores)



    avg_aesthetic=sum(

        x["aesthetic"]

        for x in scores

    )/len(scores)



    avg_overall=sum(

        x["overall"]

        for x in scores

    )/len(scores)



    text+=f"""

|指标|平均分|
|-|-|
|Functional|{avg_functional:.2f}|
|Usability|{avg_usability:.2f}|
|Aesthetic|{avg_aesthetic:.2f}|
|Overall|{avg_overall:.2f}|

"""



    text+="## 3. 人机一致率\n\n"



    for k,v in agreement.items():

        text+=f"""

### {k}

- MAE: {v["MAE"]}
- Accuracy: {v["Accuracy"]}
- Pearson: {v["Pearson"]}
- Spearman: {v["Spearman"]}

"""



    text+="## 4. 总结\n\n"

    text+="""

当前 HTML Verifier 已完成：

- HTML 自动解析
- 三维质量评价
- 批量评测
- 人机一致性分析


后续可继续扩大测试集，
优化评分模型。

"""



    return text





def main():



    if not os.path.exists(
        OUTPUT_DIR
    ):

        os.makedirs(
            OUTPUT_DIR
        )



    scores=generate_score_summary()



    agreement=load_json(
        AGREEMENT_FILE
    )



    # 保存json


    with open(

        os.path.join(
            OUTPUT_DIR,
            "score_report.json"
        ),

        "w",

        encoding="utf-8"

    ) as f:


        json.dump(

            scores,

            f,

            indent=4,

            ensure_ascii=False

        )




    with open(

        os.path.join(
            OUTPUT_DIR,
            "agreement_report.md"
        ),

        "w",

        encoding="utf-8"

    ) as f:


        f.write(

            json.dumps(

                agreement,

                indent=4,

                ensure_ascii=False

            )

        )




    markdown=generate_markdown(

        scores,

        agreement

    )



    with open(

        os.path.join(
            OUTPUT_DIR,
            "summary.md"
        ),

        "w",

        encoding="utf-8"

    ) as f:


        f.write(
            markdown
        )



    print(
        "报告生成完成!"
    )


    print(
        "位置:",
        OUTPUT_DIR
    )




if __name__=="__main__":

    main()
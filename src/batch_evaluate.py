"""
Batch HTML Evaluator

根据dataset.json批量评价HTML
"""


import os
import json


from verifier import verify_html



DATASET_FILE="../dataset.json"


SAMPLE_DIR="../samples"


RESULT_DIR="../results"




def evaluate_all():



    if not os.path.exists(RESULT_DIR):

        os.makedirs(RESULT_DIR)



    # 读取数据集


    with open(
        DATASET_FILE,
        "r",
        encoding="utf-8"
    ) as f:

        dataset=json.load(f)



    print(
        f"加载 {len(dataset)} 个测试样本"
    )



    for item in dataset:



        html_file=item["html"]

        requirement=item["requirement"]



        print(
            "\n正在评价:",
            html_file
        )



        html_path=os.path.join(
            SAMPLE_DIR,
            html_file
        )



        with open(
            html_path,
            "r",
            encoding="utf-8"
        ) as f:

            html=f.read()



        result=verify_html(

            html,

            requirement

        )



        # 保存额外信息


        result["html"]=html_file

        result["requirement"]=requirement



        output_file=html_file.replace(
            ".html",
            ".json"
        )



        output_path=os.path.join(
            RESULT_DIR,
            output_file
        )



        with open(
            output_path,
            "w",
            encoding="utf-8"
        ) as f:


            json.dump(

                result,

                f,

                ensure_ascii=False,

                indent=4

            )



        print(
            "保存:",
            output_path
        )




if __name__=="__main__":

    evaluate_all()
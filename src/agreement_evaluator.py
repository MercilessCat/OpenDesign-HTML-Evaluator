"""
Human Agreement Evaluator

计算:
Verifier评分
vs
人工评分

指标:
MAE
Accuracy
Pearson
Spearman
"""


import os
import json


import numpy as np

from scipy.stats import pearsonr
from scipy.stats import spearmanr



RESULT_DIR="../results"

HUMAN_FILE="human_scores.json"




def load_json(path):

    with open(
        path,
        "r",
        encoding="utf-8"
    ) as f:

        return json.load(f)




def calculate_mae(
        human,
        model
):

    return round(

        np.mean(
            np.abs(
                np.array(human)
                -
                np.array(model)
            )
        ),

        3
    )




def calculate_accuracy(
        human,
        model,
        threshold=1
):

    count=0


    for h,m in zip(
        human,
        model
    ):

        if abs(h-m)<=threshold:

            count+=1



    return round(
        count/len(human),
        3
    )




def evaluate():



    human_data=load_json(
        HUMAN_FILE
    )



    dimensions=[

        "functional",

        "usability",

        "aesthetic"

    ]



    report={}



    for dim in dimensions:


        human_scores=[]

        model_scores=[]



        for item in human_data:



            filename=item["html"]



            result_file=os.path.join(

                RESULT_DIR,

                filename.replace(
                    ".html",
                    ".json"
                )

            )



            result=load_json(
                result_file
            )



            human_scores.append(

                item[dim]

            )



            model_scores.append(

                result[dim]["score"]

            )



        mae=calculate_mae(

            human_scores,

            model_scores

        )


        acc=calculate_accuracy(

            human_scores,

            model_scores

        )


        pearson=round(

            pearsonr(

                human_scores,

                model_scores

            )[0],

            3

        )


        spearman=round(

            spearmanr(

                human_scores,

                model_scores

            )[0],

            3

        )


        report[dim]={

            "MAE":mae,

            "Accuracy":acc,

            "Pearson":pearson,

            "Spearman":spearman

        }



    print("\n===== Human Agreement Report =====\n")



    print(
        json.dumps(
            report,
            indent=4,
            ensure_ascii=False
        )
    )




    with open(

        "../agreement_report.json",

        "w",

        encoding="utf-8"

    ) as f:


        json.dump(

            report,

            f,

            indent=4,

            ensure_ascii=False

        )




if __name__=="__main__":

    evaluate()
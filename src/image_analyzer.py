"""
Image Analyzer

分析HTML截图基础视觉信息
"""


from PIL import Image
import os



def analyze_image(image_path):


    img=Image.open(image_path)


    width,height=img.size



    description=[]


    description.append(
        f"页面截图尺寸为 {width}x{height}"
    )


    ratio=round(
        width/height,
        2
    )


    description.append(
        f"页面宽高比例为 {ratio}"
    )



    # 判断亮度

    img_rgb=img.convert("RGB")


    pixels=list(
        img_rgb.getdata()
    )


    avg=sum(
        sum(p)
        for p in pixels
    )/(len(pixels)*3)



    if avg>220:

        description.append(
            "页面整体偏明亮"
        )

    elif avg<80:

        description.append(
            "页面整体偏暗色"
        )

    else:

        description.append(
            "页面明暗适中"
        )



    return "\n".join(description)
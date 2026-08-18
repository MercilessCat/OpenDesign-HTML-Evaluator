"""
HTML Renderer

功能:
HTML -> 浏览器截图

用于视觉评价
"""


from playwright.sync_api import sync_playwright

import os



SCREENSHOT_DIR="../screenshot"



def render_html(
        html_path,
        output_name
):


    if not os.path.exists(
        SCREENSHOT_DIR
    ):

        os.makedirs(
            SCREENSHOT_DIR
        )


    output_path=os.path.join(
        SCREENSHOT_DIR,
        output_name
    )


    with sync_playwright() as p:


        browser=p.chromium.launch(
            headless=True
        )


        page=browser.new_page(
            viewport={
                "width":1280,
                "height":900
            }
        )


        page.goto(
            "file:///" + 
            os.path.abspath(html_path)
        )


        page.screenshot(
            path=output_path,
            full_page=True
        )


        browser.close()



    return output_path
import os


DASHSCOPE_BASE_URL = "https://token-plan.cn-beijing.maas.aliyuncs.com/compatible-mode/v1"

try:
    from config_local import DASHSCOPE_API_KEY as _DASHSCOPE_KEY
    API_KEY = _DASHSCOPE_KEY
except Exception:
    API_KEY = os.getenv("DASHSCOPE_API_KEY", "")

BASE_URL = DASHSCOPE_BASE_URL

MODEL = "qwen3.8-max"

VISION_BASE_URL = DASHSCOPE_BASE_URL
VISION_API_KEY = API_KEY
VISION_MODEL = "qwen3.8-max"

import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 模型配置
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
MODEL_NAME = os.getenv("MODEL_NAME", "gpt-3.5-turbo")

# 向量存储配置
VECTOR_STORE_DIR = os.getenv("VECTOR_STORE_DIR", "vector_store")

# 文档配置
DOCUMENTS_DIR = os.getenv("DOCUMENTS_DIR", "documents")

# 查询配置
TOP_K = int(os.getenv("TOP_K", "3"))
SIMILARITY_THRESHOLD = float(os.getenv("SIMILARITY_THRESHOLD", "0.7"))

# 系统提示配置
SYSTEM_PROMPT = os.getenv("SYSTEM_PROMPT", """你是一个有用的AI助手。
使用以下信息回答用户的问题。
如果你不知道答案，就说你不知道，不要编造信息。
基于提供的上下文给出详细的答案。
""")

# 图像生成配置
IMAGE_MODEL = os.getenv("IMAGE_MODEL", "gpt-4o")
IMAGE_OUTPUT_DIR = os.getenv("IMAGE_OUTPUT_DIR", "generated_images")
IMAGE_SIZE = os.getenv("IMAGE_SIZE", "1024x1024")
IMAGE_QUALITY = os.getenv("IMAGE_QUALITY", "standard")
IMAGE_STYLE = os.getenv("IMAGE_STYLE", "vivid") 
import os

from dotenv import load_dotenv
load_dotenv()

class Settings:
    """API配置"""

    # 文件上传配置
    MAX_FILE_SIZE = 1024 * 1024 * 150  # 最大文件大小50M
    ALLOWED_EXTENSIONS = ['.pdf', '.md', '.html','.docx']

    # 上传文件存储目录
    UPLOAD_DIR = 'data/uploads'

    # LLM模型配置
    LLM_PROVIDERS = {
        'zhipu':{
            'api_key':os.getenv('ZHIPU_API_KEY',''),
            'base_url':os.getenv('ZHIPU_BASE_URL','https://open.bigmodel.cn/api/paas/v4'),
            'default_model':os.getenv('ZHIPU_MODEL','glm-4-flash')
        },
        'qwen':{
            'api_key':os.getenv('DASHSCOPE_API_KEY',''),
            'base_url':os.getenv('DASHSCOPE_BASE_URL','https://dashscope.aliyuncs.com/compatible-mode/v1'),
            'default_model':os.getenv('DASHSCOPE_MODEL','qwen-plus')
        },
    }

    # 默认模型
    DEFAULT_MODEL = os.getenv('DEFAULT_MODEL')

    # LLM生成参数
    LLM_TEMPERATURE = 0.7
    LLM_MAX_TOKEN = 2000

    # 检索配置
    SEARCH_TOP_K = 3


# 全局配置对象
settings = Settings()
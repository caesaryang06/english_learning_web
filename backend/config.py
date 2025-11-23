import os
class Config:
    # 数据库
    DB_HOST = os.getenv('DB_HOST', '192.168.145.129')
    DB_USER = os.getenv('DB_USER', 'root')
    DB_PASSWORD = os.getenv('DB_PASSWORD', '123456')
    DB_DATABASE = os.getenv('DB_DATABASE', 'english_learning')

    # Azure TTS
    AZURE_TTS_KEY = os.getenv('AZURE_SUBSCRIPTION_KEY')
    AZURE_TTS_REGION = os.getenv('AZURE_REGION', 'eastus')


    # CORS 配置
    CORS_ORIGINS = os.getenv('CORS_ORIGINS', '*').split(',')

    # 其他配置
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key')
    DEBUG = os.getenv('DEBUG', 'False') == 'True'

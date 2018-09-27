import logging
from datetime import timedelta

from redis import StrictRedis


class Config:
    '''定义和配置对象'''
    DEBUG = True  # 调试
    SQLALCHEMY_DATABASE_URI = 'mysql://root:mysql@127.0.0.1:3306/txt'  # 链接mysql数据库
    SQLALCHEMY_TRACK_MODIFICATIONS = False  # 是否进行数据库修改追踪
    SQLALCHEMY_ECHO = False  # 是否显示ｓｑｌ语句
    REDIS_HOST = "127.0.0.1"  # ｒｅｄｉｓ的ip
    REDIS_PORT = 6379  # ｒｅｄｉｓ的端口
    SESSION_TYPE = 'redis'
    SESSION_REDIS = StrictRedis(host=REDIS_HOST, port=REDIS_PORT)  # 一个存储ｓｅｓｓｉｏｎ的　ｒｅｄｉｓｔｒｉｂｕｔｅ对象
    SESSION_USE_SIGNER = True  # 使用加密sessionid
    SECRET_KEY = 'sST3avVy9ntQ9tSNWjRwgSwDOe9uzmidlp1xQjHiEGGOqNNBwN+ZXDgkWtCCJiBl'  # 加密的秘钥
    PERMANENT_SESSION_LIFETIME = timedelta(days=7)  # 设置过期时间
    SQLALCHEMY_COMMIT_ON_TEARDOWN = True


class DevelopmentConfig(Config):  # 调试环境
    LOG_LEVEL = logging.DEBUG


class ProductConfig(Config):  # 生产环境
    DEBUG = False
    REDIS_HOST = "127.0.0.1"
    REDIS_PORT = 6379
    LOG_LEVEL = logging.ERROR


config_dict = {
    'dev': DevelopmentConfig,
    'pro': ProductConfig
}

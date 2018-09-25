import logging
from datetime import timedelta
from redis import StrictRedis


class Config:
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'mysql://root:mysql@127.0.0.1:3306/txt'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = False
    REDIS_HOST = '127.0.0.1'
    REDIS_PORT = 6379
    SESSION_TYPE = 'redis'
    SESSION_REDIS = StrictRedis(host=REDIS_HOST, port=REDIS_PORT)
    SESSION_USE_SIGNER = True
    SECRET_KEY = '124'
    PERMANENT_SESSION_LIFETIME = timedelta(days=31)


class DevelopmentConfig(Config):
    LOG_TYPE  = logging.DEBUG


class ProductionConfig(Config):
    DEBUG = False
    LOG_TYPE = logging.DEBUG


type_dict = {
    'dev': DevelopmentConfig,
    'pro': ProductionConfig
}

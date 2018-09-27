import logging
from logging.handlers import RotatingFileHandler
from flask import Flask
from flask_migrate import Migrate
from flask_session import Session
from flask_sqlalchemy import SQLAlchemy
from redis import StrictRedis
from config import type_dict

db = None  # type:SQLAlchemy
sr = None  # type:StrictRedis


def setup_log(styl_level):  # 将日志保存到文件中
    # 设置日志的记录等级
    logging.basicConfig(level=styl_level)  # 调试debug级
    # 创建日志记录器，指明日志保存的路径、每个日志文件的最大大小、保存的日志文件个数上限
    file_log_handler = RotatingFileHandler("logs/log", maxBytes=1024 * 1024 * 100, backupCount=10)
    # 创建日志记录的格式 日志等级 输入日志信息的文件名 行数 日志信息
    formatter = logging.Formatter('%(levelname)s %(pathname)s:%(lineno)d %(message)s')
    # 为刚创建的日志记录器设置日志记录格式
    file_log_handler.setFormatter(formatter)
    # 为全局的日志工具对象（flask app使用的）添加日志记录器
    logging.getLogger().addHandler(file_log_handler)


def create_app(type):
    app = Flask(__name__)
    global db, sr
    db = SQLAlchemy(app)
    config_class = type_dict[type]
    sr = StrictRedis(host=config_class.REDIS_HOST, port=config_class.REDIS_PORT,decode_responses=True)
    app.config.from_object(config_class)
    Session(app)
    Migrate(app, db)
    from info.modules.home import blu_home
    app.register_blueprint(blu_home)
    from info.modules.passport import blu_passport
    app.register_blueprint(blu_passport)
    setup_log(config_class.LOG_TYPE)
    import info.models
    return app

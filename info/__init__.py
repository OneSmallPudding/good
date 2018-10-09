import logging
from logging.handlers import RotatingFileHandler
from flask import Flask, g,render_template
from flask_migrate import Migrate
from flask_session import Session
from flask_sqlalchemy import SQLAlchemy
from redis import StrictRedis
from config import config_dict

db = None  # type:SQLAlchemy
sr = None  # type:StrictRedis


def set_log(log_level):
    # 设置日志的记录等级
    logging.basicConfig(level=log_level)  # 调试debug级
    # 创建日志记录器，指明日志保存的路径、每个日志文件的最大大小、保存的日志文件个数上限
    file_log_handler = RotatingFileHandler("logs/log", maxBytes=1024 * 1024 * 100, backupCount=10)
    # 创建日志记录的格式 日志等级 输入日志信息的文件名 行数 日志信息
    formatter = logging.Formatter('%(levelname)s %(pathname)s:%(lineno)d %(message)s')
    # 为刚创建的日志记录器设置日志记录格式
    file_log_handler.setFormatter(formatter)
    # 为全局的日志工具对象（flask app使用的）添加日志记录器
    logging.getLogger().addHandler(file_log_handler)


def create_app(config_type):  # 工厂函数，提供物料创建应用，工厂模式
    '''创建ａｐｐ'''
    config_class = config_dict[config_type]
    app = Flask(__name__, static_folder='static')
    # 用对象加载配置信息
    app.config.from_object(config_class)
    global db, sr
    # 创建数据库链接对象
    db = SQLAlchemy(app)
    # 创建ｒｅｄｉｓ数据撸链接对象
    sr = StrictRedis(host=config_class.REDIS_HOST, port=config_class.REDIS_PORT, decode_responses=True)
    # 创建ｓｅｓｓｉｏｎ数据链接对象　，ｓｅｓｓｉｏｎ对象会配置里面选择自动存储不用接收对象，进行手动操作
    Session(app)
    # 初始化迁移添加迁移命令
    Migrate(app, db)
    # 3应用注册蓝图
    from info.modules.home import blu_home  # 如果内容只使用一次就在使用前导入
    app.register_blueprint(blu_home)
    # 3应用注册蓝图
    from info.modules.passport import blu_passport  # 如果内容只使用一次就在使用前导入
    app.register_blueprint(blu_passport)

    from info.modules.news import blu_news  # 如果内容只使用一次就在使用前导入
    app.register_blueprint(blu_news)

    from info.modules.user import blu_user  # 如果内容只使用一次就在使用前导入
    app.register_blueprint(blu_user)
    # 配置日志
    set_log(config_class.LOG_LEVEL)
    # 关联模型
    # from info.models import *  #函数内部不能用ｆｒｏｍ　　ｉｍｐｏｒｔ　　*
    import info.models
    # 注册过滤器
    from info.common import func_index_convert
    app.add_template_filter(func_index_convert, 'index_convert')
    from  info.common import user_login_data
    @app.errorhandler(404)
    @user_login_data
    def error_handler_404(error):
        user = g.user
        user = user.to_dict() if user else None
        return render_template('404.html',user =user)
    return app

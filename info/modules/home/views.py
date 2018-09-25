import logging
from flask import session, current_app
from info import sr
from info.modules.home import blu_home


@blu_home.route('/')
def index():
    sr.set('name','xiaohau')
    session['name'] = 'nnnnnnn'
    logging.error('yige错误啊')
    current_app.logger.error('异常a')
    return 'index'

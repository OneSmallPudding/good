from flask import current_app, render_template, session
from info import sr
import logging

# 2蓝图注册路由
from info.models import User
from info.modules.home import blu_home


@blu_home.route('/')
def index():
    user_id = session.get('user_id')
    user = None
    if user_id:
        try:
            user = User.query.get(user_id)
        except BaseException as e:
            current_app.logger.error(e)
    user = user.to_dict() if user else None
    return render_template('index.html', user=user)
    # return '1111'


# 设置图标
@blu_home.route('/favicon.ico')
def favicon():
    # flask 内置了语法，可以返回静态文件
    # flask 中内置的访问静态页面文件的路由也会调用这个方法
    return current_app.send_static_file("news/favicon.ico")

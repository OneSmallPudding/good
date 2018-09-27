from flask import current_app, render_template
from info import sr
from . import blu_home
import logging


# 2蓝图注册路由
@blu_home.route('/')
def index():
    return render_template('index.html')

# 设置图标
@blu_home.route('/favicon.ico')
def favicon():
    # flask 内置了语法，可以返回静态文件
    # flask 中内置的访问静态页面文件的路由也会调用这个方法
    return current_app.send_static_file('/news/favicon.ico')

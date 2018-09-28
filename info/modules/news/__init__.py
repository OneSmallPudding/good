from flask import Blueprint

# 1.创建蓝图
blu_news = Blueprint('news_blu', __name__,url_prefix='/news')
# 4关联试图函数
from .views import *

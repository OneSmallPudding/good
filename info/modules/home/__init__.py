from flask import Blueprint

# 1.创建蓝图
blu_home = Blueprint('home_blu', __name__)
# 4关联试图函数
from .views import *

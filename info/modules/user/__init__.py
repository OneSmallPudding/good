from flask import Blueprint

# 1.创建蓝图
blu_user = Blueprint('user_blu', __name__, url_prefix='/user')
# 4关联试图函数
from .views import *

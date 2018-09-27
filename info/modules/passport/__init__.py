from flask import Blueprint

# 1.创建蓝图
blu_passport = Blueprint('passport_blu', __name__, url_prefix='/passport')
# 4关联试图函数
from .views import *

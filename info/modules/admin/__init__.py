from flask import Blueprint

# 1.创建蓝图
blu_admin = Blueprint('admin_blu', __name__, url_prefix='/admin')


@blu_admin.before_request
def check_superuser():
    is_admin = session.get('is_admin')
    if not is_admin and not request.url.endswith("/admin/login"):
        return redirect(url_for("home_blu.index"))


# 4关联试图函数
from .views import *

# 一个过滤器排行列表选择样式时使用
import functools
from flask import session, current_app, g
from info.models import User


def func_index_convert(index):
    index_dict = {1: 'first', 2: 'second', 3: 'third'}
    return index_dict.get(index, '')


def user_login_data(f):
    @functools.wraps(f)
    def wrapper(*args, **kwargs):
        # 查询登陆的人
        user_id = session.get('user_id')
        user = None
        if user_id:
            try:
                user = User.query.get(user_id)
            except BaseException as e:
                current_app.logger.error(e)
        g.user = user
        return f(*args, **kwargs)

    return wrapper

access_key = "kJ8wVO7lmFGsdvtI5M7eQDEJ1eT3Vrygb4SmR00E"
secret_key= "rGwHyAvnlLK7rU4htRpNYzpuz0OHJKzX2O1LWTNl"
bucket_name = "infonews"  # 存储空间名称

#b保存到七牛云
def img_upload(data):
    import qiniu
    q = qiniu.Auth(access_key, secret_key)
    key = None
    token = q.upload_token(bucket_name)
    ret, info = qiniu.put_data(token, key, data)
    if ret is not None:
        return ret.get('key')
    else:
        raise BaseException(info)

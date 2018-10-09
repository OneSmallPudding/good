from info.common import user_login_data
from info.constants import USER_COLLECTION_MAX_NEWS
from info.models import tb_user_collection
from info.modules.user import blu_user
from flask import render_template, g, url_for, abort, request, jsonify, current_app

from info.utils.response_code import RET, error_map


@blu_user.route('/user_info')
@user_login_data
def user_info():
    user = g.user
    if not user:
        return render_template(url_for('/'))
    user = user.to_dict() if user else None
    return render_template('user.html', user=user)


# 基本资料
@blu_user.route('/base_info', methods=['GET', 'POST'])
@user_login_data
def base_info():
    user = g.user
    if not user:
        return abort(404)
    if request.method == 'GET':
        return render_template('user_base_info.html', user=user)
    # 获取参数
    signature = request.json.get('signature')
    nick_name = request.json.get('nick_name')
    gender = request.json.get('gender')
    if not all([signature, nick_name, gender]):
        return jsonify(errno=RET.PARAMERR, errmsg=error_map[RET.PARAMERR])
    if gender not in ['MAN', 'WOMAN']:
        return jsonify(errno=RET.PARAMERR, errmsg=error_map[RET.PARAMERR])
    user.signature = signature
    user.nick_name = nick_name
    user.gender = gender
    return jsonify(errno=RET.OK, errmsg=error_map[RET.OK])


# 密码修改
@blu_user.route('/pass_info', methods=['GET', 'POST'])
@user_login_data
def pass_info():
    user = g.user
    if not user:
        return abort(404)
    if request.method == 'GET':
        return render_template('user_pass_info.html')
    old_password = request.json.get('old_password')
    new_password = request.json.get('new_password')
    if not all([old_password, new_password]):
        return jsonify(errno=RET.PARAMERR, errmsg=error_map[RET.PARAMERR])
    if not user.check_password(old_password):
        return jsonify(errno=RET.PWDERR, errmsg=error_map[RET.PWDERR])
    user.password = new_password
    return jsonify(errno=RET.OK, errmsg=error_map[RET.OK])


# 收藏
@blu_user.route('/collection')
@user_login_data
def collection():
    user = g.user
    if not user:
        return abort(404)
    page = request.args.get("p", 1)
    try:
        page = int(page)
    except BaseException as e:
        current_app.logger.error(e)
        page = 1
    news_list = []
    total_page = 1
    try:
        pn = user.collection_news.order_by(tb_user_collection.c.create_time.desc()).paginate(page,USER_COLLECTION_MAX_NEWS)
        news_list = pn.items
        cur_page =page
        total_page = pn.pages
    except BaseException as e:
        current_app.logger.error(e)
    data = {
        "news_list":[news.to_dict() for news in news_list],
        "cur_page": page,
        "total_page": total_page
    }

    return render_template('user_collection.html',data = data )

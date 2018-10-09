from info.common import user_login_data
from info.modules.user import blu_user
from flask import render_template, g, url_for, abort, request, jsonify

from info.utils.response_code import RET, error_map


@blu_user.route('/user_info')
@user_login_data
def user_info():
    user = g.user
    if not user:
        return render_template(url_for('/'))
    user = user.to_dict() if user else None
    return render_template('user.html', user=user)


@blu_user.route('/base_info', methods=['GET', 'POST'])
@user_login_data
def base_info():
    user = g.user
    if not user:
        return render_template(abort(404))
    if request.method == 'GET':
        return render_template('user_base_info.html')
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

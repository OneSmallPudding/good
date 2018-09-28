import random
import re
from datetime import datetime
from flask import request, abort, current_app, make_response, Response, jsonify, session
from info import sr, db
from info.lib.yuntongxun.sms import CCP
from info.models import User
from info.modules.news import blu_news
from info.modules.passport import blu_passport
from info.utils.captcha.pic_captcha import captcha
from info.utils.response_code import RET, error_map


# 图片验证码
@blu_news.route('/passport/get_img_code')
@blu_passport.route('/get_img_code')
def get_img_code():
    # 1获取数据
    img_code_id = request.args.get('img_code_id')
    # 验证下前段发的是否是个空的
    if not img_code_id:
        return abort(403)
    # ２生成图片
    img_name, img_text, img_bytes = captcha.generate_captcha()
    # ３保存图片文字部分和图片的ｋ
    try:
        sr.set('img_code_id' + img_code_id, img_text, ex=100)
    except BaseException as e:
        current_app.logger.error(e)
        return abort(500)
    # ４发送图片
    # 自定义相应对象
    response = make_response(img_bytes)  # type:Response
    response.content_type = 'image/jpeg'
    return response


# 短信验证码
@blu_passport.route('/get_sms_code', methods=['POST'])
def get_sms_code():
    # １获取数据
    mobile = request.json.get('mobile')
    img_code = request.json.get('img_code')
    img_code_id = request.json.get('img_code_id')
    # 判断前端数据
    if not all([mobile, img_code_id, img_code]):
        return jsonify(errno=RET.PARAMERR, errmsg=error_map[RET.PARAMERR])
    if not re.match('1[35678]\d{9}$', mobile):
        return jsonify(errno=RET.PARAMERR, errmsg=error_map[RET.PARAMERR])
    # ２根据图片ｋ取出图片验证码
    try:
        real_img_code = sr.get('img_code_id' + img_code_id)
    except BaseException as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg=error_map[RET.DBERR])
    # 3验证图片验证码是否正确和是否过期
    if not real_img_code:
        return jsonify(errno=RET.PARAMERR, errmsg='验证码已过期')
    if real_img_code != img_code.upper():
        return jsonify(errno=RET.PARAMERR, errmsg='验证码错误')
    # 验证用户是否存在
    try:
        user = User.query.filter_by(mobile=mobile).first()
    except BaseException as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg=error_map[RET.DBERR])
    if user:
        return jsonify(errno=RET.DATAERR, errmsg='用户已存在')
    # ４发送短信
    # 随机吗
    sms_code = '%06d' % random.randint(0, 999999)
    current_app.logger.error('短信验证码是%s' % sms_code)
    # 注意：
    #  测试的短信模板编号为1
    # response_code = CCP().send_template_sms(mobile, [sms_code, 5], 1)
    # if response_code == 0:
    #     return jsonify(errno=RET.THIRDERR, errmsg=error_map[RET.THIRDERR])
    # ５保存短信验证码
    try:
        # sr.set('sms_code_id' + mobile, sms_code, ex=2000)
        sr.set('sms_code_id' + mobile, sms_code, ex=7000)
    except BaseException as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg=error_map[RET.DBERR])
    # ６返回发送结果
    return jsonify(errno=RET.OK, errmsg=error_map[RET.OK])


# 用户注册
@blu_passport.route('/register', methods=['POST'])
def register():
    # １获取参数
    mobile = request.json.get('mobile')
    password = request.json.get('password')
    sms_code = request.json.get('sms_code')
    # ２验证参数
    if not all([mobile, password, sms_code]):
        return jsonify(errno=RET.PARAMERR, errmsg=error_map[RET.PARAMERR])
    if not re.match('1[35678]\d{9}$', mobile):
        return jsonify(errno=RET.PARAMERR, errmsg=error_map[RET.PARAMERR])
    # 3根据手机号取出短信验证码
    try:
        # sr.set('sms_code_id' + mobile, sms_code, ex=7000)
        real_sms_code = sr.get('sms_code_id' + mobile)
    except BaseException as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg=error_map[RET.DBERR])
    # ４验证短信验证码
    if not real_sms_code:
        return jsonify(errno=RET.PARAMERR, errmsg='验证码过期')
    if real_sms_code != sms_code:
        return jsonify(errno=RET.PARAMERR, errmsg='验证码错误')
    # ５保存数据
    user = User()
    user.mobile = mobile
    user.password = password
    user.nick_name = mobile
    user.last_login = datetime.now()
    try:
        db.session.add(user)
        db.session.commit()
    except BaseException as e:
        current_app.logger.error(e)
        db.session.rollback()
        return jsonify(errno=RET.DBERR, errmsg=error_map[RET.DBERR])
    session['user_id'] = user.id
    # ６返回结果
    return jsonify(errno=RET.OK, errmsg=error_map[RET.OK])


# 用户登陆
@blu_passport.route('/login', methods=['POST'])
def login():
    # 请求参数
    mobile = request.json.get('mobile')
    password = request.json.get('password')
    # 验证参数
    if not all([mobile, password]):
        print('1')
        return jsonify(errno=RET.PARAMERR, errmsg=error_map[RET.PARAMERR])
    # 验证手机号
    if not re.match('1[35678]\d{9}$', mobile):
        print('2')
        return jsonify(errno=RET.PARAMERR, errmsg=error_map[RET.PARAMERR])
    # 判断用户是否存在
    try:
        user = User.query.filter_by(mobile=mobile).first()
    except BaseException as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg=error_map[RET.DBERR])
    if not user:
        return jsonify(errno=RET.DATAERR, errmsg='用户已存在')
    # 验证密码
    if not user.check_password(password):
        return jsonify(errno=RET.PARAMERR, errmsg='密码错误')
    # 记录最后登录时间(保存到是一个日期对象)
    user.last_login = datetime.now()
    # 状态保持（免密码登录）  保存用户的主键， 就可以取出用户的所有信息
    session["user_id"] = user.id
    # 返回
    return jsonify(errno=RET.OK, errmsg=error_map[RET.OK])


# 用户退出登陆
@blu_passport.route('/logout')
def logout():
    session.pop('user_id', None)
    return jsonify(errno=RET.OK, errmsg=error_map[RET.OK])

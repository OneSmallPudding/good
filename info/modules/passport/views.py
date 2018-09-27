import random
import re

from flask import request, abort, current_app, jsonify, make_response, Response

from info import sr
from info.modules.passport import blu_passport
from info.utils.captcha.pic_captcha import captcha
from info.utils.response_code import RET, error_map


@blu_passport.route('/get_img_code')
def get_img_code():
    # 获取参数
    img_code_id = request.args.get("img_code_id")
    # 判断获取的参数
    if not img_code_id:
        return abort(403)
    # 生成图片验证码
    img_name, img_text, img_bytes = captcha.generate_captcha()
    current_app.logger.error(img_text)
    # 保存验证码文字
    try:
        sr.set("img_code_id" + img_code_id, img_text, ex=120)
    except BaseException as e:
        current_app.logger.error(e)
        return abort(500)
    # 设置响应头,改变响应的格式
    response = make_response(img_bytes)  # type:Response
    response.content_type = 'image/jpeg'
    # 发送验证码
    return response


@blu_passport.route('/get_sms_code', methods=['POST'])
def get_sms_code():
    # 获取参数
    mobile = request.json.get('mobile')
    img_code = request.json.get('img_code')
    img_code_id = request.json.get('img_code_id')
    # 验证参数
    if not all([mobile, img_code, img_code_id]):
        print('1')
        return jsonify(errno=RET.PARAMERR, errmsg=error_map[RET.PARAMERR])
    # 验证,正则手机号
    if not re.match('1[35678]\d{9}$', mobile):
        print('2')
        return jsonify(errno=RET.PARAMERR, errmsg=error_map[RET.PARAMERR])
    # 根据图片的k取出验证码
    try:
        real_img_code = sr.get('img_code_id' + img_code_id)
    except BaseException as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmg=error_map[RET.DBERR])
    # 验证验证码是否过期
    if not real_img_code:
        return jsonify(errno=RET.PARAMERR, errmsg='验证码过期')
    # 验证验证码
    if real_img_code != img_code.upper():
        return jsonify(errno=RET.PARAMERR, errmsg='验证码错误')

    # 生成短信
    sms_code = '%06d' % random.randint(0, 999999)
    current_app.logger.error(sms_code)
    # 返回短信验证码
    return jsonify(errno=RET.OK, errmsg=error_map[RET.OK])

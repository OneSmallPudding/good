from info import db
from info.common import user_login_data, img_upload
from info.constants import USER_COLLECTION_MAX_NEWS, QINIU_DOMIN_PREFIX
from info.models import tb_user_collection, Category, News
from info.modules.user import blu_user
from flask import render_template, g, url_for, abort, request, jsonify, current_app

from info.utils.response_code import RET, error_map


@blu_user.route('/user_info')
@user_login_data
def user_info():
    user = g.user
    if not user:
        return render_template(url_for('home_blu.index'))
    user = user.to_dict() if user else None
    return render_template('news/user.html', user=user)


# 基本资料
@blu_user.route('/base_info', methods=['GET', 'POST'])
@user_login_data
def base_info():
    user = g.user
    if not user:
        return abort(404)
    if request.method == 'GET':
        return render_template('news/user_base_info.html', user=user)
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
        return render_template('news/user_pass_info.html')
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
    cur_page = 1
    total_page = 1
    try:
        pn = user.collection_news.order_by(tb_user_collection.c.create_time.desc()).paginate(page,
                                                                                             USER_COLLECTION_MAX_NEWS)
        news_list = pn.items
        cur_page = pn.page
        total_page = pn.pages
    except BaseException as e:
        current_app.logger.error(e)
    data = {
        "news_list": [news.to_dict() for news in news_list],
        "cur_page": cur_page,
        "total_page": total_page
    }

    return render_template('news/user_collection.html', data=data)


# 发布新闻
@blu_user.route('/news_release', methods=['GET', 'POST'])
@user_login_data
def news_release():
    user = g.user
    if not user:
        return abort(404)
    if request.method == 'GET':
        categories = []
        try:
            categories = Category.query.all()
        except BaseException as e:
            current_app.logger.error(e)
        if len(categories):
            categories.pop(0)
        return render_template('news/user_news_release.html', categories=categories)
    title = request.form.get("title")
    category_id = request.form.get("category_id")
    digest = request.form.get("digest")
    index_image = request.files.get("index_image")
    content = request.form.get("content")
    if not all([title, category_id, digest, index_image, content]):
        return jsonify(errno=RET.PARAMERR, errmsg=error_map[RET.PARAMERR])
    try:
        category_id = int(category_id)
    except BaseException as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.PARAMERR, errmsg=error_map[RET.PARAMERR])

    # 创建新闻模型
    news = News()
    news.title = title
    news.category_id = category_id
    news.digest = digest
    news.content = content
    news.source = "个人发布"  # 新闻来源
    news.user_id = user.id  # 新闻作者id
    news.status = 1  # 新闻审核状态
    try:
        img_bytes = index_image.read()
        file_name = img_upload(img_bytes)
        news.index_image_url = QINIU_DOMIN_PREFIX + file_name
        print(news.index_image_url)
    except BaseException as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.PARAMERR, errmsg=error_map[RET.PARAMERR])
    db.session.add(news)
    return jsonify(errno=RET.OK, errmsg=error_map[RET.OK])


# 头像设置
@blu_user.route('/pic_info', methods=['GET', 'POST'])
@user_login_data
def pic_info():
    user = g.user
    if not user:
        return abort(404)
    if request.method == 'GET':
        user = user.to_dict() if user else None
        return render_template('news/user_pic_info.html', user=user)
    try:
        img_bytes = request.files.get('avatar').read()
        try:
            file_name = img_upload(img_bytes)
            user.avatar_url = file_name
        except BaseException as e:
            current_app.logger.error(e)
            return jsonify(errno=RET.THIRDERR, errmsg=error_map[RET.THIRDERR])
    except BaseException as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.PARAMERR, errmsg=error_map[RET.PARAMERR])
    return jsonify(errno=RET.OK, errmsg=error_map[RET.OK], data=user.to_dict())


# 发布
@blu_user.route('/news_list')
@user_login_data
def news_list():
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
    cur_page = 1
    total_pages = 1
    try:
        pn = user.news_list.order_by(News.create_time.desc()).paginate(page, USER_COLLECTION_MAX_NEWS)
        news_list = pn.items
        cur_page = pn.page
        total_pages = pn.pages
    except BaseException as e:
        current_app.logger.error(e)
    data = {
        "news_list": [news.to_review_dict() for news in news_list],
        "cur_page": cur_page,
        "total_page": total_pages
    }

    return render_template('news/user_news_list.html', data=data)

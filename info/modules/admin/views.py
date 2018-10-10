import time
from datetime import datetime, timedelta

from info.common import user_login_data
from info.constants import ADMIN_USER_PAGE_MAX_COUNT
from info.models import User, News
from info.modules.admin import blu_admin
from flask import render_template, request, current_app, session, redirect, url_for, g, abort, jsonify

from info.utils.response_code import RET, error_map


@blu_admin.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        user_id = session.get("user_id")
        is_admin = session.get("is_admin")
        if all([user_id, is_admin]):
            return redirect(url_for('admin_blu.index'))
        return render_template('admin/login.html')
    username = request.form.get('username')
    password = request.form.get('password')
    if not all([username, password]):
        return render_template('admin/login.html', errmsg='参数不全')
    try:
        user = User.query.filter(User.mobile == username, User.is_admin == True).first()
    except BaseException as  e:
        current_app.logger.error(e)
        return render_template('admin/login.html', errmsg='数据查询错误')
    if not user:
        return render_template('admin/login.html', errmsg='改管理员用户不存在')
    if not user.check_password(password):
        return render_template('admin/login.html', errmsg='用户名/密码错误')
    session['user_id'] = user.id
    session["is_admin"] = True
    return redirect(url_for('admin_blu.index'))


# 后台页
@blu_admin.route('/index')
@user_login_data
def index():
    return render_template('admin/index.html', user=g.user.to_dict())


# 用户统计
@blu_admin.route('/user_count')
def user_count():
    # 用户总数
    total_count = 0
    try:
        total_count = User.query.filter(User.is_admin == False).count()
    except BaseException as e:
        current_app.logger.error(e)
    # 月增人数
    mon_count = 0
    t = time.localtime()
    data_mon_str = '%d-%02d-01' % (t.tm_year, t.tm_mon)
    data_mon = datetime.strptime(data_mon_str, "%Y-%m-%d")
    try:
        mon_count = User.query.filter(User.is_admin == False, User.create_time >= data_mon).count()
    except BaseException as e:
        current_app.logger.error(e)
    # 日增人数
    day_count = 0

    data_mon_str = '%d-%02d-%02d' % (t.tm_year, t.tm_mon, t.tm_mday)
    date_day = datetime.strptime(data_mon_str, "%Y-%m-%d")
    try:
        day_count = User.query.filter(User.is_admin == False, User.create_time >= date_day).count()
    except BaseException as e:
        current_app.logger.error(e)
    # 获取30天的注册人数 情况
    active_count = []
    active_time = []
    for i in range(0, 30):
        begin_date = date_day - timedelta(days=i)
        end_date = date_day + timedelta(days=1) - timedelta(days=i)
        try:
            one_day_count = User.query.filter(User.is_admin == False, User.create_time >= begin_date,
                                              User.create_time <=
                                              end_date).count()
            active_count.append(one_day_count)
            one_day_str = begin_date.strftime("%Y-%m-%d")
            active_time.append(one_day_str)
        except BaseException as e:
            current_app.logger.error(e)
    active_time.reverse()
    active_count.reverse()
    data = {
        'total_count': total_count,
        "mon_count": mon_count,
        "day_count": day_count,
        'active_count': active_count,
        'active_time': active_time
    }
    return render_template('admin/user_count.html', data=data)


# 退出登陆
@blu_admin.route('/logout')
def logout():
    session.pop('user_id', None)
    session.pop('is_admin', None)
    return redirect(url_for('home_blu.index'))


# 用户列表
@blu_admin.route('/user_list')
def user_list():
    page = request.args.get("p", 1)
    try:
        page = int(page)
    except BaseException as e:
        current_app.logger.error(e)
        return abort(403)
    user_list = []
    cur_page = 1
    total_page = 1
    try:
        pn = User.query.filter(User.is_admin == False).paginate(page, ADMIN_USER_PAGE_MAX_COUNT)
        user_list = [user.to_admin_dict() for user in pn.items]
        cur_page = pn.page
        total_page = pn.pages
    except BaseException as e:
        current_app.logger.error(e)
        return abort(403)
    data = {
        'user_list': user_list,
        'cur_page': cur_page,
        'total_page': total_page
    }
    return render_template('admin/user_list.html', data=data)


# 新闻审核
@blu_admin.route('/news_review')
def news_review():
    page = request.args.get("p", 1)
    keyword = request.args.get("keyword")
    try:
        page = int(page)
    except BaseException as e:
        current_app.logger.error(e)
        return abort(403)
    news_list = []
    cur_page = 1
    total_page = 1
    filter_list = []
    if keyword:
        filter_list.append(News.title.contains(keyword))
    try:
        pn = News.query.filter(*filter_list).paginate(page, ADMIN_USER_PAGE_MAX_COUNT)
        news_list = [news.to_review_dict() for news in pn.items]
        cur_page = pn.page
        total_page = pn.pages
    except BaseException as e:
        current_app.logger.error(e)
        return abort(403)
    data = {
        'news_list': news_list,
        'cur_page': cur_page,
        'total_page': total_page
    }
    return render_template('admin/news_review.html', data=data)


# 新闻审核详情页
@blu_admin.route('/news_review_detail/<int:news_id>')
def news_review_detail(news_id):
    try:
        news = News.query.get(news_id)
    except BaseException as     e:
        current_app.logger.error(e)
        return abort(500)
    if not news:
        return abort(403)
    return render_template('admin/news_review_detail.html', news=news.to_dict())


# 提交审核
@blu_admin.route('/news_review_action', methods=['POST'])
def news_review_action():
    news_id = request.json.get('news_id')
    action = request.json.get('action')
    reason = request.json.get('reason')
    if not all([news_id, action]):
        return jsonify(errno=RET.PARAMERR, errmsg=error_map[RET.PARAMERR])
    if action not in ["accept", "reject"]:
        return jsonify(errno=RET.PARAMERR, errmsg=error_map[RET.PARAMERR])
    try:
        news_id = int(news_id)
    except BaseException as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.PARAMERR, errmsg=error_map[RET.PARAMERR])
    try:
        news = News.query.get(news_id)
    except BaseException as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg=error_map[RET.DBERR])
    if not news:
        return jsonify(errno=RET.PARAMERR, errmsg=error_map[RET.PARAMERR])
    if action == "accept":
        news.status = 0
    else:
        news.status = -1
        if not reason:
            return jsonify(errno=RET.PARAMERR, errmsg=error_map[RET.PARAMERR])
        news.reason = reason
    return jsonify(errno=RET.OK, errmsg=error_map[RET.OK])


# 新闻审核
@blu_admin.route('/news_edit')
def news_edit():
    page = request.args.get("p", 1)
    keyword = request.args.get("keyword")
    try:
        page = int(page)
    except BaseException as e:
        current_app.logger.error(e)
        return abort(403)
    news_list = []
    cur_page = 1
    total_page = 1
    filter_list = []
    if keyword:
        filter_list.append(News.title.contains(keyword))
    try:
        pn = News.query.filter(*filter_list).paginate(page, ADMIN_USER_PAGE_MAX_COUNT)
        news_list = [news.to_review_dict() for news in pn.items]
        cur_page = pn.page
        total_page = pn.pages
    except BaseException as e:
        current_app.logger.error(e)
        return abort(403)
    data = {
        'news_list': news_list,
        'cur_page': cur_page,
        'total_page': total_page
    }
    return render_template('admin/news_edit.html', data=data)

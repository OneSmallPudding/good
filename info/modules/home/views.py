from flask import current_app, render_template, session, request, jsonify
from info import sr
import logging

# 2蓝图注册路由
from info.constants import CLICK_RANK_MAX_NEWS, HOME_PAGE_MAX_NEWS
from info.models import User, Category, News
from info.modules.home import blu_home
from info.utils.response_code import RET, error_map


@blu_home.route('/')
def index():
    # 查询登陆的人
    user_id = session.get('user_id')
    user = None
    if user_id:
        try:
            user = User.query.get(user_id)
        except BaseException as e:
            current_app.logger.error(e)
    user = user.to_dict() if user else None

    # 查询前10的新闻
    news_list = []
    try:
        news_list = News.query.order_by(News.clicks.desc()).limit(CLICK_RANK_MAX_NEWS).all()
    except BaseException as e:
        current_app.logger.error(e)
    news_list = [news.to_basic_dict() for news in news_list]

    # 获取分类列表
    categories = []
    try:
        categories = Category.query.all()
    except BaseException as e:
        current_app.logger.error(e)
    return render_template('index.html', user=user, news_list=news_list, categories=categories)


# 设置图标
@blu_home.route('/favicon.ico')
def favicon():
    # flask 内置了语法，可以返回静态文件
    # flask 中内置的访问静态页面文件的路由也会调用这个方法
    return current_app.send_static_file("news/favicon.ico")


# 获取新闻列表
@blu_home.route('/get_news_list')
def get_news_list():
    # 获取请求参数
    cid = request.args.get('cid')
    cur_page = request.args.get('cur_page')
    per_count = request.args.get('per_count', HOME_PAGE_MAX_NEWS)
    # 验证请求参数
    if not all([cid, current_app]):
        return jsonify(errno=RET.PARAMERR, errmsg=error_map[RET.PARAMERR])
    # 格式转换
    try:
        cid = int(cid)
        cur_page = int(cur_page)
        per_count = int(per_count)
    except BaseException as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.PARAMERR, errmsg=error_map[RET.PARAMERR])
    # 根据请求参数查询数据
    filter_list = []
    if cid != 1:
        filter_list.append(News.category_id == cid)
    try:
        pn = News.query.filter(*filter_list).order_by(News.create_time.desc()).paginate(cur_page, per_count)
    except BaseException as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg=error_map[RET.DBERR])
    data = {
        "news_list": [news.to_basic_dict() for news in pn.items],
        "total_page": pn.pages
    }
    # 返回数据
    return jsonify(errno=RET.OK, errmsg=error_map[RET.OK], data=data)

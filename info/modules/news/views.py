from flask import current_app, abort, render_template, session, g, jsonify, request
from info.common import user_login_data
from info.constants import CLICK_RANK_MAX_NEWS
from info.models import News, User
from info.modules.news import blu_news

# 详情页路由
from info.utils.response_code import RET, error_map


@blu_news.route('/<int:news_id>')
@user_login_data
def news_detail(news_id):
    try:
        news = News.query.get(news_id)
    except BaseException as e:
        current_app.logger.error(e)
        return abort(404)
    news.clicks += 1

    user = g.user

    # 查询前10的新闻
    news_list = []
    try:
        news_list = News.query.order_by(News.clicks.desc()).limit(CLICK_RANK_MAX_NEWS).all()
    except BaseException as e:
        current_app.logger.error(e)
    news_list = [news.to_basic_dict() for news in news_list]

    # 查看是否收藏
    is_collect = False
    if user:
        if news in user.collection_news:
            is_collect = True
    user = user.to_dict() if user else None
    return render_template('detail.html', news=news.to_dict(), user=user, news_list=news_list, is_collect=is_collect)


# 收藏
@blu_news.route('/news_collect', methods=['POST'])
@user_login_data
def news_collect():
    user = g.user
    if not user:
        return jsonify(errno=RET.SERVERERR, errmsg=error_map[RET.SESSIONERR])
    # 获取参数
    news_id = request.json.get('news_id')
    action = request.json.get('action')
    # 验证参数
    if not all([news_id, action]):
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
    if action not in ['collect', 'cancel_collect']:
        return jsonify(errno=RET.PARAMERR, errmsg=error_map[RET.PARAMERR])
    # 经行操作
    if action == 'collect':
        user.collection_news.append(news)
    else:
        user.collection_news.remove(news)
    # 返回
    return jsonify(errno=RET.OK, errmsg=error_map[RET.OK])

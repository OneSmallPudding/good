from flask import current_app, abort, render_template, session, g, jsonify, request

from info import db
from info.common import user_login_data
from info.constants import CLICK_RANK_MAX_NEWS
from info.models import News, User, Comment
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

    # 显示评论
    # 查询出所有的评论经行日期倒序,再进行熏染
    try:
        comments = news.comments.order_by(Comment.create_time.desc()).all()
    except BaseException as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg=error_map[RET.DBERR])
    # comments = [comment.to_dict() for comment in comments]

    # 显示点赞
    comment_list = []
    for comment in comments:
        comment_dict = comment.to_dict()
        is_like = False
        if user:
            if comment in user.like_comments:
                is_like = True
        comment_dict['is_like'] = is_like
        comment_list.append(comment_dict)
    is_follow = False
    if news.user and user:
        if news.user in user.followed:
            is_follow = True
    user = user.to_dict() if user else None
    return render_template('news/detail.html', news=news.to_dict(), user=user, news_list=news_list,
                           is_collect=is_collect,
                           comments=comment_list, is_follow=is_follow)


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


# 评论
@blu_news.route('/news_comment', methods=['POST'])
@user_login_data
def news_comment():
    user = g.user
    if not user:
        return jsonify(errno=RET.SERVERERR, errmsg=error_map[RET.SESSIONERR])
    # 获取参数
    comment_content = request.json.get('comment')
    news_id = request.json.get('news_id')
    parent_id = request.json.get('parent_id')
    # 验证参数
    if not all([comment_content, news_id]):
        print('1')
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
        return jsonify(errno=RET.PARAMERR, errmsg=error_map[RET.PARAMERR])
    if not news:
        print('2')
        return jsonify(errno=RET.PARAMERR, errmsg=error_map[RET.PARAMERR])
    # 操作
    comment = Comment()
    comment.content = comment_content
    comment.news_id = news_id
    comment.user_id = user.id
    if parent_id:
        try:
            parent_id = int(parent_id)
            comment.parent_id = parent_id
        except BaseException as e:
            current_app.logger.error(e)
            return jsonify(errno=RET.PARAMERR, errmsg=error_map[RET.PARAMERR])
    try:
        db.session.add(comment)
        db.session.commit()
    except BaseException as e:
        current_app.logger.error(e)
        db.session.rollback()
        return jsonify(errno=RET.DBERR, errmsg=error_map[RET.DBERR])
    # 返回
    return jsonify(errno=RET.OK, errmsg=error_map[RET.OK], data=comment.to_dict())


# 点赞
@blu_news.route('/comment_like', methods=['POST'])
@user_login_data
def comment_like():
    user = g.user
    if not user:
        return jsonify(errno=RET.SERVERERR, errmsg=error_map[RET.SESSIONERR])
    # 获取参数
    comment_id = request.json.get('comment_id')
    action = request.json.get('action')
    if not all([comment_id, action]):
        return jsonify(errno=RET.PARAMERR, errmsg=error_map[RET.PARAMERR])
    try:
        comment_id = int(comment_id)
    except BaseException as e:
        current_app.app.logger.error(e)
        return jsonify(errno=RET.PARAMERR, errmsg=error_map[RET.PARAMERR])
    try:
        comment = Comment.query.get(comment_id)
    except BaseException as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.PARAMERR, errmsg=error_map[RET.PARAMERR])
    if not comment:
        return jsonify(errno=RET.PARAMERR, errmsg=error_map[RET.PARAMERR])
    if action not in ["add", "remove"]:
        return jsonify(errno=RET.PARAMERR, errmsg=error_map[RET.PARAMERR])
    if action == "add":
        user.like_comments.append(comment)
        comment.like_count += 1
    else:
        user.like_comments.remove(comment)
        comment.like_count -= 1
    return jsonify(errno=RET.OK, errmsg=error_map[RET.OK])


# 收藏
@blu_news.route('/followed_user', methods=['POST'])
@user_login_data
def followed_user():
    user = g.user
    if not user:
        return jsonify(errno=RET.SERVERERR, errmsg=error_map[RET.SESSIONERR])
    # 获取参数
    user_id = request.json.get('user_id')
    action = request.json.get('action')
    # 验证参数
    if not all([user_id, action]):
        return jsonify(errno=RET.PARAMERR, errmsg=error_map[RET.PARAMERR])
    try:
        user_id = int(user_id)
    except BaseException as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.PARAMERR, errmsg=error_map[RET.PARAMERR])
    try:
        author = User.query.get(user_id)
    except BaseException as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg=error_map[RET.DBERR])
    if not author:
        return jsonify(errno=RET.PARAMERR, errmsg=error_map[RET.PARAMERR])
    if action not in ['follow', 'unfollow']:
        return jsonify(errno=RET.PARAMERR, errmsg=error_map[RET.PARAMERR])
    # 经行操作
    if action == 'follow':
        user.followed.append(author)
    else:
        user.followed.remove(author)
    # 返回
    return jsonify(errno=RET.OK, errmsg=error_map[RET.OK])

from flask import current_app, abort, render_template, session, g
from info.common import user_login_data
from info.constants import CLICK_RANK_MAX_NEWS
from info.models import News, User
from info.modules.news import blu_news


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
    user = user.to_dict() if user else None

    # 查询前10的新闻
    news_list = []
    try:
        news_list = News.query.order_by(News.clicks.desc()).limit(CLICK_RANK_MAX_NEWS).all()
    except BaseException as e:
        current_app.logger.error(e)
    news_list = [news.to_basic_dict() for news in news_list]
    return render_template('detail.html', news=news.to_dict(), user=user, news_list=news_list)

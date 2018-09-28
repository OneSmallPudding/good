from flask import current_app, abort,render_template

from info.models import News
from info.modules.news import blu_news


@blu_news.route('/<int:news_id>')
def news_detail(news_id):
    try:
        news = News.query.get(news_id)
    except BaseException as e:
        current_app.logger.error(e)
        return abort(404)
    return render_template('detail.html',news=news.to_dict())
import logging
from flask import session, current_app, render_template
from info import sr
from info.modules.home import blu_home


@blu_home.route('/')
def index():
    return render_template('index.html')


@blu_home.route('/favicon.ico')
def favicon():
    return current_app.send_static_file('news/favicon.ico')

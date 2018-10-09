from flask import current_app
from flask_script import Manager
from flask_migrate import MigrateCommand
from info import create_app

app = create_app('dev')
# 创建脚本管理器
mgr = Manager(app)
mgr.add_command('mc', MigrateCommand)


@mgr.option('-u', dest='username')  # python main.py create_superuser -u admin -p 123456
@mgr.option('-p', dest='password')
def create_superuser(username, password):
    if not all([username, password]):
        print('参数不完整')
        return
    from info.models import User
    from info import db
    user = User()
    user.mobile = username
    user.password = password
    user.nick_name = username
    user.is_admin = True
    try:
        db.session.add(user)
        db.session.commit()
    except BaseException as e:
        current_app.logger.error(e)
        db.session.rollback()
        print('创建失败')
        return
    print('创建成功')


if __name__ == '__main__':
    mgr.run()

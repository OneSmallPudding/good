from flask_script import Manager
from flask_migrate import MigrateCommand
from info import create_app

app = create_app('dev')
# 创建脚本管理器
mgr = Manager(app)
mgr.add_command('mc', MigrateCommand)

if __name__ == '__main__':
    mgr.run()

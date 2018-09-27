from flask_script import Manager
from flask_migrate import MigrateCommand

from info import create_app

app = create_app('dev')
mgr = Manager(app)
mgr.add_command('mc', MigrateCommand)

if __name__ == '__main__':
    mgr.run()

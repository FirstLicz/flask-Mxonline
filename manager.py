from flask_migrate import Migrate, MigrateCommand
from flask_script import Manager, Shell
import os

from app import create_app, db
from app.utils.utils import createsuperuser

app = create_app(os.getenv('FLASK_CONFIG') or 'default')

migrate = Migrate(app=app, db=db)
manager = Manager(app)


def make_shell_context():
    return dict(app=app, db=db)


manager.add_command('shell', Shell(make_context=make_shell_context))
manager.add_command('db', MigrateCommand)
manager.command(createsuperuser)

if __name__ == '__main__':
    manager.run()

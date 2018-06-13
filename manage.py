from flask_migrate import Migrate, MigrateCommand
from flask_script import Manager
from app import create_app
from app.models import db

app = create_app(config_name="development")


migrate = Migrate(app, db)
manager = Manager(app)

manager.add_command('db', MigrateCommand)


@manager.command
def create_db():
    db.create_all()


if __name__ == '__main__':
    manager.run()

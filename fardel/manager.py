from flask_script import Manager, Command
from flask_migrate import Migrate, MigrateCommand

from fardel import Fardel
from fardel.ext import db

from fardel.core.auth.models import User


def create_admin(email, password):
    u = User(email=email, password=password, is_admin=True)
    db.session.add(u)
    db.session.commit()
    print("Successfull created an admin.")


class FardelManager():
    def __init__(self, fardel: Fardel):
        self.fardel = fardel

        migrate = Migrate(fardel.app, db)
        self.flask_manager = Manager(fardel.app)
        self.flask_manager.add_command('db', MigrateCommand)

        self.register_commands()

    def register_commands(self):
        self.flask_manager.add_command("create_admin", Command(create_admin))

    def run(self):
        self.flask_manager.run()

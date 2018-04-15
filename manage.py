from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand

from web.app import create_app
from web.ext import db

from web.core.auth.models import User


app = create_app(develop=True)
migrate = Migrate(app, db)

manager = Manager(app)
manager.add_command('db', MigrateCommand)

@manager.command
def create_admin(email, password):
	u = User(email, password)
	db.session.add(u)
	try:
		db.session.commit()
	except:
		print("Error aquired, i think a user with this email already exists")
		return
	print("Successfull created an admin.")


if __name__ == "__main__":
    manager.run()
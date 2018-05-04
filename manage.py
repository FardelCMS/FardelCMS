from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand

from fardel.app import create_app
from fardel.ext import db

from fardel.core.auth.models import User


app = create_app(develop=True)
migrate = Migrate(app, db)

manager = Manager(app)
manager.add_command('db', MigrateCommand)

@manager.command
def create_admin(email, password):
	u = User(email=email, password=password, is_admin=True)
	db.session.add(u)
	try:
		db.session.commit()
	except:
		print("Error aquired, i think a user with this email already exists")
		return
	print("Successfull created an admin.")

@manager.command
def generate_fake():
	from fardel.core.auth.models import User
	from fardel.apps.blog.models import Category, Post, Tag, Comment, PostStatus

	PostStatus.generate_default()
	# User._bootstrap(1000)
	# Category._bootstrap(10)
	# Tag._bootstrap(40)
	# Post._bootstrap(50)
	Comment._bootstrap(1000)

if __name__ == "__main__":
    manager.run()
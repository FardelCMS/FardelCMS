import click
import os

from flask.cli import FlaskGroup
from flask_migrate import Migrate

from fardel import Fardel
from fardel.ext import db

from fardel.core.auth.models import User


def create_admin(email, password):
    u = User(email=email, password=password, is_admin=True)
    db.session.add(u)
    db.session.commit()
    print("Successfull created an admin.")


class FardelManager:
    def __init__(self, fardel: Fardel):
        self.fardel = fardel

        Migrate(fardel.app, db)

        # self.register_commands()

        self.cli = FlaskGroup(
            help="A general utility script for Fardel applications.",
            create_app=self.get_flask_app,
        )

    def get_flask_app(self, *args, **kwargs):
        return self.fardel.app

    def register_commands(self):
        self.fardel.app.cli.command(create_admin)

    def run(self):
        self.cli.main()

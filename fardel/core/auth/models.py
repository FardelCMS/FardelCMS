import json
import time
import bcrypt

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm.attributes import flag_modified

from flask_babel import gettext
from flask import current_app, jsonify, render_template
from flask_login import UserMixin

from fardel.ext import db, jwt, login_manager
from fardel.core.utils import random_string

__all__ = ['User', 'Permission', 'Group', 'RevokedToken', 'setup_permissions']

CONFIRM_EMAIL = "email_confirm"

TEMPLATES = {
    "confirm_email": {
        "txt": "confirm_email.txt",
        "html": "confirm_email.html",
    }
}


def setup_permissions():
    Group.setup_permissions()
    User.setup_permissions()
    Permission.setup_permissions()


class AbstractModelWithPermission():
    @classmethod
    def setup_permissions(cls):
        for permission in cls.Meta.permissions:
            p = Permission.query.filter_by(code_name=permission[0]).first()
            if not p:
                p = Permission(code_name=permission[0], name=permission[1])
                db.session.add(p)
                db.session.commit()


class Permission(db.Model, AbstractModelWithPermission):
    __tablename__ = "auth_permissions"
    id = db.Column(db.Integer, primary_key=True, index=True)
    name = db.Column(db.String(64))
    code_name = db.Column(db.String(64), index=True)

    groups = db.relationship('Group', secondary='auth_groups_permissions')

    class Meta:
        permissions = (
            ('can_get_permissions', 'Can get permissions'),
        )

    def dict(self):
        return {'name': self.name, 'code_name': self.code_name}


class Group(db.Model, AbstractModelWithPermission):
    __tablename__ = "auth_groups"
    id = db.Column(db.Integer, primary_key=True, index=True)
    name = db.Column(db.String(64))

    permissions = db.relationship('Permission', secondary='auth_groups_permissions')

    class Meta:
        permissions = (
            ('can_get_groups', 'Can get groups'),
        )

    def add_permission(self, permission):
        perm = Permission.query.filter_by(code_name=permission).first()
        self.permissions.append(perm)

    def can(self, permission):
        if permission in [perm.code_name for perm in self.permissions]:
            return True
        return False

    def dict(self):
        return {
            'id': self.id, 'name': self.name,
            'permissions': [p.dict() for p in self.permissions]
        }


class GroupPermission(db.Model):
    __tablename__ = "auth_groups_permissions"
    id = db.Column(db.Integer, primary_key=True)
    group_id = db.Column(db.Integer, db.ForeignKey('auth_groups.id'))
    permission_id = db.Column(db.Integer, db.ForeignKey('auth_permissions.id'))


user_group_table = db.Table(
    "auth_users_groups",
    db.Column("user_id", db.Integer, db.ForeignKey("auth_users.id")),
    db.Column("group_id", db.Integer, db.ForeignKey("auth_groups.id")),
)


class User(db.Model, AbstractModelWithPermission, UserMixin):
    __tablename__ = 'auth_users'
    id = db.Column(db.Integer, primary_key=True, index=True)

    first_name = db.Column(db.String(64), nullable=False, default="")
    last_name = db.Column(db.String(64), nullable=False, default="")
    username = db.Column(db.String(64), index=True, unique=True)

    _email = db.Column(db.String(128), index=True, unique=True, nullable=False)
    password_hash = db.Column(db.String(128))

    groups = db.relationship("Group", secondary=user_group_table)

    is_admin = db.Column(db.Boolean, default=False)
    is_staff = db.Column(db.Boolean, default=False)

    confirmed = db.Column(db.Boolean, default=False)
    deleted = db.Column(db.Boolean, default=False)

    tokens = db.Column(db.JSON, default=[])

    class Meta:
        permissions = (
            ('can_get_users', 'Can get users'),
        )

    @staticmethod
    def _bootstrap(count):
        from mimesis import Person
        person = Person('en')

        for _ in range(count):
            u = User(
                email=person.email(),
                confirmed=True,
                first_name=person.name(),
                last_name=person.surname(),
            )

            db.session.add(u)
            try:
                db.session.commit()
            except IntegrityError:
                db.session.rollback()

    @property
    def email(self):
        return self._email

    @email.setter
    def email(self, email):
        self._email = email.lower()

    @property
    def password(self):
        return self.password_hash

    @password.setter
    def password(self, _password):
        self.password_hash = bcrypt.hashpw(_password.encode('utf8'),
                                           bcrypt.gensalt()).decode()

    def check_password(self, _password):
        return bcrypt.checkpw(_password.encode('utf8'),
                              self.password.encode('utf8'))

    def generate_token(self, token_type):
        token = random_string(length=6)
        if not self.tokens:
            self.tokens = []
        self.tokens.append({"token_type": token_type, "expire_at": time.time() + 3600, "token": token})
        if len(self.tokens) > 6:
            self.tokens.pop(0)
        flag_modified(self, "tokens")
        db.session.add(self)
        db.session.commit()
        return token

    def confirm_token(self, token, token_type):
        for t in self.tokens:
            if t['token'] == token and t['token_type'] == token_type and t['expire_at'] > time.time():
                print(token)
                self.tokens.remove(t)
                flag_modified(self, "tokens")
                db.session.add(self)
                db.session.commit()
                return True
        return False

    def set_admin(self):
        self.is_admin = True
        db.session.commit()

    def set_staff(self):
        self.is_staff = True
        db.session.commit()

    def get_confirmed(self):
        if self.confirmed:
            return gettext("بله")
        return gettext("خیر")

    def get_first_name(self):
        if self.first_name:
            return self.first_name
        return ""

    def get_last_name(self):
        if self.last_name:
            return self.last_name
        return ""

    def generate_registration_email(self):
        token = self.generate_token(CONFIRM_EMAIL)
        return {
            "subject": gettext("Verify your email account"),
            "html": render_template(TEMPLATES['confirm_email']['html'], token=token),
            "text": render_template(TEMPLATES['confirm_email']['txt'], token=token),
            "from": current_app.config['REGISTERATION_MAIL_SENDER'],
            "to": [
                self.email,
            ]
        }

    def confirm_email_with_token(self, token):
        if self.confirm_token(token, CONFIRM_EMAIL):
            self.confirmed = True
            db.session.add(self)
            db.session.commit()
            return True
        return False

    def can(self, permission):
        if self.is_admin:
            return True
        elif self.group:
            return self.group.can(permission)
        return False

    def dict(self):
        obj = {
            'id': self.id, 'first_name': self.first_name, 'last_name': self.last_name,
            'email': self.email,  'is_confirmed': self.confirmed,
        }
        return obj

    def access_dict(self):
        obj = {}
        if self.groups:
            obj['groups'] = [g.dict() for g in self.groups]
        if self.is_admin:
            obj['is_admin'] = True
        if self.is_staff:
            obj['is_staff'] = True
        return obj

    def __repr__(self):
        return "<User email='%s' id=%d>" % (self.email, self.id)


class RevokedToken(db.Model):
    __tablename__ = 'auth_revoked_tokens'
    id = db.Column(db.Integer, primary_key=True)
    jti = db.Column(db.String(120))

    def add(self):
        db.session.add(self)
        db.session.commit()

    @classmethod
    def is_jti_blacklisted(cls, jti):
        query = cls.query.filter_by(jti=jti).first()
        return bool(query)


@jwt.user_loader_callback_loader
def identify(payload):
    return User.query.filter(User._email == payload).scalar()


@jwt.token_in_blacklist_loader
def check_if_token_in_blacklist(decrypted_token):
    jti = decrypted_token['jti']
    return RevokedToken.is_jti_blacklisted(jti)


@jwt.revoked_token_loader
def revoked_token_loader():
    return jsonify({'message': 'Token has been revoked'}), 401


@jwt.expired_token_loader
def expired_token_loader():
    return jsonify({"message": "Token has expired"}), 401


@jwt.invalid_token_loader
def invalid_token_loader(reason):
    return jsonify({"message": reason}), 422


@jwt.needs_fresh_token_loader
def needs_fresh_token_loader():
    return jsonify({"message": "Fresh token required"}), 401


@login_manager.user_loader
def load_user(user_id):
    return User.query.filter_by(id=user_id).first()

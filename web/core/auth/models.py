import json
import time
import bcrypt

from flask import current_app, jsonify

from web.ext import db, jwt

__all__ = ['User', 'Permission', 'Group', 'RevokedToken', 'setup_permissions']


def setup_permissions():
    Group.setup_permissions()
    User.setup_permissions()


class AbstractModelWithPermission():    
    @classmethod
    def setup_permissions(cls):
        for permission in cls.Meta.permissions:
            p = Permission.query.filter_by(code_name=permission[0]).first()
            if not p:
                p = Permission(code_name=permission[0], name=permission[1])
                db.session.add(p)
                db.session.commit()


class Permission(db.Model):
    __tablename__ = "auth_permissions"
    id = db.Column(db.Integer, primary_key=True, index=True)
    name = db.Column(db.String(64))
    code_name = db.Column(db.String(64), index=True)

    groups = db.relationship('Group', secondary='auth_groups_permissions')


class Group(db.Model, AbstractModelWithPermission):
    __tablename__ = "auth_groups"
    id = db.Column(db.Integer, primary_key=True, index=True)
    name = db.Column(db.String(64))

    permissions = db.relationship('Permission', secondary='auth_groups_permissions')

    class Meta:
        permissions = (
            ('can_get_groups', 'Can get groups'),
            ('can_add_groups', 'Can add groups'),
            ('can_edit_groups', 'Can edit groups'),
            ('can_delete_groups', 'Can delete groups'),
        )

    def add_permission(self, permission):
        perm = Permission.query.filter_by(code_name=permission).first()
        self.permissions.append(perm)

    def can(self, permission):
        if permission in [perm.code_name for perm in self.permissions]:
            return True
        return False


class GroupPermission(db.Model):
    __tablename__ = "auth_groups_permissions"
    id = db.Column(db.Integer, primary_key=True)
    group_id = db.Column(db.Integer, db.ForeignKey('auth_groups.id'))
    permission_id = db.Column(db.Integer, db.ForeignKey('auth_permissions.id'))


class User(db.Model, AbstractModelWithPermission):
    __tablename__ = 'auth_users'
    id = db.Column(db.Integer, primary_key=True, index=True)

    first_name = db.Column(db.String(64))
    last_name = db.Column(db.String(64))
    # username = db.Column(db.String(64), index=True, unique=True)

    email = db.Column(db.String(128), index=True, unique=True)
    password_hash = db.Column(db.String(128))

    group_id = db.Column(db.Integer, db.ForeignKey('auth_groups.id'))

    is_admin = db.Column(db.Boolean, default=False)
    is_staff = db.Column(db.Boolean, default=False)

    confirmed = db.Column(db.Boolean, default=False)
    deleted = db.Column(db.Boolean, default=False)

    group = db.relationship(Group)

    class Meta:
        permissions = (
            ('can_get_users', 'Can get users'),
            ('can_add_users', 'Can add users'),
            ('can_edit_users', 'Can edit users'),
            ('can_delete_users', 'Can delete users'),
        )

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

    def generate_token(self):
        pass

    def set_admin(self):
        self.is_admin = True
        db.session.commit()

    def set_staff(self):
        self.is_staff = True
        db.session.commit()

    def can(self, permission):
        if self.is_admin:
            return True
        elif self.group:
            return self.group.can(permission)
        return False

    def dict(self):
        obj = {
            'id':self.id, 'first_name':self.first_name, 'last_name':self.last_name,
            'email':self.email
        }
        if self.group:
            obj['group'] = self.group.name
        if self.is_admin:
            obj['is_admin'] = self.is_admin
        if self.is_staff:
            obj['is_staff'] = self.is_staff
        return obj

    def __repr__(self):
        return "<User email='%s' id=%d>" % (self.email, self.id)


class RevokedToken(db.Model):
    __tablename__ = 'auth_revoked_tokens'
    id = db.Column(db.Integer, primary_key = True)
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
    return User.query.filter(User.email==payload).scalar()

@jwt.token_in_blacklist_loader
def check_if_token_in_blacklist(decrypted_token):
    jti = decrypted_token['jti']
    return RevokedToken.is_jti_blacklisted(jti)

@jwt.revoked_token_loader
def revoked_token_loader():
    return jsonify({'message':'Token has been revoked'}), 401

from sqlalchemy import or_
from flask import render_template, redirect, url_for, jsonify, request, make_response

from flask_restful import Api, abort, reqparse
from flask_jwt_extended import (
    create_access_token, create_refresh_token,
    jwt_required, jwt_refresh_token_required,
    get_jwt_identity, get_raw_jwt, current_user,
    jwt_optional
)

from web.ext import jwt, db
from web.core.base import BaseResource

from . import mod
from .models import *


auth_api = Api(mod)

@mod.before_app_first_request
def create_permissions():
    setup_permissions()


def rest_resource(resource_cls):
    """ Decorator for adding resources to Api App """
    auth_api.add_resource(resource_cls, *resource_cls.endpoints)
    return resource_cls


@rest_resource
class RegistrationApi(BaseResource):
    endpoints = ['/register/']

    def alread_exists(self):
        return {
            'message': 'A user with this email already exists.'
        }, 409

    def post(self):
        data = request.get_json()
        if not self.check_data(data, ['password', 'email']):
            return self.bad_request()

        password = data['password']
        email = data['email']

        if User.query.filter_by(email=email).first():
            return self.alread_exists()

        u = User(password=password, email=email)
        db.session.add(u)
        db.session.commit()
        access_token = create_access_token(identity=u.email)
        refresh_token = create_refresh_token(identity=u.email)
        return {
            'message':'Successfully registered',
            'access_token': access_token,
            'refresh_token': refresh_token
        }


@rest_resource
class LoginApi(BaseResource):
    endpoints = ['/login/']
    def post(self):
        data = request.get_json()
        if not self.check_data(data, ['email', 'password']):
            return self.bad_request()

        password = data['password']
        email = data['email']

        u = User.query.filter_by(email=email).scalar()
        if u and u.check_password(password):
            access_token = create_access_token(identity=u.email)
            refresh_token = create_refresh_token(identity=u.email)
            return {
                'message':'Successfully logined',
                'access_token': access_token,
                'refresh_token': refresh_token
            }
        return {
            'message':'Username or password is not correct'
        }, 401


@rest_resource
class LogoutApi(BaseResource):
    endpoints = ['/logout/']
    method_decorators = [jwt_required]

    def post(self):
        jti = get_raw_jwt()['jti']
        revoked_token = RevokedToken(jti=jti)
        revoked_token.add()
        return {'message': 'Access token has been revoked'}


@rest_resource
class LogoutRefreshApi(BaseResource):
    endpoints = ['/logout-refresh/']
    method_decorators = [jwt_refresh_token_required]
    def post(self):
        jti = get_raw_jwt()['jti']
        revoked_token = RevokedToken(jti=jti)
        revoked_token.add()
        return {'message': 'Refresh token has been revoked'}


@rest_resource
class RefreshTokenApi(BaseResource):
    endpoints = ['/refresh-token/']
    method_decorators = [jwt_refresh_token_required]
    def post(self):
        current_user = get_jwt_identity()
        access_token = create_access_token(identity=current_user)
        return {'access_token': access_token}


@rest_resource
class ProfileApi(BaseResource):
    endpoints = ['/profile/']
    method_decorators = {
        'get':[jwt_optional]
    }

    def get(self):
        if current_user:
            return {"user":current_user.dict()}
        return {"message":"Not login", "user":None}

    def put(self):
        if current_user:
            data = request.get_json()
            fields = {
                "first_name": data.get('first_name'),
                "last_name": data.get('last_name'),                
                "email": data.get('email'),
                "password": data.get('password'),
            }
            for field in fields:
                if data[field]:
                    setattr(current_user, field, data[field])

            db.session.commit()
            return {"message":"Profile successfully updated"}, 200
        return {"message": "No profile to update"}, 204
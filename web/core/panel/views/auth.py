from flask import jsonify, request
from flask_restful import Api, abort
from flask_jwt_extended import current_user, jwt_required

from web.core.auth.models import User, Group, Permission
from web.ext import db

from .. import mod, staff_required_rest, admin_required_rest, permission_required
from ...base import BaseResource, GetBaseResource, PostBaseResource, DeleteBaseResource

panel_api = Api(mod)

panel_decorators = [staff_required_rest, jwt_required]


def rest_resource(resource_cls):
    """ Decorator for adding resources to Api App """
    panel_api.add_resource(resource_cls, *resource_cls.endpoints)
    return resource_cls

@rest_resource
class UserApi(PostBaseResource, DeleteBaseResource):
    endpoints = ['/users/', '/users/<int:obj_id>/']
    method_decorators = {
        'get': [permission_required('can_get_users')] + panel_decorators,
        'post': [admin_required_rest] + panel_decorators,
        'delete': [admin_required_rest] + panel_decorators,
        'put': [admin_required_rest] + panel_decorators,
    }

    resource_class = User
    resource_name = 'user'
    required_to_create = ('email', 'password')
    optional_fields = (
        'first_name', 'last_name', 'group_id',
        'confirmed', 'is_admin', 'is_staff'
    )

    def delete(self, obj_id=None):
        if current_user.id == obj_id:
            return {"message":"You can't delete yourself"}, 422

        return super(UserApi, self).delete(obj_id=obj_id)

    def put(self, obj_id=None):
        if not obj_id:
            return self.obj_id_required()

        u = User.query.filter_by(id=obj_id).first()
        if not u:
            return {"message": "User not found"}, 404

        data = request.get_json()
        edditable_attrs = [
            'email', 'password', 'first_name',
            'last_name', 'group_id', 'confirmed',
            'is_admin', 'is_staff'
        ]
        for attr in edditable_attrs:
            if data.get(attr):
                setattr(u, attr, data[attr])
        db.session.commit()

        return {"message":"User successfully updated", 'user':u.dict()}


@rest_resource
class PermissionApi(GetBaseResource):
    endpoints = ['/permissions/', '/permissions/<int:obj_id>/']
    method_decorators = {
        'get': [permission_required('can_get_permissions')] + panel_decorators
    }

    resource_class = Permission
    resource_name = 'permission'


@rest_resource
class GroupApi(PostBaseResource, DeleteBaseResource):
    endpoints = ['/groups/', '/groups/<int:obj_id>/']
    method_decorators = {
        'get': [permission_required('can_get_groups')] + panel_decorators,
        'post': [admin_required_rest] + panel_decorators,
        'delete': [admin_required_rest] + panel_decorators,
        'put': [admin_required_rest] + panel_decorators,
    }

    resource_class = Group
    resource_name = 'group'
    required_to_create = ('name')

    def put(self, obj_id=None):
        if not obj_id:
            return self.obj_id_required()


"""
Objects
=======

1.User
    :id:
    :first_name:
    :last_name:
    :email:

2. Permission
    :id:
    :name:
    :code_name:

3. Group
    :id:
    :name:
    
"""

from flask import request
from flask_jwt_extended import current_user, jwt_required

from web.core.rest import create_api, abort, Resource
from web.core.auth.models import User, Group, Permission
from web.ext import db

from .. import mod, staff_required_rest, admin_required_rest, permission_required
from ...base import BaseResource, GetBaseResource, PostBaseResource, DeleteBaseResource

panel_auth_api = create_api(mod)

panel_decorators = [staff_required_rest, jwt_required]


def rest_resource(resource_cls):
    """ Decorator for adding resources to Api App """
    panel_auth_api.add_resource(resource_cls, *resource_cls.endpoints)
    return resource_cls

@rest_resource
class UserApi(BaseResource):
    """
    :URL: ``/api/panel/users/`` or ``/api/panel/users/<int:obj_id>/``
    """
    endpoints = ['/users/', '/users/<int:user_id>/']
    method_decorators = {
        'get': [permission_required('can_get_users')] + panel_decorators,
        'post': [admin_required_rest] + panel_decorators,
        'delete': [admin_required_rest] + panel_decorators,
        'put': [admin_required_rest] + panel_decorators,
    }
    
    required_to_create = ('email', 'password')
    optional_fields = (
        'first_name', 'last_name', 'group_id',
        'confirmed', 'is_admin', 'is_staff'
    )

    def obj_id_required(self):
        return {"message":"user_id must be provided"}, 422

    def get(self, user_id=None):
        """
        * Authorization header with access token required
        * permssion can_get_users is required

        :optional url parameter:
            * user_id

        :optional url query string:
            * page (default: 1)
            * per_page (default: 32)

        :response:
            If user_id is provided:

            .. code-block:: python

                {"users": UserObject}

            If user_id is not provided:

            .. code-block:: python

                {"users": [List of UserObjects]}

        :errors:
            1. 404 User not found
            2. 401 Authentication errors
        """
        if user_id:
            u = User.query.filter_by(id=user_id).first()
            if not u:
                return {"message": "User not found"}, 404
            return {'user': u.dict()}

        page = request.args.get('page', type=int, default=1)
        per_page = request.args.get('per_page', type=int, default=32)
        return {
            "users": [obj.dict() for obj in 
                User.query.paginate(
                    page=page, per_page=per_page, error_out=False).items]
        }

    def delete(self, user_id=None):
        """
        * Authorization header with access token required
        * Being admin is required
        * Deleting the current user is not possible

        :required url parameter:
            * user_id

        :response:
            .. code-block:: python

                {"message":"User successfully deleted"}

        :errors:
            :status_code: 422

            .. code-block:: python

                {"message":"You can't delete yourself"}

            :status code: 404

            .. code-block:: python

                {"message":"No user deleted"}
        """
        if current_user.id == user_id:
            return {"message":"You can't delete yourself"}, 422

        if not user_id:
            abort(403)

        deleteds = User.query.filter_by(id=user_id).delete()
        db.session.commit()
        if deleteds == 1:
            return {"message":"User successfully deleted"}
        return {"message":"No user deleted"}, 404

    def patch(self, user_id=None):
        """
        * Authorization header with access token required
        * Being admin is required

        :required url parameter:
            * user_id

        :optional data (application/json):
            * email
            * password
            * first_name
            * last_name
            * group_id
            * confirmed
            * is_admin
            * is_staff

        :response:
            .. code-block:: python

                {"message":"User successfully updated"}

        :errors:
            :status code: 404
            
            .. code-block:: python

                {"message":"No user deleted"}
        """
        if not user_id:
            return self.obj_id_required()

        u = User.query.filter_by(id=user_id).first()
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
class PermissionApi(BaseResource):
    """
    :URL: ``/api/panel/permissions/``
    """
    endpoints = ['/permissions/']
    method_decorators = {
        'get': [permission_required('can_get_permissions')] + panel_decorators
    }

    def get(self):
        """
        * Authorization header with access token required
        * permssion can_get_permissions is required

        :optional url parameter:
            * perm_id

        :response:
            .. code-block:: python

                {"permissions": [List of all PermissionObjects]}

        :errors:
            2. 401 Authentication errors
        """
        return {
            'permissions': [obj.dict() for obj in 
                Permission.query.all()]
        }


@rest_resource
class GroupApi(BaseResource):
    """
    :URL: ``/api/panel/groups/`` or ``/api/panel/groups/<int:group_id>/``
    """
    endpoints = ['/groups/', '/groups/<int:group_id>/']
    method_decorators = {
        'get': [permission_required('can_get_groups')] + panel_decorators,
        'post': [admin_required_rest] + panel_decorators,
        'delete': [admin_required_rest] + panel_decorators,
        'put': [admin_required_rest] + panel_decorators,
    }

    resource_class = Group
    resource_name = 'group'
    required_to_create = ('name')

    def get(self, group_id=None):
        """
        * Authorization header with access token required
        * permssion can_get_groups is required

        :optional url parameter:
            * group_id

        :response:
            If group_id is provided:

            .. code-block:: python

                {"group": GroupObject}

            If group_id is not provided:

            .. code-block:: python

                {"groups": [List of all GroupObjects]}

        :errors:
            1. 404 Group not found
            2. 401 Authentication errors
        """
        if group_id:
            g = Group.query.filter_by(id=group_id).first()
            if not g:
                return {"message": "Group not found"}, 404
            return {'group': g.dict()}

        return {
            "groups": [obj.dict() for obj in 
                Group.query.all()]
        }

    def put(self, group_id=None):
        if not group_id:
            return self.obj_id_required()
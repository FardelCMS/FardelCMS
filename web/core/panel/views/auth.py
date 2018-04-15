from flask import jsonify, request
from flask_restful import Api, abort
from flask_jwt_extended import current_user, jwt_required

from web.core.auth import User

from .. import mod, staff_required_rest, admin_required_rest, permission_required
from ...base import BaseResource

panel_api = Api(mod)


class PanelResource(BaseResource):
    method_decorators = [staff_required_rest]


def rest_resource(resource_cls):
    """ Decorator for adding resources to Api App """
    panel_api.add_resource(resource_cls, *resource_cls.endpoints)
    return resource_cls

@rest_resource
class UserApi(PanelResource):
    endpoints = ['/users/', '/users/<int:user_id>/']
    method_decorators = {
        'get': [permission_required('can_get_users'), jwt_required],
        'post': [permission_required('can_add_users'), jwt_required],
        'delete': [permission_required('can_delete_users'), jwt_required],
        'put': [permission_required('can_update_users'), jwt_required],
    }

    def get(self, user_id=None):
        page = request.args.get('page', type=int, default=1)
        if user_id:
            return User.query.filter_by(id=user_id).first_or_404().jsonify()
        return {'users': [user.dict() for user in 
                User.query.paginate(page=page, per_page=32, error_out=False).items]}

    def delete(self, user_id):
        if current_user.id == user_id:
            abort(403)

        count = User.query.filter_by(id=user_id).delete()
        if count:
            return jsonify({'type':'ok', 'message':'User deleted.'})
        return jsonify({'type':'error', 'message':'No User found.'})

    def post(self):
        data = request.get_json()
        email = data.get('email')
        password = data.get('password')
        if not email or not password:
            return {'message':'Email and password must be provided.'}, 422

        first_name = data.get('first_name')
        last_name = data.get('last_name')
        group_id = data.get('group_id')
        confirmed = data.get('confirmed', default=False)

        is_admin = None
        is_staff = None
        if current_user.is_admin:
            is_admin = data.get('is_admin')
            is_staff = data.get('is_staff')

        u = User(
            email=email, password=password, first_name=first_name, last_name=last_name,
            group_id=group_id, confirmed=confirmed, is_admin=is_admin, is_staff=is_staff 
        )
        db.session.add(u)
        db.session.commit()
        return {'message': "User successfully added"}

    def put(self, user_id):
        pass

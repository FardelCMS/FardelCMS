from flask import jsonify, request
from flask_restful import Api, abort
from flask_login import current_user

from web.core.auth import User

from .. import mod, staff_required_rest, admin_required_rest, permission_required
from ..models import sidebar_links, add_sidebar_link, sidebar_link
from ..base import BaseResource

panel_api = Api(mod)


class PanelResource(BaseResource):
    # method_decorators = [staff_required_rest]
    pass


def rest_resource(resource_cls):
    """ Decorator for adding resources to Api App """
    panel_api.add_resource(resource_cls, *resource_cls.endpoints)
    return resource_cls


@sidebar_link('Users')
@rest_resource
class UserApi(PanelResource):
    sidebar_endpoint = '/rs-admin/api/users/'
    endpoints = ['/api/users/', '/api/users/<user_id>/']
    method_decorators = {
        'get': [permission_required('can_get_users')],
        'post': [permission_required('can_add_users')],
        'delete': [permission_required('can_delete_users')],
        'put': [permission_required('can_update_users')],
    }

    def get(self, user_id=None):
        page = request.args.get('page', type=int, default=1)
        if user_id:
            return User.query.filter_by(id=user_id).first_or_404().jsonify()
        return jsonify([user.jsonify(serialize=False) for user in
             User.query.paginate(page=page, per_page=32, error_out=False).items])

    def delete(self, user_id):
        if current_user.id == user_id:
            abort(403)

        count = User.query.filter_by(id=user_id).delete()
        if count:
            return jsonify({'type':'ok', 'message':'User deleted.'})
        return jsonify({'type':'error', 'message':'No User found.'})

    def post(self):
        pass

    def put(self, user_id):
        pass

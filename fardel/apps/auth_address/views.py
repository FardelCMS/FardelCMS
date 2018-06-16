import math

from sqlalchemy import and_, or_
from flask import request

from flask_jwt_extended import current_user, jwt_required

from fardel.core.rest import create_api, abort, Resource
from . import mod
from .models import *
from fardel.ext import db, cache


auth_address_api = create_api(mod)


def rest_resource(resource_cls):
    """ Decorator for adding resources to Api App """
    auth_address_api.add_resource(resource_cls, *resource_cls.endpoints)
    return resource_cls


@rest_resource
class UserAddressApi(Resource):
    """
    :URL: ``/api/auth/address/`` and ``/api/auth/address/<addr_id>/``
    """
    endpoints = ['/address/', '/address/<addr_id>/']

    @jwt_required
    def get(self, addr_id=None):
        ua = UserAddress.query.filter_by(id=addr_id).first_or_404()
        if ua.user_id != current_user.id:
            abort(404)
        return {"address": ua.dict()}

    @jwt_required
    def post(self, addr_id=None):
        pass

    @jwt_required
    def patch(self, addr_id=None):
        pass
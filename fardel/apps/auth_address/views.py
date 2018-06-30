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
        """ To get all addresses """
        uas = UserAddress.query.filter_by(user_id=current_user.id).all()
        return {"addresses": [ua.dict() for ua in uas]}

    @jwt_required
    def post(self, addr_id=None):
        """ To create an address """
        if addr_id:
            abort(405)

        data = request.get_json()
        if (not data.get('country') or not data.get('city') or
            not data.get("phone") or not data.get("postal_code") or
            not data.get('street_address')):
            return {"message":"Submitted form is not complete"}, 422
            
        ua = UserAddress(
            country=data.get('country'),
            city=data.get('city'),
            phone=data.get('phone'),
            postal_code=data.get('postal_code'),
            street_address=data.get('street_address'),
            user_id=current_user.id,
        )
        db.session.add(ua)
        db.session.commit()
        return {"address": ua.dict()}

    @jwt_required
    def patch(self, addr_id=None):
        """ To update an address. Is it required ? addr_id required """
        if not addr_id:
            abort(404)
        abort(404)

    @jwt_required
    def delete(self, addr_id=None):
        """ To delete an address, addr_id required """
        if not addr_id:
            abort(405)

        ua = UserAddress.query.filter_by(user_id=current_user.id,
                                         id=addr_id).first_or_404()
        db.session.delete(ua)
        db.session.commit()
        return {"message":"Successfully deleted the address."}
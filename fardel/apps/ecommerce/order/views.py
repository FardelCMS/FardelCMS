from flask import request
from flask_jwt_extended import current_user, jwt_required, jwt_optional

from fardel.core.rest import create_api, abort, Resource
from .. import mod
from .models import *


ecommerce_order_api = create_api(mod)


def rest_resource(resource_cls):
    """ Decorator for adding resources to Api App """
    ecommerce_order_api.add_resource(resource_cls, *resource_cls.endpoints)
    return resource_cls


@rest_resource
class OrderApi(Resource):
    """
    :URL: ``/api/ecommerce/order/`` or ``/api/ecommerce/order/<order_id>/``
    """	
    endpoints = ['/order/', '/order/<int:order_id>/']

    @jwt_required
    def get(self, order_id=None):
        if order_id:
            order = Order.query.filter_by(user_id=current_user.id, id=order_id).first()
            if order:
                return {"order":order.dict()}
            return {"message":"Order with this id does not exist."}, 404

        query = Order.query.filter_by(user_id=current_user.id)
        page = request.args.get("page", type=int, default=1)
        per_page = request.args.get("per_page", type=int, default=16)
        orders = query.paginate(per_page=per_page, page=page, error_out=False).items
        return {"orders": [order.dict() for order in orders]}

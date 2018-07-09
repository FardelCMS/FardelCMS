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
    :URL: ``/api/ecommerce/order/``
    """	
	endpoint = ['/orders/']

    @jwt_required
    def get(self):
    	if Order.query.current_user().first():
	        query = Order.query
	        page = request.args.get("page", type=int, default=1)
	        per_page = request.args.get("per_page", type=int, default=16)
	        orders = query.paginate(per_page=per_page, page=page, error_out=False)
	        return {"orders": [order.dict() for order in orders]}    	
	    else:
	    	return {"message":"There isn't any order to show!"}, 404

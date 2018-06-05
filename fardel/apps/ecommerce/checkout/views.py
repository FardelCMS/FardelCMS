from sqlalchemy import func
from flask import request
from flask_jwt_extended import jwt_optional

from fardel.core.rest import create_api, abort, Resource
from .models import *
from .. import mod
from fardel.ext import db, cache


ecommerce_checkout_api = create_api(mod)


def rest_resource(resource_cls):
    """ Decorator for adding resources to Api App """
    ecommerce_checkout_api.add_resource(resource_cls, *resource_cls.endpoints)
    return resource_cls


@rest_resource
class ShoppingCartApi(Resource):
    """
    :URL: ``/api/ecommerce/checkout/cart/``
    """
    endpoints = ['/checkout/cart/']
    @jwt_optional
    def get(self):
        """ Get current_user open shopping cart """
        if current_user:
            cart = Cart.query.current_user().first()
            if cart:
                return {
                    "cart": cart.dict()
                }

            return {
                "cart": {}
            }
        else:
            cart_token = request.args.get('cart_token')
            if cart_token:
                return {
                    "cart": Cart.query.filter_by(token=cart_token).open().first().dict()
                }
            return {"cart":{}}

    @jwt_optional
    def put(self):
        """ Update/Create a shopping cart """
        data = request.get_json()
        if current_user:
            cart = Cart.query.current_user().first()

            if cart:
                pass
            else:                
                cs = CartStatus.query.filter_by(name="open").first()
                cart = Cart(status_id=cs.id, user_id=current_user.id)
                db.session.add(cart)
                db.session.commit()

            return {"cart":cart.dict()}
        else:
            cart_token = request.args.get('cart_token')
            cart = Cart.query.filter_by(token=cart_token).first()

            if cart:
                pass
            else:
                cart = Cart(status_id=cs.id)
                
            return {
                'cart_token':cart.token,
                'cart': cart.dict()
            }

    @jwt_optional
    def delete(self):
        cart = None
        if current_user:
            cart = Cart.query.current_user().first()
        else:
            cart_token = request.args.get('cart_token')
            cart = Cart.query.filter_by(token=cart_token).first()

        if cart:
            db.session.delete(cart)
            db.session.commit()
        return {
            "message":"successfuly cleared the shopping cart."
        }

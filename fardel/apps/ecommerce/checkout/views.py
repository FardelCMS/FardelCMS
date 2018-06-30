import os

from sqlalchemy import func
from flask import request, current_app
from flask_jwt_extended import jwt_optional
from flask_login import login_required


from fardel.core.panel.views.media import is_safe_path
from fardel.core.panel.decorator import staff_required
from fardel.core.media.models import File
from fardel.core.rest import create_api, abort, Resource
from .models import *
from ..product.models import ProductVariant
from .. import mod
from fardel.ext import db, cache
from zeep import Client
from fardel.config import BaseConfig

ecommerce_checkout_api = create_api(mod)


def rest_resource(resource_cls):
    """ Decorator for adding resources to Api App """
    ecommerce_checkout_api.add_resource(resource_cls, *resource_cls.endpoints)
    return resource_cls


@mod.before_app_first_request
def create_defaults():
    CartStatus.generate_default()


@mod.before_app_first_request
def create_permissions():
    pass

@rest_resource
class ShoppingCartApi(Resource):
    """
    :URL: ``/api/ecommerce/checkout/cart/``
    """
    endpoints = ['/checkout/cart/']
    @jwt_optional
    def get(self):
        """ To get current_user/anonymous_user shopping cart. """
        cart_token = request.args.get('cart_token')
        if cart_token:
            cart = Cart.query.filter_by(token=cart_token).open().first()
            if cart:
                if current_user and cart.user_id == None:
                    _cart = Cart.query.current_user().first()
                    cart.user_id = current_user.id
                    if _cart:
                        db.session.delete(_cart)
                    db.session.commit()

                if current_user and cart.user_id != current_user.id:
                    return {"cart": None}
                return {"cart": cart.dict()}

        if current_user:
            cart = Cart.query.current_user().first()
            if cart:
                return {"cart": cart.dict()}        

        return {"cart": None}

    @jwt_optional
    def put(self):
        """
        To add a product(ProductVariant) into a shopping cart, if shopping cart wasn't
        available it creates a shopping cart. If the user is not logined client has to
        save the shopping cart token and use it in every ShoppingCartApi request
        as query parameter.
        """
        data = request.form
        variant_id = data.get("variant_id")
        count = data.get('count')
        file = request.files.get('file')

        if not variant_id or not count:
            return {"message": "Data input is not valid."}, 422

        variant = ProductVariant.query.filter_by(id=variant_id).first()
        if not variant:
            return {"message":"No variant with this id"}, 404

        if variant.is_file_required and not file:
            return {"message":"This product type requires file."}, 422

        cart_token = request.args.get('cart_token')
        cart = Cart.query.filter_by(token=cart_token).first()

        if cart:
            if current_user and cart.user_id == None:
                _cart = Cart.query.current_user().first()
                cart.user_id = current_user.id
                if _cart:
                    db.session.delete(_cart)
                db.session.commit()
        else:
            cs = CartStatus.query.filter_by(name="open").first()
            cart = Cart(status_id=cs.id)

            if current_user:
                cart.user_id = current_user.id

            db.session.add(cart)
            db.session.commit()

        data = {}
        if variant.is_file_required:
            path = "images/%s" % datetime.datetime.now().year

            uploads_folder = current_app.config['UPLOAD_FOLDER']
            lookup_folder = uploads_folder / path
            if is_safe_path(str(os.getcwd() / lookup_folder), str(lookup_folder)):
                file = File(path, file=file)
                file.save()
                data['file'] = file.url

        cart.add(variant, count, data)
        db.session.commit()
        return {'cart': cart.dict()}

    @jwt_optional
    def patch(self):
        """
        To update a product(ProductVariant) count in a shopping cart.
        """
        data = request.get_json()
        line_id = data.get('line_id')
        count = data.get('count')
        cart_token = request.args.get('cart_token')

        if not line_id or not isinstance(count, int):
            return {"message": "Data input is not valid."}, 422

        cl = CartLine.query.filter_by(id=line_id).first()
        if not cl or cl.cart_token != cart_token:
            return {"message":"No line with this id"}, 404

        cart = cl.cart
        cl.set_quantity(count)
        return {"cart": cl.cart.dict()}

    @jwt_optional
    def delete(self):
        """
        To clear/delete a shopping cart.
        """
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


@rest_resource
class PaymentApi(Resource):
    """
    :URL: ``/api/ecommerce/checkout/payment/<int:cart_id>/?url=<url>``
    """
    endpoints = ['/checkout/payment/<cart_id>/']

    @login_required
    def get(self, cart_id):

        """ to get payemnt of a current_user with this cart_id """

        payemnt = Payment.query.filter_by(cart_token=cart_id).open().first()
        if payment:
            if current_user and payment.user_id != current_user.id:
                return {"cart": None}
            return {"payment": payment.dict()}

        return {"payment": None}


    @login_required    
    def put(self, cart_id):

        """
        To add a shopping cart  into payment, if payment wasn't
        available it creates a payment. 
        """

        data = request.form
        description = data.get('description')
        mobile_number = data.get('mobile_number')

        cart = Cart.query.filter_by(token=cart_id).first()

        if not cart:
            return {"message":"No cart with this id"}, 404


        user = Cart.query.current_user().first()

        if current_user and cart.token == user.token: 
            payment = Payment.query.filter_by(cart_token=cart_id).first()

            if not payment:
                payment = Payment(cart_token=cart_id, user_id=current_user.id, amount=cart.total)

                db.session.add(payment)
                db.session.commit()

        data = {}

        payment.add(description, mobile_number, data)
        db.session.commit()
        # return {'payment': payment.dict()}

        client = Client(current_app.config['ZARINPAL_WEBSERVICE'])
        mail = current_user.mail


        result = client.service.PaymentRequest(current_app.config['MURCHANT_ID'],
                                               cart.amount,
                                               description,
                                               mail,
                                               mobile_number,
                                               str(url_for('verify', _external=True)))

        if result.Status == 100:
            return redirect('https://www.zarinpal.com/pg/StartPay/' + result.Authority)
        else:
            return 'Error'

    @login_required        
    def delete(self, cart_id):
        payment = Payment.query.current_user().first()
        if payment:
            db.session.delete(payment)
            db.session.commit()
        return {
            "message":"successfuly cleared the payment." }

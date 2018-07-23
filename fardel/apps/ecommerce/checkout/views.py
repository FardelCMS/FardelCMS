import os

from sqlalchemy import func
from flask import request, current_app
from flask_jwt_extended import current_user, jwt_required, jwt_optional

from fardel.core.panel.views.media import is_safe_path
from fardel.core.panel.decorator import staff_required
from fardel.core.media.models import File
from fardel.core.rest import create_api, abort, Resource
from .models import *
from ..product.models import ProductVariant
from ...auth_address.models import UserAddress
from ..order.models import *
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
    pass


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
            cart = Cart(status="open")

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
    :URL: ``/api/ecommerce/checkout/payment/`` & ``/api/ecommerce/checkout/payment/<payment_id>/``
    """
    endpoints = ['/checkout/payment/', '/checkout/payment/<int:payment_id>']

    @jwt_required
    def get(self, payment_id=None):

        """ to get payemnt of a current_user """
        if payment_id:
            payemnt = Payment.query.filter_by(id=payment_id).first()
            if payment and payment.user_id == current_user.id:
                return {"payment": payment.dict()}
            return {"message":"Payment does not exist."}, 404

        query = Payment.query
        page = request.args.get("page", type=int, default=1)
        per_page = request.args.get("per_page", type=int, default=16)
        payments = query.paginate(per_page=per_page, page=page, error_out=False).items
        return {"payments": [payment.dict() for payment in payments]}

    @jwt_required
    def post(self, payment_id=None):
        """
        To add a shopping cart  into payment, if payment wasn't
        available it creates a payment. 
        """
        data = request.get_json()
        redirect_url = data.get('redirect_url')
        cart_token = data.get('cart_token')
        address_id = data.get('address_id')
        
        cart = Cart.query.filter_by(token=cart_token, user_id=current_user.id).first()
        if not cart:
            return {"message":"No cart with this id"}, 404

        if not address_id:
            return {"message": "Please enter a address for your order"}, 404

        order = Order.create_from_cart(cart_token, address_id)
        payment = Payment.query.filter_by(order_id=order.id).first()
        if not payment:
            payment = Payment(
                user_id=current_user.id, 
                order_id=order.id, 
                amount=order.total,
                status='Pending'
                )

            db.session.add(payment)
            db.session.commit()

        client = Client(current_app.config['ZARINPAL_WEBSERVICE'])
        mail = current_user._email

        if not mail:
            return {"message": "Please enter your email address to continue the payment"}

        user_info = UserAddress.query.filter_by(id=address_id).first()
        if user_info.phone:
            mobile = user_info.phone
        else:
            mobile = ''    

        result = client.service.PaymentRequest(current_app.config['MERCHANT_ID'],
                                               payment.amount,
                                               'nani',
                                               mail,
                                               mobile,
                                               redirect_url)

        payment.authority = result.Authority
        db.session.commit()
        if result.Status == 100:
            return {'payment_url':'https://www.zarinpal.com/pg/StartPay/' + result.Authority}
        else:
            return {
                'message':"We can't connect you to zarin pal server, right now. Please try again in a few moments."
            }, 404

@rest_resource
class PaymentVerification(Resource):
    endpoints = ['/checkout/payment/verification/<authority>/<status>/']
    def get(self, authority, status):
        payment = Payment.query.filter_by(authority=authority).first_or_404()
        if payment.status != 'Succeeded' or True:
            client = Client(current_app.config['ZARINPAL_WEBSERVICE'])
            if status == 'OK':
                result = client.service.PaymentVerification(current_app.config['MERCHANT_ID'],
                                                            authority,
                                                            payment.amount)
                
                if result.Status == 100 or result.Status == 101:
                    payment.status = "Succeeded"
                    payment.ref_id = result.RefID
                    if payment.amount == payment.order.total and payment.order.status != "Fulfiled":
                        payment.order.set_fulfiled()
                else:
                    payment.status = "Failed"
                db.session.commit() 
        return {'payment': payment.dict()} 

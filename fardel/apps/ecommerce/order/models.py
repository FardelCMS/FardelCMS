import datetime

from fardel.apps.ecommerce.checkout.models import Cart, CartLine

from sqlalchemy import func
from sqlalchemy.dialects.postgresql import JSONB, UUID

from flask_sqlalchemy import BaseQuery
from flask_jwt_extended import current_user

from fardel.ext import db


class Order(db.Model):
    __tablename__ = "orders"
    """
    Status Types:
        :Fulfiled:
        :Unfulfiled:
        :Canceled:
    """
    id = db.Column(db.Integer, primary_key=True, index=True)
    status = db.Column(db.String(64), default="Unfulfiled")
    user_id = db.Column(db.Integer, db.ForeignKey('auth_users.id'))
    address_id = db.Column(db.Integer, db.ForeignKey('auth_users_address.id'))
    create_time = db.Column(db.TIMESTAMP, default=func.current_timestamp())
    total = db.Column(db.Integer, default=0)
    quantity = db.Column(db.Integer, default=0)
    data = db.Column(JSONB())


    user = db.relationship("User")
    address = db.relationship("UserAddress")
    lines = db.relationship("OrderLine")

    @staticmethod
    def create_from_cart(cart_id, address_id):
        cart = Cart.query.filter_by(token=cart_id).first()
        if current_user.id == cart.user_id:
            order = Order(
                user_id=cart.user_id, 
                total=cart.total, 
                quantity=cart.quantity,
                address_id=address_id, 
                data=cart.checkout_data
                )

            db.session.add(order)
            db.session.commit()
            
            for line in cart.lines:
                order_line = OrderLine(
                    order_id=order.id, 
                    variant_id=line.variant_id,
                    quantity=line.quantity, 
                    total=line.get_total(),
                    data=line.data
                    )
                db.session.add(order_line)

            cart.clear()    
            db.session.flush()
            return order
        else:
            return None

    @property
    def is_shipping_required(self):
        """Return `True` if any of the lines requires shipping."""
        if not hasattr(self, '_is_shipping_required'):
            self._is_shipping_required = False
            for line in self.lines:
                if line.variant.is_shipping_required:
                    self._is_shipping_required = True
                    break
        return self._is_shipping_required

    def delete_line(self, variant_id, data):
        """ Delete a line with specified variant_id+data """
        line = self.get_line(variant_id, data)
        line.delete()

    def dict(self):
        """ Serialize object to json """
        return {
            'id': self.id,
            'status': self.status,
            'user' : self.user.dict(),
            'address': self.address.dict(),
            'create_time': self.create_time,
            'total': self.total,
            'quantity': self.quantity,
            'lines': [line.dict() for line in self.lines],
            'is_shipping_required': self.is_shipping_required,
        }


class OrderLine(db.Model):
    __tablename__= "order_lines"
    id = db.Column(db.Integer, primary_key=True, index=True)
    order_id = db.Column(db.ForeignKey('orders.id'))    
    variant_id = db.Column(db.Integer,
        db.ForeignKey('product_product_variants.id', ondelete="CASCADE"))
    total = db.Column(db.Integer)
    quantity = db.Column(db.Integer)
    data = db.Column(JSONB(), default={})

    variant = db.relationship("ProductVariant")
    order = db.relationship("Order")    

    def dict(self):
        return {
            'id': self.id,
            'variant':self.variant.dict(cart=True),
            'quantity':self.quantity,
            'data':self.data,
            'total': self.total,
            'quantity': self.quantity,
            'is_shipping_required': self.is_shipping_required
        }

    @property
    def is_shipping_required(self):
        return self.variant.is_shipping_required
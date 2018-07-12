import datetime

from fardel.apps.ecommerce.checkout.models import Cart

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

    user = db.relationship("User")
    address = db.relationship("UserAddress")
    lines = db.relationship("OrderLine")

    @staticmethod
    def creat_from_cart(cart_id, address_id):
        cart = Cart.query.filter_by(token=cart_id).first()
        if current_user.id == cart.user_id:
            order = Order(
                user_id=cart.user_id, 
                total=cart.total, 
                quantity=cart.quantity,
                address_id=address_id, 
                data=cart.data
                )
            db.session.add(order)
            db.session.commit(order)
        else:
            return {"message": "this Cart does not exist"}, 404

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

    def create_line(self, variant, quantity, data):
        """
        To Create a line if the variant_id with the data doesn't exists
        """
        cl = OrderLine(
            order_id=self.id,
            variant_id=variant.id,
            quantity=quantity,
            data=data
        )
        db.session.add(cl)
        db.session.flush()

    def get_line(self, variant, data):
        """ Get a line with same variant_id and data """
        return OrderLine.query.filter_by(order_id=self.id,
            data=data, variant_id=variant.id).first()

    def add(self, variant, quantity, data):
        """
        Create a line with the quantity and data or if variant+data already exists
        it adds the quantity to exists one.
        """
        line = self.get_line(variant, data)
        if not line:
            self.create_line(variant, quantity, data)
        else:
            line.quantity += quantity
            db.session.flush()

    def set_line(self, variant_id, quantity, data):
        """ Set exists line to the specified quantity
            if quantity is ZERO it will be removed.
        """
        line = self.get_line(variant, data)
        if quantity == 0:
            line.delete()
        else:
            line.quantity = quantity
            db.session.flush()

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


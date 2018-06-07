import datetime

import uuid

from sqlalchemy import func
from sqlalchemy.dialects.postgresql import JSONB, UUID

from flask_sqlalchemy import BaseQuery
from flask_jwt_extended import current_user

from fardel.ext import db


class CartQueryset(BaseQuery):
    def open(self):
        return self.outerjoin(CartStatus).filter(CartStatus.name=="open")

    def canceled(self):
        return self.outerjoin(CartStatus).filter(CartStatus.name=="canceled")

    def current_user(self):
        return self.filter_by(user_id=current_user.id).open()


class CartStatus(db.Model):
    __tablename__ = "checkout_carts_statuses"
    id = db.Column(db.Integer, primary_key=True, index=True)
    name = db.Column(db.String(32))

    @staticmethod
    def generate_default():
        statuses = [
            {'name':'open'},
            {'name':'canceled'},
        ]
        for status in statuses:
            s = CartStatus.query.filter_by(name=status['name']).first()
            if not s:
                s = CartStatus(name=status['name'])
                db.session.add(s)
                db.session.commit()


def generate_unique_id():
    _uuid = uuid.uuid4()
    return str(uuid.UUID(str(_uuid)))


class Cart(db.Model):
    query_class = CartQueryset
    __tablename__ = "checkout_carts"    
    token = db.Column(UUID(), primary_key=True, default=generate_unique_id)

    status_id = db.Column(db.Integer, db.ForeignKey("checkout_carts_statuses.id",
        ondelete="SET NULL"))
    create_time = db.Column(db.TIMESTAMP, default=func.current_timestamp())
    last_status_change = db.Column(db.TIMESTAMP,
        default=func.current_timestamp(), onupdate=func.current_timestamp())
    user_id = db.Column(db.Integer, db.ForeignKey('auth_users.id'))
    # voucher = db.Column(db.Integer, db.ForeignKey('discount.Voucher'))
    checkout_data = db.Column(JSONB(), default={})

    total = db.Column(db.String(12), default=0)
    quantity = db.Column(db.Integer, default=0)

    status = db.relationship("CartStatus")
    lines = db.relationship("CartLine")
    user = db.relationship("User")

    @staticmethod
    def cron_delete():
        """ DELETE old and canceled carts """
        deleted = Cart.query.filter(CartStatus.name=="canceled"
            ).join(CartStatus).delete()
        db.session.flush()

    def update_quantity_total(self):
        """Recalculate cart quantity based on lines."""
        self.quantity = 0
        for line in lines:
            self.quantity += line.quantity
            self.total += line.get_total()
        self.quantity = self._count
        db.session.commit()

    def change_status(self, status):
        """Change cart status."""
        self.status_id = CartStatus.query.filter_by(name=status).first().id
        db.session.flush()

    def change_user(self, user):
        """Assign cart to a user.

        If the user already has an open cart assigned, cancel it.
        """
        if not self.user:
            self.user_id = user.id
            db.session.flush()

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

    def clear(self):
        """Remove the cart."""
        db.session.delete(self)
        db.session.flush()

    def create_line(self, variant, quantity, data):
        """
        To Create a line if the variant_id with the data doesn't exists
        """
        cl = CartLine(
            cart_token=self.token,
            variant_id=variant.id,
            quantity=quantity,
            data=data
        )
        db.session.add(cl)
        db.session.flush()

    def get_line(self, variant, data):
        """ Get a line with same variant_id and data """
        return CartLine.query.filter_by(cart_token=self.token,
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
        line = self.get_line(variant_id, data)
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
            'token': self.token,
            'total': self.total,
            'quantity': self.quantity,
            'lines': [line.dict() for line in self.lines],
            'is_shipping_required': self.is_shipping_required,
        }


class CartLine(db.Model):
    __tablename__ = "checkout_carts_lines"
    id = db.Column(db.Integer, primary_key=True, index=True)

    cart_token = db.Column(UUID(),
        db.ForeignKey('checkout_carts.token', ondelete="CASCADE"))
    variant_id = db.Column(db.Integer,
        db.ForeignKey('product_product_variants.id', ondelete="CASCADE"))
    quantity = db.Column(db.Integer)
    data = db.Column(JSONB(), default={})

    variant = db.relationship("ProductVariant")

    def get_total(self):
        """Return the total price of this line."""
        if not hasattr(self, "total"):
            self.total = self.variant.get_price() * self.quantity
        return self.total

    def get_price_per_item(self):
        """Return the unit price of the line."""
        return self.variant.get_price()

    @property
    def is_shipping_required(self):
        return self.variant.is_shipping_required

    def delete(self):
        db.session.delete(self)
        db.session.flush()

    def dict(self):
        return {
            'variant':self.variant.dict(cart=True),
            'quantity':self.quantity,
            'data':self.data,
            'total': self.get_total(),
            'item_price': self.get_price_per_item(),
            'is_shipping_required': self.is_shipping_required
        }
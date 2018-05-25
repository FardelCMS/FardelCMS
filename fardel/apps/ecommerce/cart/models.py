import datetime

from uuid import uuid4

from sqlalchemy import func
from sqlalchemy.dialects.postgresql import JSONB, UUID

from flask_sqlalchemy import BaseQuery
from flask_jwt_extended import current_user

from fardel.ext import db


class CartQueryset(BaseQuery):
    def open(self):
        return self.outerjoin(Cart.status).filter(Cart.status.name=="open")

    def canceled(self):
        return self.outerjoin(Cart.status).filter(Cart.status.name=="canceled")

    def current_user(self):
        return self.filter_by(user_id=current_user.id)


class CartStatus(db.Model):
    __tablename__ = "cart_carts_statuses"
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


class Cart(db.Model):
    query_class = CartQueryset
    __tablename__ = "cart_carts"    
    token = db.Column(UUID(), primary_key=True, default=uuid4)

    status = db.Column(db.Integer, db.ForeignKey("cart_carts_statuses.id"))
    create_time = db.Column(db.TIMESTAMP, default=func.current_timestamp())
    last_status_change = db.Column(db.TIMESTAMP,
        default=func.current_timestamp(), onupdate=func.current_timestamp())
    user_id = db.Column(db.Integer, db.ForeignKey('auth_users.id'))
    # voucher = db.Column(db.Integer, db.ForeignKey('discount.Voucher'))
    checkout_data = db.Column(JSONB(), default={})

    total = db.Column(db.String(12), default=0)
    quantity = db.Column(db.Integer, default=0)

    lines = db.relationship("CartLine")
    user = db.relationship("User")

    @staticmethod
    def cron_delete():
        """ DELETE old and canceled carts """
        pass

    def update_quantity(self):
        """Recalculate cart quantity based on lines."""
        pass

    def change_status(self, status):
        """Change cart status."""
        pass

    def change_user(self, user):
        """Assign cart to a user.

        If the user already has an open cart assigned, cancel it.
        """
        pass

    def is_shipping_required(self):
        """Return `True` if any of the lines requires shipping."""
        pass

    def get_total(self, discounts=None):
        """Return the total cost of the cart prior to shipping."""
        pass

    def count(self):
        """Return the total quantity in cart."""
        pass

    def clear(self):
        """Remove the cart."""
        pass

    def create_line(self, variant, quantity, data):
        pass

    def get_line(self, variant, data=None):
        pass

    def add(self, variant, quantity=1, replace=False, check_quantity=True):
        pass


class CartLine(db.Model):
    __tablename__ = "cart_carts_lines"
    id = db.Column(db.Integer, primary_key=True, index=True)

    cart_token = db.Column(UUID(),
        db.ForeignKey('cart_carts.token', ondelete="CASCADE"))
    variant = db.Column(db.Integer,
        db.ForeignKey('product_product_variants.id', ondelete="CASCADE"))
    quantity = db.Column(db.Integer)
    data = db.Column(JSONB(), default={})

    def __eq__(self, other):
        if not isinstance(other, CartLine):
            return NotImplemented

        return (
            self.variant == other.variant and
            self.quantity == other.quantity,
            self.data == other.data)

    def __ne__(self, other):
        return not self == other

    def get_total(self, discounts=None):
        """Return the total price of this line."""
        pass

    def get_price_per_item(self, discounts=None):
        """Return the unit price of the line."""
        pass

    def is_shipping_required(self):
        return self.variant.is_shipping_required()
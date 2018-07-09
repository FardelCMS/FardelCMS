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
        ::
        ::
        ::
        ::
    """
    id = db.Column(db.Integer, primary_key=True, index=True)
    status = db.Column(db.String(32))    
    user_id = db.Column(db.Integer, db.ForeignKey('auth_users.id'))
    address_id = db.Column(db.Integer, db.ForeignKey('auth_users_address'))
    create_time = db.Column(db.TIMESTAMP, default=func.current_timestamp())
    amount = db.Column(db.Integer, default=0)
    cart_token = db.Column(UUID(),
        db.ForeignKey('checkout_carts.token', ondelete="CASCADE"))

    user = db.relationship("User")
    cart = db.relationship("Cart")
    address = db.relationship("UserAddress")

    @staticmethod
    def creat_from_cart(cart_id):
        cart = Cart.query.filter_by(token=cart_id).first()
        if current_user.id == cart.user_id:
            order = Order(user_id=cart.user_id, amount=cart.total, cart_token=cart_id)
            db.session.add(order)
            db.session.commit(order)
        else:
            return {
                "message": "this Cart does not exist"
            }, 404

    def dict(self):
        return {
            'id': self.id,
            'status': self.status
            'user' : self.user.dict(),
            'address': self.address.dict(),
            'create_time': self.create_time,
            'amount': self.amount,
            'cart': self.cart.dict(),

        }

# class Order(db.Model):
#     created = models.DateTimeField(
#         default=now, editable=False)
#     status = models.CharField(
#         max_length=32, default=OrderStatus.UNFULFILLED,
#         choices=OrderStatus.CHOICES)
#     user = models.ForeignKey(
#         settings.AUTH_USER_MODEL, blank=True, null=True, related_name='orders',
#         on_delete=models.SET_NULL)
#     language_code = models.CharField(
#         max_length=35, default=settings.LANGUAGE_CODE)
#     tracking_client_id = models.CharField(
#         max_length=36, blank=True, editable=False)
#     billing_address = models.ForeignKey(
#         Address, related_name='+', editable=False, null=True,
#         on_delete=models.SET_NULL)
#     shipping_address = models.ForeignKey(
#         Address, related_name='+', editable=False, null=True,
#         on_delete=models.SET_NULL)
#     user_email = models.EmailField(blank=True, default='')
#     shipping_method = models.ForeignKey(
#         ShippingMethodCountry, blank=True, null=True, related_name='orders',
#         on_delete=models.SET_NULL)
#     shipping_price_net = MoneyField(
#         currency=settings.DEFAULT_CURRENCY, max_digits=12,
#         decimal_places=settings.DEFAULT_DECIMAL_PLACES,
#         default=0, editable=False)
#     shipping_price_gross = MoneyField(
#         currency=settings.DEFAULT_CURRENCY, max_digits=12,
#         decimal_places=settings.DEFAULT_DECIMAL_PLACES,
#         default=0, editable=False)
#     shipping_price = TaxedMoneyField(
#         net_field='shipping_price_net', gross_field='shipping_price_gross')
#     shipping_method_name = models.CharField(
#         max_length=255, null=True, default=None, blank=True, editable=False)
#     token = models.CharField(max_length=36, unique=True)
#     total_net = MoneyField(
#         currency=settings.DEFAULT_CURRENCY, max_digits=12,
#         decimal_places=settings.DEFAULT_DECIMAL_PLACES, default=0)
#     total_gross = MoneyField(
#         currency=settings.DEFAULT_CURRENCY, max_digits=12,
#         decimal_places=settings.DEFAULT_DECIMAL_PLACES, default=0)
#     total = TaxedMoneyField(net_field='total_net', gross_field='total_gross')
#     voucher = models.ForeignKey(
#         Voucher, null=True, related_name='+', on_delete=models.SET_NULL)
#     discount_amount = MoneyField(
#         currency=settings.DEFAULT_CURRENCY, max_digits=12,
#         decimal_places=settings.DEFAULT_DECIMAL_PLACES, default=0)
#     discount_name = models.CharField(max_length=255, default='', blank=True)

#     objects = OrderQueryset.as_manager()

#     class Meta:
#         ordering = ('-pk',)
#         permissions = (
#             ('view_order',
#              pgettext_lazy('Permission description', 'Can view orders')),
#             ('edit_order',
#              pgettext_lazy('Permission description', 'Can edit orders')))

#     def save(self, *args, **kwargs):
#         if not self.token:
#             self.token = str(uuid4())
#         return super().save(*args, **kwargs)

#     def is_fully_paid(self):
#         total_paid = sum(
#             [
#                 payment.get_total_price() for payment in
#                 self.payments.filter(status=PaymentStatus.CONFIRMED)],
#             TaxedMoney(
#                 net=Money(0, settings.DEFAULT_CURRENCY),
#                 gross=Money(0, settings.DEFAULT_CURRENCY)))
#         return total_paid.gross >= self.total.gross

#     def get_user_current_email(self):
#         return self.user.email if self.user else self.user_email

#     def _index_billing_phone(self):
#         return self.billing_address.phone

#     def _index_shipping_phone(self):
#         return self.shipping_address.phone

#     def __iter__(self):
#         return iter(self.lines.all())

#     def __repr__(self):
#         return '<Order #%r>' % (self.id,)

#     def __str__(self):
#         return '#%d' % (self.id,)

#     def get_absolute_url(self):
#         return reverse('order:details', kwargs={'token': self.token})

#     def get_last_payment_status(self):
#         last_payment = max(
#             self.payments.all(), default=None, key=attrgetter('pk'))
#         if last_payment:
#             return last_payment.status
#         return None

#     def get_last_payment_status_display(self):
#         last_payment = max(
#             self.payments.all(), default=None, key=attrgetter('pk'))
#         if last_payment:
#             return last_payment.get_status_display()
#         return None

#     def is_pre_authorized(self):
#         return self.payments.filter(status=PaymentStatus.PREAUTH).exists()

#     @property
#     def quantity_fulfilled(self):
#         return sum([line.quantity_fulfilled for line in self])

#     def is_shipping_required(self):
#         return any(line.is_shipping_required for line in self)

#     def get_subtotal(self):
#         subtotal_iterator = (line.get_total() for line in self)
#         return sum(subtotal_iterator, ZERO_TAXED_MONEY)

#     def get_total_quantity(self):
#         return sum([line.quantity for line in self])

#     def is_draft(self):
#         return self.status == OrderStatus.DRAFT

#     def is_open(self):
#         statuses = {OrderStatus.UNFULFILLED, OrderStatus.PARTIALLY_FULFILLED}
#         return self.status in statuses

#     def can_cancel(self):
#         return self.status not in {OrderStatus.CANCELED, OrderStatus.DRAFT}


# class OrderLine(db.Model):
#     order = models.ForeignKey(
#         Order, related_name='lines', editable=False, on_delete=models.CASCADE)
#     variant = models.ForeignKey(
#         ProductVariant, related_name='+', on_delete=models.SET_NULL,
#         blank=True, null=True)
#     product_name = models.CharField(max_length=128)
#     product_sku = models.CharField(max_length=32)
#     is_shipping_required = models.BooleanField()
#     quantity = models.IntegerField(
#         validators=[MinValueValidator(0), MaxValueValidator(999)])
#     quantity_fulfilled = models.IntegerField(
#         validators=[MinValueValidator(0), MaxValueValidator(999)], default=0)
#     unit_price_net = MoneyField(
#         currency=settings.DEFAULT_CURRENCY, max_digits=12,
#         decimal_places=settings.DEFAULT_DECIMAL_PLACES)
#     unit_price_gross = MoneyField(
#         currency=settings.DEFAULT_CURRENCY, max_digits=12,
#         decimal_places=settings.DEFAULT_DECIMAL_PLACES)
#     unit_price = TaxedMoneyField(
#         net_field='unit_price_net', gross_field='unit_price_gross')

#     def __str__(self):
#         return self.product_name

#     def get_total(self):
#         return self.unit_price * self.quantity

#     @property
#     def quantity_unfulfilled(self):
#         return self.quantity - self.quantity_fulfilled
from fardel.ext import db



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
    __tablename__ = "cart_carts"
    id = db.Column(db.Integer, primary_key=True, index=True)
    
    status = db.Column(db.Integer, db.ForeignKey("cart_carts_statuses.id"))
    create_time = db.Column(db.TIMESTAMP, default=func.current_timestamp())
    last_status_change = db.Column(db.TIMESTAMP, default=func.current_timestamp())
    user = db.Column(db.Integer, db.ForeignKey('auth_users.id'))
    # token = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    # voucher = db.Column(db.Integer, db.ForeignKey('discount.Voucher'))
    checkout_data = db.Column(db.JSONB(), default={})

    total = db.Column(db.String(12), default=0)
    quantity = db.Column(db.Integer, default=0)

    lines = db.relationship("CartLine")

    # def __init__(self, *args, **kwargs):
    #     self.discounts = kwargs.pop('discounts', None)
    #     super().__init__(*args, **kwargs)

    def update_quantity(self):
        """Recalculate cart quantity based on lines."""
        total_lines = self.count()['total_quantity']
        if not total_lines:
            total_lines = 0
        self.quantity = total_lines
        self.save(update_fields=['quantity'])

    def change_status(self, status):
        """Change cart status."""
        # FIXME: investigate replacing with django-fsm transitions
        if status not in dict(CartStatus.CHOICES):
            raise ValueError('Not expected status')
        if status != self.status:
            self.status = status
            self.last_status_change = now()
            self.save()

    def change_user(self, user):
        """Assign cart to a user.

        If the user already has an open cart assigned, cancel it.
        """
        open_cart = find_open_cart_for_user(user)
        if open_cart is not None:
            open_cart.change_status(status=CartStatus.CANCELED)
        self.user = user
        self.save(update_fields=['user'])

    def is_shipping_required(self):
        """Return `True` if any of the lines requires shipping."""
        return any(line.is_shipping_required() for line in self.lines.all())

    def __repr__(self):
        return 'Cart(quantity=%s)' % (self.quantity,)

    def __len__(self):
        return self.lines.count()

    def get_total(self, discounts=None):
        """Return the total cost of the cart prior to shipping."""
        if not discounts:
            discounts = self.discounts
        subtotals = [line.get_total(discounts) for line in self.lines.all()]
        if not subtotals:
            raise AttributeError('Calling get_total() on an empty cart')
        return sum_prices(subtotals)

    def count(self):
        """Return the total quantity in cart."""
        lines = self.lines.all()
        return lines.aggregate(total_quantity=models.Sum('quantity'))

    def clear(self):
        """Remove the cart."""
        self.delete()

    def create_line(self, variant, quantity, data):
        """Create a cart line for given variant, quantity and optional data.

        The `data` parameter may be used to differentiate between items with
        different customization options.
        """
        return self.lines.create(
            variant=variant, quantity=quantity, data=data or {})

    def get_line(self, variant, data=None):
        """Return a line matching the given variant and data if any."""
        all_lines = self.lines
        if data is None:
            data = {}
        line = [
            line for line in all_lines
            if line.variant_id == variant.id and line.data == data]
        if line:
            return line[0]
        return None

    def add(self, variant, quantity=1, replace=False, check_quantity=True):
        """Add a product vartiant to cart.

        The `data` parameter may be used to differentiate between items with
        different customization options.

        If `replace` is truthy then any previous quantity is discarded instead
        of added to.
        """
        cart_line, dummy_created = self.lines.get_or_create(
            variant=variant, defaults={'quantity': 0, 'data': data or {}})

        if replace:
            new_quantity = quantity
        else:
            new_quantity = cart_line.quantity + quantity

        if new_quantity < 0:
            raise ValueError('%r is not a valid quantity (results in %r)' % (
                quantity, new_quantity))

        variant.check_quantity(new_quantity)
        cart_line.quantity = new_quantity

        if not cart_line.quantity:
            cart_line.delete()
        else:
            cart_line.save(update_fields=['quantity'])
        self.update_quantity()


class CartLine(db.Model):
    __tablename__ = "cart_carts_lines"
    id = db.Column(db.Integer, primary_key=True, index=True)

    cart = db.Column(db.Integer, db.ForeignKey('cart_carts.id')) # delete cascade
    variant = db.Column(db.Integer, db.ForeignKey('product_product_variants.id')) # delete cascade
    quantity = db.Column(db.Integer)
    # data = db.Column(db.JSONB(), default={})

    def __eq__(self, other):
        if not isinstance(other, CartLine):
            return NotImplemented

        return (
            self.variant == other.variant and
            self.quantity == other.quantity)
            # self.data == other.data)

    def __ne__(self, other):
        return not self == other

    def get_total(self, discounts=None):
        """Return the total price of this line."""
        return self.get_price_per_item(discounts) * self.quantity

    def get_price_per_item(self, discounts=None):
        """Return the unit price of the line."""
        pass

    def is_shipping_required(self):
        return self.variant.is_shipping_required()
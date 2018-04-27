import time

from sqlalchemy.dialects.postgresql import JSONB

from web.core.seo import SeoModel
from web.ext import db


class ProductCategory(db.Model, SeoModel):
    __tablename__ = "product_categories"
    id = db.Column(db.Integer, primary_key=True)

    name = db.Column(db.String(32), nullable=False)
    description = db.Column(db.Text)
    hidden = db.Column(db.Boolean, default=False)

    parent_id = db.Column(db.Integer, db.ForeignKey('product_categories.id'))
    parent = db.relationship('ProductCategory', remote_side=[id])
    children = db.relationship('ProductCategory')

    def dict(self):
        return {
        
        }.update(self.seo_dict())


class ProductCategories(db.Model):
    __tablename__ = "product_products_categories"
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('product_products.id'))
    category_id = db.Column(db.Integer, db.ForeignKey('product_categories.id'))


class ProductType(db.Model):
    __tablename__ = "product_product_types"
    id = db.Column(db.Integer, primary_key=True)

    name = db.Column(db.String(128), nullable=False)
    has_variants = db.Column(db.Boolean, default=True)
    product_attributes = db.relationship('ProductAttribute',
        secondary="product_product_types_attributes")
    variant_attributes = db.relationship('ProductVariant',
        secondary="product_product_types_variants")
    is_shipping_required = db.Column(db.Boolean, default=False)


class ProductTypeAttributes(db.Model):
    __tablename__ = "product_product_types_attributes"
    id = db.Column(db.Integer, primary_key=True)

    product_type_id = db.Column(db.Integer,
        db.ForeignKey('product_product_types.id'))
    product_attributes_id = db.Column(db.Integer,
        db.ForeignKey('product_products_attributes.id'))


class ProductTypeVariants(db.Model):
    __tablename__ = "product_product_types_variants"
    id = db.Column(db.Integer, primary_key=True)

    product_type_id = db.Column(db.Integer,
        db.ForeignKey('product_product_types.id'))
    product_variants_id = db.Column(db.Integer,
        db.ForeignKey('product_product_variants.id'))


class Product(db.Model, SeoModel):
    __tablename__ = "product_products"
    id = db.Column(db.Integer, primary_key=True)

    name = db.Column(db.String(32), nullable=False)
    description = db.Column(db.Text)

    price = db.Column(db.Integer, nullable=False)
    weight = db.Column(db.Integer, default=0)

    updated_at = db.Column(db.Integer, default=time.time, onupdate=time.time)

    attributes = db.Column(JSONB(), default={})

    is_published = db.Column(db.Boolean, default=True)
    is_featured = db.Column(db.Boolean, default=False)

    category_id = db.Column(db.Integer, db.ForeignKey('product_categories.id'))
    product_type_id = db.Column(db.Integer, db.ForeignKey('product_product_types.id'))

    product_type = db.relationship('ProductType')

    def dict(self):
        return {
        
        }.update(self.seo_dict())


class ProductVariant(db.Model):
    __tablename__ = "product_product_variants"
    id = db.Column(db.Integer, primary_key=True)

    sku = db.Column(db.String(32), unique=True, nullable=True)
    name = db.Column(db.String(255), default="")
    price_override = db.Column(db.Integer, nullable=True)

    product_id = db.Column(db.Integer, db.ForeignKey('product_products.id'))
    attributes = db.Column(JSONB(), default={})
    images = db.Column(JSONB())
    quantity = db.Column(db.Integer, default=1)
    quantity_allocated = db.Column(db.Integer, default=0)

    product = db.relationship("Product")

    @property
    def quantity_available(self):
        return max(self.quantity - self.quantity_allocated, 0)

    def check_quantity(self, quantity):
        if quantity > self.quantity_available:
            return False
        return True

    def get_price_per_item(self, discounts=None):
        price = self.price_override or self.product.price
        price = calculate_discounted_price(self.product, price, discounts)
        return price

    @property
    def is_shipping_required(self):
        return self.product.product_type.is_shipping_required

    @property
    def first_image(self):
        return self.product.images[0]

    def dict(self):
        return {

        }


class ProductAttribute(db.Model):
    __tablename__ = "product_products_attributes"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128))

    choices = db.relationship('AttributeChoiceValue', lazy="joined")

    def __str__(self):
        return self.name    


class AttributeChoiceValue(db.Model):
    __tablename__ = "product_products_attributechoicevalue"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    attribute_id = db.Column(db.Integer, db.ForeignKey("product_products_attributes.id"))

    attribute = db.relationship('ProductAttribute')

    def __str__(self):
        return self.name


class Collection(db.Model, SeoModel):
    __tablename__ = "product_collections"
    id = db.Column(db.Integer, primary_key=True)

    name = db.Column(db.String(100), unique=True)
    is_published = db.Column(db.Boolean, default=False)

    products = db.relationship('Product',
        secondary='product_products_collections', lazy='select')

    def dict(self):
        return {
        
        }.update(self.seo_dict())

    def __str__(self):
        return self.name

class ProductCollection(db.Model):
    __tablename__ = "product_products_collections"
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('product_products.id'))
    collection_id = db.Column(db.Integer, db.ForeignKey('product_collections.id'))
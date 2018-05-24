import math
import time

from sqlalchemy.dialects.postgresql import JSONB

from fardel.core.seo import SeoModel
from fardel.ext import db

__all__ = (
    "ProductCategory", "Collection", "ProductType",
    "Product", "ProductVariant", "ProductAttribute",
    "AttributeChoiceValue",
)


class ProductCategory(db.Model, SeoModel):
    __tablename__ = "product_categories"
    id = db.Column(db.Integer, primary_key=True)

    name = db.Column(db.String(32), nullable=False)
    description = db.Column(db.Text)
    hidden = db.Column(db.Boolean, default=False)

    parent_id = db.Column(db.Integer, db.ForeignKey('product_categories.id'))
    parent = db.relationship('ProductCategory', remote_side=[id])
    children = db.relationship('ProductCategory')

    def get_name(self):
        if self.parent:
            return "%s > %s" % (self.parent.get_name(), self.name)
        return self.name

    def recersive_subcategories_id(self):
        subc = []
        for child in self.children:
            subc = subc + child.recersive_subcategories_id()
        subc.append(self.id)
        return subc

    def dict(self, products=False, page=None, per_page=None):
        obj = dict(
            id=self.id,
            name=self.name,
            subcategories=[cat.dict() for cat in self.children]
        )
        if products:
            subcategories = self.recersive_subcategories_id()
            print(subcategories)
            query = Product.query.filter(
                Product.category_id.in_(subcategories), Product.is_published==True
            ).outerjoin(ProductVariant).filter(ProductVariant.quantity>0)
            pages = math.ceil(query.count() / per_page)
            products = query.paginate(page=page, per_page=per_page, error_out=False).items
            obj.update(pages=pages, products=[p.dict() for p in products])
            obj.update(self.seo_dict())
        return obj
        

class ProductType(db.Model):
    __tablename__ = "product_product_types"
    id = db.Column(db.Integer, primary_key=True)

    name = db.Column(db.String(128), nullable=False)
    has_variants = db.Column(db.Boolean, default=True)
    product_attributes = db.relationship('ProductAttribute',
        secondary="product_product_types_attributes")
    variant_attributes = db.relationship('ProductAttribute',
        secondary="product_product_types_variants")
    is_shipping_required = db.Column(db.Boolean, default=False)

    @property
    def product_attributes_print(self):
        return " ".join([pa.name for pa in self.product_attributes])

    @property
    def variant_attributes_print(self):
        return " ".join([pa.name for pa in self.variant_attributes])

    @property
    def variant_ids(self):
        if not hasattr(self, "_variant_ids"):
            self._variant_ids = [var.id for var in self.variant_attributes]
        return self._variant_ids

    @property
    def attr_ids(self):
        if not hasattr(self, "_attr_ids"):
            self._attr_ids = [var.id for var in self.product_attributes]
        return self._attr_ids

    def set_attributes(self, attributes):
        for pa in self.product_attributes:
            if pa.id not in attributes:
                self.product_attributes.remove(pa)
            else:
                attributes.remove(pa.id)

        for attr_id in attributes:
            pa = ProductAttribute.query.filter_by(id=attr_id).first()
            self.product_attributes.append(pa)
            db.session.flush()

    def set_variants(self, variants):
        for pv in self.variant_attributes:
            if pv.id not in variants:
                self.variant_attributes.remove(pv)
            else:
                variants.remove(pv.id)

        for var_id in variants:
            pa = ProductAttribute.query.filter_by(id=var_id).first()
            self.variant_attributes.append(pa)
            db.session.flush()

    def dict(self):
        pass


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
        db.ForeignKey('product_products_attributes.id'))


class Product(db.Model, SeoModel):
    __tablename__ = "product_products"
    id = db.Column(db.Integer, primary_key=True)

    name = db.Column(db.String(32), nullable=False)
    description = db.Column(db.Text)

    price = db.Column(db.Integer, nullable=False)
    weight = db.Column(db.Integer, default=0)

    updated_at = db.Column(db.Integer, default=time.time, onupdate=time.time)

    images = db.Column(JSONB(), default={})
    attributes = db.Column(JSONB(), default={})

    is_published = db.Column(db.Boolean, default=True)
    is_featured = db.Column(db.Boolean, default=False)

    category_id = db.Column(db.Integer, db.ForeignKey('product_categories.id'))
    product_type_id = db.Column(db.Integer, db.ForeignKey('product_product_types.id'))

    product_type = db.relationship('ProductType')
    variants = db.relationship('ProductVariant')

    @property
    def attr_dict(self):
        return self.attributes

    def get_attr_choice_id(self, _id):
        if self.attributes.get(str(_id)):
            return int( self.attributes.get(str(_id)) )

    def dict(self, detailed=False):
        obj = dict(name=self.name, price=self.price)
        if detailed:
            obj.update(variants=[v.dict() for v in self.product_variants])
            obj.update(description=self.description, images=self.images)
            obj.update(self.seo_dict())
        else:
            obj['image'] = None
            if self.images:
                obj.update(image=self.images[0])
        return obj


class ProductVariant(db.Model):
    __tablename__ = "product_product_variants"
    id = db.Column(db.Integer, primary_key=True)

    sku = db.Column(db.String(32), unique=True, nullable=True)
    name = db.Column(db.String(255), default="")
    price_override = db.Column(db.Integer, nullable=True)

    product_id = db.Column(db.Integer, db.ForeignKey('product_products.id'))
    attributes = db.Column(JSONB(), default={})
    quantity = db.Column(db.Integer, default=1)
    quantity_allocated = db.Column(db.Integer, default=0)

    product = db.relationship("Product")

    def get_attr_choice_id(self, _id):
        if self.attributes.get(str(_id)):
            return int( self.attributes.get(str(_id)) )

    def generate_name(self):
        names = []
        for k, v in self.attributes.items():
            pa = AttributeChoiceValue.query.filter_by(id=v).first()
            names.append(pa.name)
        self.name = " / ".join(names)

    @property
    def quantity_available(self):
        return max(self.quantity - self.quantity_allocated, 0)

    def check_quantity(self, quantity):
        if quantity > self.quantity_available:
            return False
        return True

    def get_price(self, discounts=None):
        return self.price_override or self.product.price

    @property
    def is_shipping_required(self):
        return self.product.product_type.is_shipping_required

    @property
    def first_image(self):
        return self.product.images[0]

    def dict(self):
        obj = dict(sku=self.sku, name=self.name,
            price_override=self.price_override,)


class ProductAttribute(db.Model):
    __tablename__ = "product_products_attributes"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128))

    choices = db.relationship('AttributeChoiceValue', lazy="joined")

    def dict(self):
        return {'id':self.id, 'text':self.name}


class AttributeChoiceValue(db.Model):
    __tablename__ = "product_products_attributechoicevalue"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    attribute_id = db.Column(db.Integer, db.ForeignKey("product_products_attributes.id"))

    attribute = db.relationship('ProductAttribute')
    
    def dict(self):
        pass


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
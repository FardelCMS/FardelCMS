"""
Objects
=======

1. Category
    :id: ID for the category in database.
    :name: Name of the category to display.
    :description: 
    :children: List of Category objects.

2. Product
    :id: ID for the product in database.

3. Collection
    :id: ID for the collection in database.

"""

from flask import request

from fardel.core.rest import create_api, abort, Resource
from .models import *
from .. import mod
from fardel.ext import db, cache


ecommerce_product_api = create_api(mod)


def rest_resource(resource_cls):
    """ Decorator for adding resources to Api App """
    ecommerce_product_api.add_resource(resource_cls, *resource_cls.endpoints)
    return resource_cls


@rest_resource
class ProductCategoryApi(Resource):
    """
    :URL: ``/api/ecommerce/categories/`` or ``/api/ecommerce/categories/<category_id>/products/``
    """
    endpoints = ['/categories/', '/categories/<category_id>/products/']

    @cache.cached(timeout=50)
    def get(self, category_id=None):
        data = request.get_json()
        if category_id:
            cat = ProductCategory.query.filter_by(id=category_id).first()
            page = data.get('page', default=1, type=int)
            per_page = data.get('per_page', default=20, type=int)
            return cat.dict(products=True, page=page, per_page=per_page)

        categories = ProductCategory.query.filter_by(hidden=False, parent_id=None).all()
        return [cat.dict() for cat in categories]


@rest_resource
class ProductCollectionApi(Resource):
    """
    :URL: ``/api/ecommerce/collections/`` or ``/collections/<category_id>/products/``
    """
    endpoints = ['/collections/', '/collections/<collection_id>/products/']
    def get(self, collection_id=None):
        abort(404)


@rest_resource
class ProductApi(Resource):
    """
    :URL: ``/api/ecommerce/products/<product_id>/``
    """
    endpoints = ['/products/<product_id>/']
    def get(self, product_id):
        p = Product.query.filter_by(id=product_id).first()

        return p.dict()

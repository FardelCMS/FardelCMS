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
from sqlalchemy import func
from flask import request

from fardel.core.rest import create_api, abort, Resource
from fardel.core.utils import cache_get_key
from .models import *
from .. import mod
from fardel.ext import db, cache


ecommerce_product_api = create_api(mod)


def rest_resource(resource_cls):
    """ Decorator for adding resources to Api App """
    ecommerce_product_api.add_resource(resource_cls, *resource_cls.endpoints)
    return resource_cls
        

@rest_resource
class FeaturedProductApi(Resource):
    """
    :URL: ``/api/ecommerce/products/featured/``
    """
    endpoints = ['/products/featured/']
    @cache.cached(timeout=120)
    def get(self):
        return {}


@rest_resource
class ProductCategoryApi(Resource):
    """
    :URL: ``/api/ecommerce/categories/`` or ``/api/ecommerce/categories/<category_name>/products/``
    """
    endpoints = ['/categories/', '/categories/<category_name>/products/']

    # @cache.cached(timeout=600)
    def get(self, category_name=None):
        print('asdasd')
        if category_name:
            cat = ProductCategory.query.filter_by(name=category_name).first()
            page = request.args.get('page', default=1, type=int)
            per_page = request.args.get('per_page', default=20, type=int)
            order_by = request.args.get('order_by')
            return cat.dict(products=True, page=page, per_page=per_page, order_by=order_by)

        categories = ProductCategory.query.filter_by(hidden=False, parent_id=None).all()
        return {"categories":[cat.dict() for cat in categories]}


@rest_resource
class ProductCollectionApi(Resource):
    """
    :URL: ``/api/ecommerce/collections/`` or ``/collections/<category_id>/products/``
    """
    endpoints = ['/collections/', '/collections/<collection_id>/products/']
    @cache.cached(timeout=60)
    def get(self, collection_id=None):
        abort(404)


@rest_resource
@cache_get_key
class ProductApi(Resource):
    """
    :URL: ``/api/ecommerce/products/<product_id>/``
    """
    endpoints = ['/products/', '/products/<int:product_id>/']
    # @cache.cached(timeout=60)
    def get(self, product_id=None):
        if product_id:
            p = Product.query.filter_by(id=product_id).first_or_404()
            return {"product":p.dict(detailed=True)}

        page = request.args.get('page', default=1, type=int)
        per_page = request.args.get('per_page', default=20, type=int)
        order_by = request.args.get('order_by')
        query = Product.query.availables().order(order_by)
        ps = query.paginate(page=page, per_page=per_page, error_out=False).items
        return {'products':[p.dict() for p in ps]}    


@rest_resource
class FilterPanelApi(Resource):
    """
    :URL: ``/api/ecommerce/filter_panel/`` or ``/api/ecommerce/filter_panel/<category_name>/``
    """
    endpoints = ['/filter_panel/', '/filter_panel/<category_name>/']
    @cache.cached(timeout=600)
    def get(self, category_name=None):        
        key_query = db.session.query(func.jsonb_object_keys(Product.attributes)).distinct()

        if category_name:
            key_query = key_query.join(ProductCategory
                ).filter(ProductCategory.name==category_name)

        keys = {}
        for key in key_query.all():
            keys[key[0]] = [v[0] for v in
                db.session.query(Product.attributes[key[0]]).distinct().all()]

        return {"keys":keys}
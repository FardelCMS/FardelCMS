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
from flask_restful import Api, abort, Resource

from .models import *
from .. import mod
from web.ext import db


ecommerce_product_api = Api(mod)
    

def rest_resource(resource_cls):
    """ Decorator for adding resources to Api App """
    ecommerce_product_api.add_resource(resource_cls, *resource_cls.endpoints)
    return resource_cls


@rest_resource
class ProductCategory(Resource):
	endpoints = ['/product/categories/']
	def get(self):
		pass
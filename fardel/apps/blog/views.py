"""
.. _restapi/auth:

Objects
=======

1. Category
    :id: ID for the category in database.
    :name: Name of the category to display.
    :posts:


2. Post
    :id: ID for the post in database.
    :title: 
    :content:
    :allow_comment:
    :category:
    :image:
    :comments_count:
    :tags:
    :create_time:
    :update_time:
    :summarized:


3. Tag
    :id: ID for the tag in database.
    :name: Name of the tag.
    :frequency: 
    :posts: list of PostObjects (conditional).


4. Comment
    :id: ID for the comment in database.
    :content: Content of the comment.
    :create_time: (Timestamp) create time of the comment.
    :user: UserObject :ref:`restapi-auth` if user is login.
    :author_mail: Author email if user is not login.
    :author_name: Author name if user is not login.
    :replies: List of Comment Objects.
    
    
"""
import math

from sqlalchemy import and_, or_
from flask import request

from flask_jwt_extended import current_user, jwt_optional

from fardel.core.rest import create_api, abort, Resource
from fardel.core.utils import cache_get_key
from . import mod
from .models import *
from fardel.ext import db, cache


blog_api = create_api(mod)
    

def rest_resource(resource_cls):
    """ Decorator for adding resources to Api App """
    blog_api.add_resource(resource_cls, *resource_cls.endpoints)
    return resource_cls

def get_valid_post(post_id):
    post = Post.query.filter_by(id=post_id).first()
    if not post:
        return None
    if post and post.status.name != "Publish":
        return None
    return post

@mod.before_app_first_request
def create_permissions():
    setup_permissions()
    PostStatus.generate_default()


@rest_resource
@cache_get_key
class PostApi(Resource):
    """
    :URL: ``/api/blog/posts/`` and ``/api/blog/posts/<post_id>/``
    """
    endpoints = ['/posts/', '/posts/<post_id>/']

    @cache.cached(timeout=50)
    def get(self, post_id=None):
        """
        :optional url parameter:
            * post_id

        :optional url query string:
            * page (default: 1)
            * per_page (default: 16)

        :response:
            If post_id is provided:

            .. code-block:: python

               { "post": PostObject(with content) }

            If post_id is not provided:

            .. code-block:: python

                {
                    "posts":[list of PostObjects(without content and with summarized)]
                    "pages": Number of pages
                }

        :errors:
            If post id is not valid:

            :status_code: 404
            :response:
                .. code-block:: json

                    {"message":"No post with this id"}
        """
        if post_id:
            post = get_valid_post(post_id)
            if not post:
                return {"message":"No post with this id"}, 404

            return {'post':post.dict(summarized=False)}

        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 16, type=int)
        query = Post.query.filter(or_(PostStatus.name=="Publish",
            PostStatus.name=="Auto-Draft")).join(
            PostStatus, Post.status_id==PostStatus.id)
        pages = math.ceil(query.count() / per_page)
        posts = query.order_by(Post.id.desc()).paginate(page=page,
                    per_page=per_page, error_out=False).items
        return {'posts':[post.dict() for post in posts], 'pages':pages}


@rest_resource
class FeaturedPostsApi(Resource):
    """
    :URL:
    """
    endpoints = ['/featured/posts/', '/featured/posts/<category_name>/']
    @cache.cached(timeout=50)
    def get(self, category_name=None):
        if category_name:
            posts = Post.query.filter_by(featured=True
                ).outerjoin(Category).filter(Category.name==category_name).all()
            if posts:
                return {"posts":[post.dict() for post in posts]}

        posts = Post.query.filter_by(featured=True).all()
        return {"posts":[post.dict() for post in posts]}


@rest_resource
@cache_get_key
class CommentApi(Resource):
    """
    :URL: ``/api/blog/posts/<post_id>/comments/``
    """
    endpoints = ['/posts/<post_id>/comments/']
    method_decorators = {
        'get': [cache.cached(timeout=20)],
        'post':[jwt_optional],
    }
    def get(self, post_id):
        """
        :optional url query string:
            * page (default: 1)
            * per_page (default: 16)

        :response:
            .. code-block:: python

                {
                    "comments":[list of CommentObjects]
                    "pages": Number of pages
                }

        :errors:
            If post_id is not in valid ( not a published post or not found ):
            
            :status_code: 404
                .. code-block:: python

                   {"message":"No post with this id"}
        """
        post = get_valid_post(post_id)
        if not post:
            return {"message":"No post with this id"}, 404

        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 16, type=int)
        comment_query = Comment.query.filter_by(
            post_id=post_id, parent_comment_id=None, approved=True
        )
        pages = math.ceil(comment_query.count() / per_page)
        comments = comment_query.paginate(page=page,
            per_page=per_page, error_out=False).items
        return {'comments':[c.dict() for c in comments], 'pages':pages}

    def post(self, post_id):
        """
        * Authorization token is not required but optional

        :required data:
            * author_name (if you dont use access_token)
            * author_email (if you dont use access_token)
            * content

        :optional data:
            * parent_comment_id
        
        :response:
            .. code-block:: json

                {"message":"Comment successfuly added"}

        :errors:
            If post_id is not in valid ( not a published post or not found ):
            
            :status_code: 404
            :response:
                .. code-block:: python

                   {"message":"No post with this id"}

            If commenter information (user_id or (author_name, author_email) ) is not provided:
            
            :status_code: 422
            :response:
                .. code-block:: python
                    
                   {"message":"Author name and Author email are required to post a comment  or you need to sign in"}
        """
        post = get_valid_post(post_id)
        if not post:
            return {"message":"No post with this id"}, 404

        data = request.get_json()
        user_id = getattr(current_user, 'id', None)
        author_name = data.get('author_name')
        author_email = data.get('author_email')
        parent_comment_id = data.get('parent_comment_id')
        content = data.get('content')
        if not user_id and (not author_email or not author_name):
            return {
                "message":"Author name and Author email are required to\
 post a comment  or you need to sign in"
            }, 422

        if not content:
            return {"message":"Comment needs content"}, 422

        c = Comment(
            post_id=post_id, parent_comment_id=parent_comment_id, content=content,
            author_name=author_name, author_email=author_email, user_id=user_id,
        )
        db.session.add(c)
        db.session.commit()
        return {"message":"Comment successfuly added", 'comment':c.dict()}


@rest_resource
class TagApi(Resource):
    """
    :URL: ``/api/blog/tags/`` or ``/api/blog/tags/<tag_id>/posts/``
    """
    endpoints = ['/tags/<tag_id>/posts/', '/tags/']

    @cache.cached(timeout=50)
    def get(self, tag_id=None):
        """
        If tag_id is provided:
            :response:
                .. code-block:: python

                    {
                        "tag": TagObject(with posts)
                    }

            :errors:
                If tag_id is not in valid:
                
                :status_code: 404
                    .. code-block:: python

                       {"message":"No tag found with this id"}

        Without tag_id:
            :response:
                .. code-block:: python

                    {
                        "tags": [list of TagObjects(without posts)]
                    }
        """
        if tag_id:
            tag = Tag.query.filter_by(id=tag_id).first()
            if not tag:
                return {"message":"No tag found with this id"}, 404
            return {'tag':tag.dict(posts=True)}

        tags = Tag.query.all()
        return {'tags':[tag.dict() for tag in tags]}


@rest_resource
@cache_get_key
class CategoryApi(Resource):
    """
    :URL: ``/api/blog/categories/`` or ``/api/blog/categories/<category_name>/posts/``
    """
    endpoints = ['/categories/<category_name>/posts/', '/categories/']
    
    @cache.cached(timeout=50)
    def get(self, category_name=None):
        """
        If category_name is provided:        
            :optional url query string:
                * page (default: 1)
                * per_page (default: 16)

            :response:
                .. code-block:: python

                    {
                        "category": CategoryObject(with posts)
                    }

            :errors:
                If category_id is not in valid:
                
                :status_code: 404
                    .. code-block:: python

                       {"message":"No category found with this id"}

        Without category_id:
            :response:
                .. code-block:: python

                    {
                        "categories": [list of CategoryObject(without posts)]
                    }
        """
        if category_name:
            category = Category.query.filter_by(name=category_name).first()
            if not category:
                return {"message":"No category found with this id"}, 404
                
            page = request.args.get('page', 1, type=int)
            per_page = request.args.get('per_page', 16, type=int)

            category_dict = category.dict()
            query = Post.query.outerjoin(PostStatus
                ).filter(PostStatus.name=='Publish', Post.category_id==category.id)
            pages = math.ceil(query.count() / per_page)
            posts = query.order_by(Post.id.desc()
                ).paginate(page=page, per_page=per_page, error_out=False).items
            category_dict['posts'] = [post.dict() for post in posts]
            category_dict['pages'] = pages
            return {'category':category_dict}

        categories = Category.query.all()
        return {'categories':[category.dict() for category in categories]}
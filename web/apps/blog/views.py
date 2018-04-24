import math

from flask import request

from flask_restful import Api, abort, Resource
from flask_jwt_extended import current_user, jwt_optional

from . import mod
from .models import *


blog_api = Api(mod)
    

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
class PostApi(Resource):
    endpoints = ['/posts/', '/posts/<post_id>/']
    def get(self, post_id=None):
        if post_id:
            post = get_valid_post(post_id)
            if not post:
                return {"message":"No post with this id"}, 404

            return {'post':post.dict(summarized=False)}

        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 16, type=int)
        pages = math.ceil(Post.query.count() / per_page)
        posts = Post.query.outerjoin(PostStatus # Alternatively use filter_by(status_id==1) ?
            ).filter(PostStatus.name=='Publish').order_by(Post.publish_time
            ).paginate(page=page, per_page=per_page, error_out=False).items
        return {'posts':[post.dict() for post in posts], 'pages':pages}


@rest_resource
class CommentApi(Resource):
    endpoints = ['/posts/<post_id>/comments/']
    method_decorators = {
        'post':[jwt_optional],
    }

    def get(self, post_id):
        post = get_valid_post(post_id)
        if not post:
            return {"message":"No post with this id"}, 404

        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('page', 16, type=int)
        comments = Comment.query.filter_by(
            post_id=post_id, parent_comment_id=None, approved=True
        ).paginate(page=page, per_page=per_page, error_out=False).items

        return {'comments':[c.dict() for c in comments]}

    def post(self, post_id):
        post = get_valid_post(post_id)
        if not post:
            return {"message":"No post with this id"}, 404

        data = request.get_json()
        user_id = getattr(current_user, 'id', None)
        author_name = data.get('author_name')
        author_email = data.get('author_email')
        parent_comment_id = data.get('parent_comment_id')
        content = data.get('content')
        if not user_id and not (not author_email or not author_name):
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
    endpoints = ['/tags/<tag_id>/posts/', '/tags/']
    def get(self, tag_id=None):
        if tag_id:
            tag = Tag.query.filter_by(id=tag_id).first()
            if not tag:
                return {"message":"No tag found with this id"}, 404
            return {'tag':tag.dict(posts=True)}

        tags = Tag.query.all()
        return {'tags':[tag.dict() for tag in tags]}


@rest_resource
class CategoryApi(Resource):
    endpoints = ['/categories/<category_id>/posts/', '/categories/']
    def get(self, category_id=None):
        if category_id:
            category = Category.query.filter_by(id=category_id).first()
            if not category:
                return {"message":"No category found with this id"}, 404
                
            page = request.args.get('page', 1, type=int)
            per_page = request.args.get('page', 16, type=int)

            category_dict = category.dict()
            posts = Post.query.outerjoin(PostStatus # Alternatively use filter_by(status_id==1) ?
                ).filter(PostStatus.name=='Publish', Post.category_id==category_id
                ).order_by(Post.publish_time
                ).paginate(page=page, per_page=per_page, error_out=False).items
            category_dict['posts'] = [post.dict() for post in posts]
            return {'category':category_dict}

        categories = Category.query.all()
        return {'categories':[category.dict() for category in categories]}
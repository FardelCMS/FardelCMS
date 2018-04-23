from flask import request
from flask_restful import Api, Resource, abort
from flask_jwt_extended import jwt_required

from web.apps.blog.models import Post, Category, Tag, Comment
from web.ext import db

from .. import mod, staff_required_rest, admin_required_rest, permission_required

panel_blog_api = Api(mod)

panel_decorators = [staff_required_rest, jwt_required]

def rest_resource(resource_cls):
    """ Decorator for adding resources to Api App """
    panel_auth_api.add_resource(resource_cls, *resource_cls.endpoints)
    return resource_cls


class PostApi(Resource):
    endpoints = ('/blog/posts/', '/blog/posts/<post_id>/')
    method_decorators = {
        'get': [permission_required('can_get_posts')] + panel_decorators,
        'post': [permission_required('can_create_posts')] + panel_decorators,
        'delete': [permission_required('can_delete_posts')] + panel_decorators,
        'patch': [permission_required('can_publish_posts')] + panel_decorators,
        'put': [permission_required('can_edit_posts')] + panel_decorators,
    }

    def get(self, post_id=None):
        """ To get posts details """
        if post_id:
            p = Post.query.filter_by(id=post_id).first()
            return p.dict(summarized=False, admin=True)

        page = request.args.get('page', default=16, type=int)
        per_page = request.args.get('page', default=16, type=int)
        posts = Post.query.order_by(Post.id
            ).paginate(page=page, per_page=per_page, error_out=False).items
        return {'posts':[p.dict(admin=True) for p in posts]}

    def post(self, post_id=None):
        """ To create Post without publish for the first time """
        if post_id:
            abort(403)

        data = request.get_json()
        image = data.get('image')
        title = data.get('title')
        content = data.get('content')
        allow_comment = data.get('allow_comment')
        category_id = data.get('category_id')
        tags = data.get('tags')

        p = Post(
            image=image, title=title, edited_content=content,
            allow_comment=allow_comment, category_id=category_id
        )

        db.session.add(p)
        p.add_tags(tags)
        db.session.commit()
        return {'message':'Post successfuly saved'}

    def delete(self, post_id=None):
        """ To delete Post """
        if not post_id:
            abort(403)

        deleted = Post.query.filter_by(post_id).delete()
        db.session.commit()
        if deleted:
            return {'message':'successfuly deleted the post'}
        else:
            return {'message':'Post id is not valid or its already deleted'}, 404

    def patch(self, post_id=None):
        """ To edit Posts whenever it is changed in the panel """
        if not post_id:
            abort(403)

        data = request.get_json()
        content = data.get('content')

        p = Post.query.filter_by(id=post_id).first()
        if p:
            p.edited_content = content
            db.session.commit()
            return {}
        return {"message":"No post with id"}, 404

    def put(self, post_id=None):
        """ To save and publish Posts """
        if post_id:
            pass


class CommentApi(Resource):
    endpoints = (
        '/blog/posts/<post_id>/comments/', # To get
        '/blog/posts/<post_id>/comments/<comment_id>/' # To delete and edit
    )
    method_decorators = {
        'get': [permission_required('can_get_comments')] + panel_decorators,
        'delete': [permission_required('can_delete_comments')] + panel_decorators,
        'patch': [permission_required('can_edit_comments')] + panel_decorators,
    }

    def get(self, post_id, comment_id=None):
        pass

    def delete(self, post_id, comment_id=None):
        pass

    def patch(self, post_id, comment_id=None):
        pass


class TagApi(Resource):
    endpoints = (
        '/blog/tags/',
    )
    # Does it really need permission ?
    def get(self):
        """ Get closest tags to the string """
        like = request.args.get('like')
        if not like:
            return {"message":"provide a like string"}, 422
            
        tags = Tag.query.filter(Tag.name.like('%' + like +'%')).all()
        return {'tags':[tag.dict() for tag in tags]}


class CategoryApi(Resource):
    endpoints = (
        '/blog/categories/',
        '/blog/categories/<category_id>/'
    )
    method_decorators = {
        'get': [permission_required('can_get_comments')] + panel_decorators,
        'delete': [permission_required('can_delete_comments')] + panel_decorators,
        'patch': [permission_required('can_edit_comments')] + panel_decorators,
    }

    def get(self, category_id=None):
        pass

    def delete(self, category_id=None):
        pass

    def patch(self, category_id=None):
        pass
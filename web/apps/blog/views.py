from flask_restful import Api, abort, Resource
from flask_jwt_extended import current_user, jwt_optional

from . import mod
from .models import *


blog_api = Api(mod)

def rest_resource(resource_cls):
    """ Decorator for adding resources to Api App """
    blog_api.add_resource(resource_cls, *resource_cls.endpoints)
    return resource_cls


@rest_resource
class PostApi(Resource):
    endpoints = ['/posts/', '/posts/<post_id>/']
    def get(self, post_id=None):
        if post_id:
            post = Post.query.filter_by(id=post_id).first()
            if post.status.name != "Publish":
                return {"message":"No post with this id"}, 404

            return {'post':post.dict(summarized=False)}

        page = request.args.get('page', 1)
        posts = Post.query.outerjoin(PostStatus # Alternatively use filter_by(status_id==1) ?
            ).filter(PostStatus.name=='Publish').order_by(Post.publish_time
            ).paginate(page=page, per_page=16, error_out=False).items
        return {'posts':[post.dict() for post in posts]}


@rest_resource
class CommentApi(Resource):
    endpoints = ['/posts/<post_id>/comments/']
    method_decorators = {
        'post':[jwt_optional],
    }

    def get(self, post_id):
        post = Post.query.filter_by(id=post_id).first()
        if post.status.name != "Publish":
            return {"message":"No post with this id"}, 404

        page = request.args.get('page')
        comments = Comment.query.filter_by(post_id=self.id, parent_comment_id=None
            ).paginate(page=page, per_page=32, error_out=False).items

        return {'comments':[c.dict() for c in comments]}

    def post(self, post_id):
        data = request.get_json()
        user_id = getattr(current_user, 'id', None)
        author_name = data.get('author_name')
        author_email = data.get('author_email')
        parent_comment_id = data.get('parent_comment_id')
        content = data.get('content')
        if not user_id and not (not author_email or not author_name):
            return {
                "message":"Author name and Author email are required to post a comment."
            }, 422

        if not content:
            return {"message":"Comment needs content"}, 422

        c = Comment(
            post_id=post_id, parent_comment_id=parent_comment_id, content=content,
            author_name=author_name, author_email=author_email, user_id=user_id,
        )
        db.session.add(c)
        db.session.commit()
        return {"message":"Comment successfuly added.", 'comment':c.dict()}


class TagApi(Resource):
    endpoints = ['/tags/<tag_id>/', '/tags/']
    def get(self, tag_id):
        pass

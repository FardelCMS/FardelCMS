import time

from sqlalchemy.sql.expression import func
from sqlalchemy.exc import IntegrityError
from sqlalchemy_utils.types import TSVectorType
from sqlalchemy_searchable import SearchQueryMixin, make_searchable

from flask_sqlalchemy import BaseQuery
from flask_babel import lazy_gettext, gettext

from fardel.core.seo import SeoModel
from fardel.core.auth.models import AbstractModelWithPermission
from fardel.ext import db
from fardel.core.utils import convert_timestamp

__all__ = (
    'Category', 'Post', 'Tag', 'Comment', 'PostStatus', 'setup_permissions'
)

make_searchable()

def setup_permissions():
    Comment.setup_permissions()
    Category.setup_permissions()
    Post.setup_permissions()


class SearchQuery(BaseQuery, SearchQueryMixin):
    pass


class PostStatus(db.Model):
    """
    Post statuses:
        # Publish: Viewable by everyone. (1) 
        # Future: Scheduled to be published in a future date. (2)
        # Draft: Incomplete post viewable by anyone with proper user role. (3)
        # Pending:
            Awaiting a user with the publish_posts capability
            (typically a user assigned the Editor role) to publish. (4) 
        # Private:
            Viewable only to users at Administrator level. (5)
        # Trash: Posts in the Trash are assigned the trash status. (6)
        # Auto-Draft:
            Revisions that saves automatically
            while you are editing. (7)
    """
    __tablename__ = "blog_post_statuses"
    id = db.Column(db.Integer, primary_key=True, index=True)
    name = db.Column(db.String(32), index=True)

    @staticmethod
    def generate_default():
        statuses = [
            'Publish', 'Future', 'Draft', 'Pending',
            'Private', 'Trash', 'Auto-Draft'
        ]
        for status in statuses:
            ps = PostStatus.query.filter_by(name=status).first()
            if not ps:
                ps = PostStatus(name=status)
                db.session.add(ps)
                db.session.commit()

    @property
    def tranlations(self):
        return {
            "Publish": gettext('Publish'), "Future": gettext('Future'),
            "Draft": gettext('Draft'), "Pending": gettext('Pending'),
            "Private": gettext('Private'), "Trash": gettext('Trash'),
            "Auto-Draft": gettext('Auto-Draft')
        }

    def get_name(self):
        return self.tranlations[self.name]

    def dict(self):
        return dict(id=self.id, name=self.name)


class Category(db.Model, SeoModel, AbstractModelWithPermission):
    __tablename__ = "blog_categories"
    id = db.Column(db.Integer, primary_key=True, index=True)
    name = db.Column(db.String(64), unique=True)

    class Meta:
        permissions = (
            ('can_get_categories', 'Can get categories'),
            ('can_create_categories', 'Can create categories'),
            ('can_delete_categories', 'Can delete categories'),
        )

    @staticmethod
    def _bootstrap(count):
        from mimesis import Text
        text = Text(locale='en')

        for _ in range(count):
            c = Category(name=text.word())
            db.session.add(c)

            try:
                db.session.commit()
            except IntegrityError:
                db.session.rollback()

    def dict(self):
        obj = {'id':self.id, 'name':self.name}
        return obj


class Post(db.Model, SeoModel, AbstractModelWithPermission):
    query_class = SearchQuery
    __tablename__ = "blog_posts"
    id = db.Column(db.Integer, primary_key=True, index=True)
    
    image = db.Column(db.String(512))
    title = db.Column(db.String(256))
    content = db.Column(db.Text)
    summarized = db.Column(db.Text)
    edited_content = db.Column(db.Text)
    create_time = db.Column(db.TIMESTAMP, default=func.current_timestamp())
    update_time = db.Column(db.TIMESTAMP,
        default=func.current_timestamp(), onupdate=func.current_timestamp())
    publish_time = db.Column(db.TIMESTAMP)

    status_id = db.Column(db.Integer, db.ForeignKey('blog_post_statuses.id'), index=True)
    featured = db.Column(db.Boolean, default=False)
    allow_comment = db.Column(db.Boolean, default=True)

    category_id = db.Column(db.Integer,
        db.ForeignKey('blog_categories.id', ondelete="SET NULL"), index=True)
    category = db.relationship('Category', lazy="selectin")

    user_id = db.Column(db.Integer,
        db.ForeignKey("auth_users.id", ondelete="SET NULL"))
    user = db.relationship("User")

    comments = db.relationship("Comment", cascade="all,delete")
    status = db.relationship('PostStatus', lazy="joined")
    tags = db.relationship('Tag', secondary='blog_posts_tags', lazy="selectin")

    # To enable search uncomment following line
    # search_vector = db.Column(TSVectorType('title', 'content'))

    # And add these lines to alembic migrations
    # import sqlalchemy_utils
    # from sqlalchemy_searchable import sync_trigger
    # conn = op.get_bind()
    # sync_trigger(conn, 'blog_posts', 'search_vector', ['title', 'content'])


    class Meta:
        permissions = (
            ('can_get_posts', 'Can get posts'),
            ('can_create_posts', 'Can create posts'),
            ('can_publish_posts', 'Can publish posts'),
            ('can_edit_posts', 'Can edit posts'),
            ('can_delete_posts', 'Can delete posts'),
        )

    @property
    def tags_ids(self):
        if not self._tags_ids:
            self._tags_ids = [c.id for c in self.tags]
        return self._tags_ids

    def set_tags(self, tags):
        for tag in self.tags:
            if tag.name not in tags:
                self.tags.remove(tag)
                
        for tag_name in tags:
            tag_name = tag_name.strip()
            tag = Tag.query.filter_by(name=tag_name).first()
            if not tag:
                tag = Tag(name=tag_name)
                db.session.add(tag)
            self.tags.append(tag)
            db.session.flush()

    def get_tags(self):
        return " ".join([tag.name for tag in self.tags])

    @staticmethod
    def _bootstrap(count):
        from mimesis import Text
        text = Text(locale='en')

        for _ in range(count):
            pd = Post(
                title=text.title(), content=text.text(quantity=100),
                summarized=text.text(quantity=3), publish_time=func.current_timestamp(),
                status_id=PostStatus.query.filter_by(name="Draft").first().id,
                allow_comment=True,
                category_id=Category.query.order_by(func.random()).first().id,                
            )
            db.session.add(pd)

            for i in range(3):
                t = Tag.query.order_by(func.random()).first()
                pd.tags.append(t)
                
            pp = Post(
                title=text.title(), content=text.text(quantity=100),
                summarized=text.text(quantity=3), publish_time=func.current_timestamp(),
                status_id=PostStatus.query.filter_by(name="Publish").first().id,
                allow_comment=True,
                category_id=Category.query.order_by(func.random()).first().id,                
            )
            db.session.add(pp)

            for i in range(3):
                t = Tag.query.order_by(func.random()).first()
                pp.tags.append(t)

            db.session.flush()

            # try:
            db.session.commit()
            # except IntegrityError:
            #     db.session.rollback()

    @property
    def create_timestamp(self):
        return convert_timestamp(self.create_time)

    @property
    def update_timestamp(self):
        return convert_timestamp(self.update_time)

    @property
    def publish_timestamp(self):
        return convert_timestamp(self.publish_time) if self.publish_time else 0

    def get_comments(self, page=1):
        """ What is use of this function? """
        return Comment.query.filter_by(post_id=self.id, parent_comment_id=None
            ).paginate(page=page, per_page=32, error_out=False).items

    @property
    def comments_count(self):
        return Comment.query.filter_by(post_id=self.id).count()

    def get_status(self):
        pass

    def dict(self, summarized=True, admin=False):
        obj = {
            'id': self.id, 'title':self.title, 'allow_comment': self.allow_comment,
            'create_time':self.create_timestamp, 'update_time':self.update_timestamp,
            'publish_time':self.publish_timestamp,
            'tags':[tag.dict() for tag in self.tags],
            'image':self.image, 'comments_count': self.comments_count
        }
        if self.category:
            obj['category'] = self.category.dict()
            
        if summarized:
            obj['summarized'] = self.summarized
        else:
            obj['content'] = self.content

        if admin:
            obj['status'] = self.status.dict()
            
        if admin and not summarized:
            obj['editted_content'] = self.editted_content

        return obj


class Tag(db.Model):
    __tablename__ = "blog_tags"
    id = db.Column(db.Integer, primary_key=True, index=True)
    name = db.Column(db.String(64), index=True)
    frequency = db.Column(db.Integer, default=0)

    posts = db.relationship('Post', secondary='blog_posts_tags', lazy='select')

    @staticmethod
    def _bootstrap(count):
        from mimesis import Text
        text = Text(locale='en')

        for _ in range(count):
            t = Tag(name=text.word())
            db.session.add(t)

            try:
                db.session.commit()
            except IntegrityError:
                db.session.rollback()

    def panel_dict(self):
        return {'id': self.name, 'text': self.name}

    def dict(self, posts=False):
        obj = {
            'id':self.id, 'name':self.name
        }
        if posts:
            obj.update({"posts":[p.dict() for p in self.posts]})
        return obj


class PostTag(db.Model):
    __tablename__ = "blog_posts_tags"
    id = db.Column(db.Integer, primary_key=True)
    post_id = db.Column(db.Integer,
        db.ForeignKey('blog_posts.id'), index=True)
    tag_id = db.Column(db.Integer,
        db.ForeignKey('blog_tags.id'), index=True)


class Comment(db.Model, AbstractModelWithPermission):
    __tablename__ = "blog_comments"
    id = db.Column(db.Integer, primary_key=True, index=True)

    author_name = db.Column(db.String(32))
    author_email = db.Column(db.String(128))

    content = db.Column(db.Text)
    create_time = db.Column(db.TIMESTAMP, default=func.current_timestamp())
    approved = db.Column(db.Boolean, default=True)

    parent_comment_id = db.Column(db.Integer,
        db.ForeignKey('blog_comments.id', ondelete="SET NULL"), index=True)
    post_id = db.Column(db.Integer,
        db.ForeignKey('blog_posts.id'), index=True)
    user_id = db.Column(db.Integer,
        db.ForeignKey('auth_users.id', ondelete="SET NULL"))

    user = db.relationship("User")
    parent_comment = db.relationship('Comment',
        remote_side=[id], lazy="select")
    replies = db.relationship('Comment', lazy="joined")

    class Meta:
        permissions = (
            ('can_get_comments', 'Can get comments'),
            ('can_delete_comments', 'Can delete comments'),
            ('can_edit_comments', 'Can edit comments'),
        )

    @staticmethod
    def _bootstrap(count):
        from mimesis import Text
        import random
        from ...core.auth.models import User

        text = Text(locale='en')

        for _ in range(count):
            c = Comment(
                content=text.text(quantity=10),
                user_id=User.query.order_by(func.random()).first().id,
                post_id=Post.query.filter_by(status_id=1
                    ).order_by(func.random()).first().id,                
            )
            db.session.add(c)

            if random.random() > .75:
                c.parent_comment_id = Comment.query.filter_by(
                    post_id=c.post_id).order_by(func.random()).first().id

            try:
                db.session.commit()
            except IntegrityError:
                db.session.rollback()

    @property
    def create_timestamp(self):
        return convert_timestamp(self.create_time)

    def dict(self):
        obj = {
            'author_email':self.author_email, 'author_name':self.author_name,
            'id':self.id, "content":self.content, 'create_time':self.create_timestamp,
            'replies': [c.dict() for c in self.replies]
        }
        if self.user:
            obj['user'] = self.user.dict()
        return obj

# @event.listens_for(PostTag, 'after_insert')
# def receive_before_insert(mapper, connection, target):
#     print(target)
#     print(mapper)
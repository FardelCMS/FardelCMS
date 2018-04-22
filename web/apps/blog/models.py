import time

from sqlalchemy.sql.expression import func
from sqlalchemy.exc import IntegrityError 
from sqlalchemy import event 

from ...core.auth.models import AbstractModelWithPermission
from ...ext import db

__all__ = (
    'Category', 'Post', 'Tag', 'Comment', 'PostStatus', 'setup_permissions'
)

def setup_permissions():
    Comment.setup_permissions()
    Category.setup_permissions()
    Post.setup_permissions()
    Tag.setup_permissions()


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

class Category(db.Model, AbstractModelWithPermission):
    __tablename__ = "blog_categories"
    id = db.Column(db.Integer, primary_key=True, index=True)
    name = db.Column(db.String(64), unique=True)

    class Meta:
        permissions = (
            ('can_create_categories', 'Can create categories'),
            ('can_edit_categories', 'Can edit categories'),
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


class Post(db.Model, AbstractModelWithPermission):
    __tablename__ = "blog_posts"
    id = db.Column(db.Integer, primary_key=True, index=True)
    
    image = db.Column(db.String(512))
    title = db.Column(db.String(256))
    content = db.Column(db.Text)
    editted_content = db.Column(db.Text)
    create_time = db.Column(db.Integer, default=time.time)
    update_time = db.Column(db.Integer, default=time.time, onupdate=time.time)
    publish_time = db.Column(db.Integer)

    status_id = db.Column(db.Integer, db.ForeignKey('blog_post_statuses.id'))
    allow_comment = db.Column(db.Boolean, default=True)

    category_id = db.Column(db.Integer, db.ForeignKey('blog_categories.id'))
    category = db.relationship('Category', backref='posts')

    status = db.relationship('PostStatus')
    tags = db.relationship('Tag', secondary='blog_posts_tags')
    # comments = db.relationship('Comment')

    class Meta:
        permissions = (
            ('can_get_posts', 'Can get posts'),
            ('can_create_posts', 'Can create posts'),
            ('can_publish_posts', 'Can publish posts'),
            ('can_edit_posts', 'Can edit posts'),
            ('can_delete_posts', 'Can delete posts'),
        )

    @staticmethod
    def _bootstrap(count):
        from mimesis import Text
        text = Text(locale='en')

        for _ in range(count):
            p = Post(
                title=text.title(), content=text.text(quantity=100),
                publish_time=time.time(), status_id=1, allow_comment=True,
                category_id=Category.query.order_by(func.random()).first().id,                
            )
            db.session.add(p)

            for i in range(3):
                t = Tag.query.order_by(func.random()).first()
                p.tags.append(t)

            db.session.flush()

            try:
                db.session.commit()
            except IntegrityError:
                db.session.rollback()

    def get_comments(self, page=1):
        """ What is use of this function? """
        return Comment.query.filter_by(post_id=self.id, parent_comment_id=None
            ).paginate(page=page, per_page=32, error_out=False).items

    @property
    def comments_count(self):
        return Comment.query.filter_by(post_id=self.id).count()

    def get_status(self):
        pass

    def summarized(self, length=256):
        return "%s ..." % self.content[:length]

    def dict(self, summarized=True, admin=False):
        obj = {
            'id': self.id, 'title':self.title, 'allow_comment': self.allow_comment,
            'create_time':self.create_time, 'update_time':self.update_time,
            'category':self.category.dict(), 'tags':[tag.dict() for tag in self.tags],
            'image':self.image, 'comments_count': self.comments_count
        }
        if summarized:
            obj['summarized'] = self.summarized()
        else:
            obj['content'] = self.content
            # obj['comments'] = [c.dict() for c in self.get_comments()]
        if admin:
            obj.update({'editted_content':self.editted_content, 'status':self.status})
        return obj


class Tag(db.Model, AbstractModelWithPermission):
    __tablename__ = "blog_tags"
    id = db.Column(db.Integer, primary_key=True, index=True)
    name = db.Column(db.String(64), index=True)
    frequency = db.Column(db.Integer)

    posts = db.relationship('Post', secondary='blog_posts_tags')

    class Meta:
        permissions = (
            ('can_create_tags', 'Can create tags'),
            ('can_edit_tags', 'Can edit tags'),
        )

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

    def dict(self, posts=False):
        obj = {
            'id':self.id, 'name':self.name, 'frequency':self.frequency
        }
        if posts:
            obj.update({"posts":[p.dict() for p in self.posts]})
        return obj


class PostTag(db.Model):
    __tablename__ = "blog_posts_tags"
    id = db.Column(db.Integer, primary_key=True)
    post_id = db.Column(db.Integer, db.ForeignKey('blog_posts.id'))
    tag_id = db.Column(db.Integer, db.ForeignKey('blog_tags.id'))


class Comment(db.Model, AbstractModelWithPermission):
    __tablename__ = "blog_comments"
    id = db.Column(db.Integer, primary_key=True, index=True)

    author_name = db.Column(db.String(32))
    author_email = db.Column(db.String(128))

    content = db.Column(db.Text)
    create_time = db.Column(db.Integer, default=time.time)
    approved = db.Column(db.Boolean, default=True)

    parent_comment_id = db.Column(db.Integer, db.ForeignKey('blog_comments.id'))
    post_id = db.Column(db.Integer, db.ForeignKey('blog_posts.id'), index=True)
    user_id = db.Column(db.Integer, db.ForeignKey('auth_users.id'))

    user = db.relationship("User")
    parent_comment = db.relationship('Comment', remote_side=[id], backref='replies')

    class Meta:
        permissions = (
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
                post_id=Post.query.order_by(func.random()).first().id,                
            )
            db.session.add(c)

            if random.random() > .75:
                c.parent_comment_id = Comment.query.filter_by(
                    post_id=c.post_id).order_by(func.random()).first().id

            try:
                db.session.commit()
            except IntegrityError:
                db.session.rollback()

    def dict(self):
        obj = {
            'author_email':self.author_email, 'author_name':self.author_name,
            'id':self.id, "content":self.content, 'create_time':self.create_time,
            'replies': [c.dict() for c in self.replies]
        }
        if self.user:
            obj['user'] = self.user.dict()
        return obj

# @event.listens_for(PostTag, 'after_insert')
# def receive_before_insert(mapper, connection, target):
#     print(target)
#     print(mapper)
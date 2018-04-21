import time

from web.ext import db

__all__ = (
    'Category', 'Post', 'Tag', 'Comment', 'PostStatus'
)

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

class Category(db.Model):
    __tablename__ = "blog_categories"
    id = db.Column(db.Integer, primary_key=True, index=True)
    name = db.Column(db.String(64))


class Post(db.Model):
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

    def get_comments(self, page=1):
        """ What is use of this function? """
        return Comment.query.filter_by(post_id=self.id, parent_comment_id=None
            ).paginate(page=page, per_page=32, error_out=False).items

    def get_status(self):
        pass

    def summarized(self):
        return "%s ..." % self.content[:256]

    def dict(self, summarized=True, admin=False):
        obj = {
            'id': self.id, 'title':self.title, 'url':self.url,
            'allow_comment': self.allow_comment, 'created_time':self.created_time,
            'update_time':self.update_time,
            'category':self.category.dict(), 'tags':[tag.dict() for tag in self.tags]
        }
        if summarized:
            obj['summarized'] = self.summarized
        else:
            obj['content'] = self.content
            # obj['comments'] = [c.dict() for c in self.get_comments()]
        if admin:
            obj.update({'editted_content':self.editted_content, 'status':self.status})
        return obj


class Tag(db.Model):
    __tablename__ = "blog_tags"
    id = db.Column(db.Integer, primary_key=True, index=True)
    name = db.Column(db.String(64), index=True)
    frequency = db.Column(db.Integer)

    posts = db.relationship('Post', secondary='blog_posts_tags')

    def dict(self, posts=False):
        obj = {
            'id':self.id, 'name':self.name, 'frequency':self.frequency
        }
        if posts:
            return obj.update({"posts":self.posts.dict()})
        else:
            return obj


class PostTag(db.Model):
    __tablename__ = "blog_posts_tags"
    id = db.Column(db.Integer, primary_key=True)
    post_id = db.Column(db.Integer, db.ForeignKey('blog_posts.id'))
    tag_id = db.Column(db.Integer, db.ForeignKey('blog_tags.id'))


class Comment(db.Model):
    __tablename__ = "blog_comments"
    id = db.Column(db.Integer, primary_key=True, index=True)

    author_name = db.Column(db.String(32))
    author_email = db.Column(db.String(128))

    content = db.Column(db.Text)
    create_time = db.Column(db.Integer, default=time.time)
    approved = db.Column(db.Boolean, default=False)

    parent_comment_id = db.Column(db.Integer, db.ForeignKey('blog_comments.id'))
    post_id = db.Column(db.Integer, db.ForeignKey('blog_posts.id'), index=True)
    user_id = db.Column(db.Integer, db.ForeignKey('auth_users.id'))

    user = db.relationship("User")
    parent_comment = relationship('Comment', remote_side=[id], backref='replies')

    def dict(self):
        return {
            'author_email':self.author_email, 'author_name':self.author_name,
            'id':self.id, "content":self.content, 'status':self.status,
            'create_time':self.create_time, "user": self.user.email,
            'replies': [c.dict() for c in self.replies]
        }


# @event.listens_for(Post, 'before_insert')
# def receive_before_insert(mapper, connection, target):
#     pass
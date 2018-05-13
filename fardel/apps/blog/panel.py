import os
import pathlib
import math
import datetime

from sqlalchemy import and_

from flask import (request, Blueprint, render_template,
    request, redirect, url_for, abort, current_app, jsonify)
from flask_login import current_user, login_required
from flask_babel import gettext

from fardel.apps.blog.models import Post, Category, Tag, Comment, PostStatus
from fardel.ext import db

from fardel.core.media.models import File
from fardel.core.panel import staff_required, admin_required, permission_required
from fardel.core.panel.sidebar import panel_sidebar, Section, Link, ChildLink
from fardel.core.panel.views.media import is_safe_path

PATH_TO_BLOG_APP = pathlib.Path(__file__).parent

mod = Blueprint(
    'blog_panel',
    'blog_panel',
    url_prefix="/panel/blog",
    static_folder=str(PATH_TO_BLOG_APP / "static"),
    template_folder=str(PATH_TO_BLOG_APP / "templates"),
)

@mod.before_app_first_request
def add_blog_section():
    section = Section(gettext('Weblog/Magazine'))
    blog_link = Link('fa fa-pencil', gettext('Posts'),
            permission="can_get_posts")
    blog_link.add_child(ChildLink(gettext("All Posts"),
        url_for('blog_panel.posts_list'), permission="can_get_posts"))
    blog_link.add_child(ChildLink(gettext("Create Post"),
        url_for('blog_panel.posts_create'), permission="can_create_posts"))

    section.add_link(blog_link)

    cat_link = Link('fa fa-clipboard', gettext('Categories'),
            permission="can_get_categories")
    cat_link.add_child(ChildLink(gettext("All Categories"),
        url_for('blog_panel.categories_list'), permission="can_get_categories"))
    cat_link.add_child(ChildLink(gettext("Create Category"),
        url_for('blog_panel.categories_create'), permission="can_create_categories"))
    section.add_link(cat_link)

    section.add_link(
        Link('fa fa-tags', gettext('Tags'), url_for('blog_panel.tags_list'),
            permission="can_get_tags")
    )
    panel_sidebar.add_section(section)

@permission_required('can_upload_files')
@staff_required
@mod.route('/upload/images/', methods=['POST'])
@login_required
def upload_images():
    file = request.files.get('file')
    path = "images/%s" % datetime.datetime.now().year
    if not file:
        return jsonify({"message":"No file to upload"}), 422

    uploads_folder = current_app.config['UPLOAD_FOLDER']
    lookup_folder = uploads_folder / path
    if is_safe_path(str(os.getcwd() / lookup_folder), str(lookup_folder)):
        file = File(path, file=file)
        file.save()
        return jsonify(
            {'message':'File saved successfully',
             'location':file.url})
    return jsonify({"message":"Invalid path"}), 422

@permission_required('can_get_posts')
@staff_required
@mod.route('/posts/list/')
@login_required
def posts_list():
    page = request.args.get('page', default=1, type=int)
    per_page = request.args.get('per_page', default=20, type=int)
    query = Post.query.filter(and_(PostStatus.name!="Trash",
        PostStatus.name!=None)).outerjoin(PostStatus)
    pages = math.ceil(query.count() / per_page)
    posts = query.order_by(Post.id.desc()).paginate(page=page, per_page=per_page, error_out=False).items
    return render_template('posts_list.html', posts=posts, page=page, pages=pages)

@permission_required('can_create_posts')
@staff_required
@mod.route('/posts/create/', methods=["POST", "GET"])
@login_required
def posts_create():
    """ To create Post without publish for the first time """
    if request.method == "POST":
        data = request.form
        image = request.files.get('image')
        file = None
        if image:
            path = "images/%s" % datetime.datetime.now().year
            file = File(path, file=image)
            file.save()

        title = data.get('title')
        content = data.get('content')
        summarized = data.get('summarized')
        allow_comment = data.get('allow_comment', type=bool)
        category_id = data.get('category_id', type=int)
        tags = data.getlist('tags')

        p = Post(
            title=title, edited_content=content,
            allow_comment=allow_comment, category_id=category_id,
            summarized=summarized
        )
        if file:
            p.image = file.url

        ps = PostStatus.query.filter_by(name="Draft").first()
        p.status_id = ps.id
        p.user_id = current_user.id

        db.session.add(p)
        p.set_tags(tags)
        db.session.commit()
        return redirect(url_for('blog_panel.posts_list'))
    categories = Category.query.all()
    return render_template('posts_form.html', categories=categories)

@permission_required('can_create_posts')
@staff_required
@mod.route('/posts/edit/<int:post_id>/', methods=["POST", "GET"])
@login_required
def posts_edit(post_id):
    post = Post.query.filter_by(id=post_id).first_or_404()
    if request.method == "POST":
        data = request.form
        image = request.files.get('image')
        if image:
            path = "images/%s" % datetime.datetime.now().year
            file = File(path, file=image)
            file.save()
            post.image = file.url

        title = data.get('title')
        content = data.get('content')
        summarized = data.get('summarized')
        allow_comment = data.get('allow_comment', type=bool)
        category_id = data.get('category_id', type=int)
        tags = data.getlist('tags')
        print(tags)

        post.title = title
        post.edited_content = content
        post.summarized = summarized
        post.allow_comment = allow_comment
        post.category_id = category_id
        post.set_tags(tags)
        db.session.commit()

        return redirect(url_for('blog_panel.posts_list'))

    categories = Category.query.all()
    return render_template("posts_form.html", categories=categories, post=post)

@permission_required('can_publish_posts')
@staff_required
@mod.route('/posts/publish/<int:post_id>/')
@login_required
def posts_publish(post_id):
    p = Post.query.filter_by(id=post_id).first_or_404()
    status = PostStatus.query.filter_by(name="Publish").first()
    p.status_id = status.id
    db.session.commit()
    return redirect(url_for('blog_panel.posts_list'))

@permission_required('can_publish_posts')
@staff_required
@mod.route('/posts/draft/<int:post_id>/')
@login_required
def posts_draft(post_id):
    p = Post.query.filter_by(id=post_id).first_or_404()
    status = PostStatus.query.filter_by(name="Draft").first()
    p.status_id = status.id
    db.session.commit()
    return redirect(url_for('blog_panel.posts_list'))

@permission_required('can_delete_posts')
@staff_required
@login_required
@mod.route('/posts/trash/<int:post_id>/')
def posts_trash(post_id):
    """ To delete Post """
    post = Post.query.filter_by(id=post_id).first_or_404()
    status = PostStatus.query.filter_by(name="Trash").first()
    post.status_id = status.id
    db.session.commit()
    return redirect(url_for('blog_panel.posts_list'))

@staff_required
@mod.route('/tags/')
@login_required
def tags_api():
    """ Get closest tags to the string """
    like = request.args.get('term')
    if not like:
        like = ""
    tags = Tag.query.filter(Tag.name.like('%' + like +'%')).limit(20)
    return jsonify({'results':[tag.panel_dict() for tag in tags]})

@staff_required
@mod.route('/tags/list/')
@login_required
def tags_list():
    """ Get closest tags to the string """
    like = request.args.get('term')        
    tags = Tag.query.all()
    return render_template('tags_list.html', tags=tags)

@staff_required
@mod.route('/tags/delete/<int:tag_id>/')
@login_required
def tags_delete(tag_id):
    """ Get closest tags to the string """
    deleted = Tag.query.filter_by(id=tag_id).delete()
    db.session.commit()
    if not deleted:
        abort(404)
    return redirect(url_for('blog_panel.tags_list'))

@staff_required
@mod.route('/categories/list/')
@login_required
def categories_list():
    categories = Category.query.all()
    return render_template("categories_list.html", categories=categories)

@staff_required
@mod.route('/categories/delete/<int:cat_id>/')
@login_required
def categories_delete(cat_id):
    deleted = Category.query.filter_by(id=cat_id).delete()
    db.session.commit()
    if not deleted:
        abort(404)
    return redirect(url_for('blog_panel.categories_list'))

@staff_required
@mod.route('/categories/create/', methods=["POST", "GET"])
@login_required
def categories_create():
    if request.method == "POST":
        data = request.form
        name = data.get('name')
        if not name:
            flash(gettext('Name is required'))
            return redirect(url_for('blog_panel.categories_create'))

        c = Category(name=name)
        db.session.add(c)
        db.session.commit()
        return redirect(url_for("blog_panel.categories_list"))
    return render_template("categories_form.html")
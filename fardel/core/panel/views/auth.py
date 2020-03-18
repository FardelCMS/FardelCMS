import math

from sqlalchemy import or_

from flask import (request, render_template, redirect, url_for,
                   jsonify, abort, current_app, flash)
from flask_login import current_user, login_required
from flask_babel import gettext, pgettext

from fardel.core.auth.models import User, Group, Permission
from fardel.ext import db

from .. import mod, staff_required, admin_required, permission_required


#########
# USERS #
#########

@mod.route('/auth/users/search/email/')
@permission_required("can_send_email")
@staff_required
@login_required
def email_users_search():
    like_query = request.args.get("q")
    users = User.query.filter(User._email.like("{}%".format(like_query))).all()
    return jsonify({
        "users": [{"text": u.email} for u in users],
    })


@mod.route('/auth/users/list/')
@permission_required("can_get_users")
@staff_required
@login_required
def users_list():
    page = request.args.get('page', type=int, default=1)
    per_page = request.args.get('per_page', type=int, default=40)
    query = User.query.filter_by(is_staff=False, is_admin=False)
    pages = math.ceil(query.count() / per_page)
    users = query.paginate(
        page=page, per_page=per_page, error_out=False).items
    return render_template('auth/users_list.html',
                           users=users, pages=pages, page=page)


@mod.route('/auth/users/edit/<int:user_id>/', methods=['POST', 'GET'])
@admin_required
@staff_required
@login_required
def users_edit(user_id):
    user = User.query.filter_by(id=user_id).first_or_404()
    if request.method == "POST":
        email = request.form.get('email')
        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')
        password = request.form.get('password')
        confirmed = request.form.get('confirmed', type=bool)
        is_admin = request.form.get('is_admin', type=bool)
        is_staff = request.form.get('is_staff', type=bool)
        group_ids = request.form.getlist('group_ids')

        if not email or not first_name or not last_name:
            flash('gettext(email, first name, last name and password fields can not be empty!)', 'error')
        user._email = email
        user.first_name = first_name
        user.last_name = last_name
        user.groups = []
        for gid in group_ids:
            group = Group.query.filter_by(id=gid).first()
            user.groups.append(group)

        if password and password != "":
            user.password = password

        user.confirmed = confirmed
        user.is_admin = is_admin
        user.is_staff = is_staff
        db.session.commit()

        if user.is_staff or user.is_admin:
            return redirect(url_for("panel.staffs_list"))
        else:
            return redirect(url_for("panel.users_list"))

    groups = Group.query.all()
    user_group_ids = [g.id for g in user.groups]
    return render_template('auth/users_form.html', user=user, groups=groups, user_group_ids=user_group_ids)


@mod.route('/auth/users/create/', methods=['POST', 'GET'])
@admin_required
@staff_required
@login_required
def users_create():
    if request.method == "POST":
        email = request.form.get('email')
        if User.query.filter_by(_email=email).first():
            flash(gettext('user with this email already exists.'), 'error')
            return redirect(url_for('panel.users_create'))

        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')
        password = request.form.get('password')
        confirmed = request.form.get('confirmed', type=bool)
        is_admin = request.form.get('is_admin', type=bool)
        group_ids = request.form.getlist('group_ids')

        for gid in group_ids:
            group = Group.query.filter_by(id=gid).first()
            user.groups.append(group)

        if not email or not first_name or not last_name:
            flash(gettext('email, first name, last name and password fields can not be empty!'), 'error')
            return redirect(url_for('panel.users_create'))

        user = User(_email=email, first_name=first_name, last_name=last_name, password=password,
                    confirmed=confirmed, is_admin=is_admin, group_id=group_id)

        db.session.add(user)
        db.session.commit()
        flash(gettext('user successfully created'), 'success')
        if user.is_staff or user.is_admin:
            return redirect(url_for("panel.staffs_list"))
        else:
            return redirect(url_for("panel.users_list"))
    groups = Group.query.all()
    return render_template('auth/users_form.html', groups=groups)


@mod.route('/auth/users/delete/<int:user_id>/')
@admin_required
@staff_required
@login_required
def users_delete(user_id):
    abort(404)

################
# STAFFMEMBERS #
################


@mod.route('/auth/staffs/list/')
@permission_required("can_get_users")
@admin_required
@staff_required
@login_required
def staffs_list():
    page = request.args.get('page', type=int, default=1)
    per_page = request.args.get('per_page', type=int, default=40)
    query = User.query.filter(or_(User.is_staff == True, User.is_admin == True))
    pages = math.ceil(query.count() / per_page)
    users = query.paginate(
        page=page, per_page=per_page, error_out=False).items
    return render_template('auth/users_list.html',
                           users=users, pages=pages, page=page)


###############
# GROUPS #
###############


@mod.route('/auth/permissions/list/')
@permission_required('can_get_permissions')
@staff_required
@login_required
def permissions_get():
    return jsonify({
        'permissions': [obj.dict() for obj in
                        Permission.query.all()]
    })

###########
# GRPOUPS #
###########


@mod.route('/auth/groups/list/')
@permission_required('can_get_groups')
@staff_required
@login_required
def groups_list():
    page = request.args.get('page', type=int, default=1)
    per_page = request.args.get('per_page', type=int, default=40)
    query = Group.query
    pages = math.ceil(query.count() / per_page)
    groups = query.paginate(
        page=page, per_page=per_page, error_out=False).items
    return render_template('auth/groups_list.html',
                           groups=groups, pages=pages, page=page)


@mod.route('/auth/group/create/', methods=["POST", "GET"])
@admin_required
@staff_required
@login_required
def groups_create():
    permissions = Permission.query.all()
    if request.method == "POST":
        name = request.form.get("name")
        permissions = request.form.getlist("permissions")

        group = Group(name=name)

        for pid in permissions:
            permission = Permission.query.filter_by(id=pid).first()
            group.permissions.append(permission)

        db.session.add(group)
        db.session.commit()
        flash(gettext("Group created successfully"))
        return redirect(url_for("panel.groups_list"))

    return render_template("auth/groups_form.html", permissions=permissions)


@mod.route('/auth/group/edit/<int:group_id>/', methods=["POST", "GET"])
@admin_required
@staff_required
@login_required
def groups_edit(group_id):
    group = Group.query.filter_by(id=group_id).first_or_404()
    if request.method == "POST":
        name = request.form.get("name")
        permissions = request.form.getlist("permissions")

        group.name = name
        group.permissions = []
        for pid in permissions:
            permission = Permission.query.filter_by(id=pid).first()
            group.permissions.append(permission)

        db.session.add(group)
        db.session.commit()
        flash(gettext("Group editted successfully"))
        return redirect(url_for("panel.groups_list"))

    permissions = Permission.query.all()
    group_permission_ids = [p.id for p in group.permissions]
    return render_template("auth/groups_form.html", permissions=permissions, group=group, group_permission_ids=group_permission_ids)

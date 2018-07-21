import math

from sqlalchemy import or_

from flask import (request, render_template, redirect, url_for,
    jsonify, abort, current_app, flash)
from flask_login import current_user, login_required

from fardel.core.auth.models import User, Group, Permission
from fardel.ext import db

from .. import mod, staff_required, admin_required, permission_required


#########
# USERS #
#########

@permission_required("can_get_users")
@staff_required
@login_required
@mod.route('/auth/users/list/')
def users_list():
    page = request.args.get('page', type=int, default=1)
    per_page = request.args.get('per_page', type=int, default=40)
    query = User.query.filter_by(is_staff=False, is_admin=False)
    pages = math.ceil(query.count() / per_page)
    users = query.paginate(
        page=page, per_page=per_page, error_out=False).items
    return render_template('auth/users_list.html',
        users=users, pages=pages, page=page)

# @permission_required("can_get_users")
# @staff_required
# @login_required
# @mod.route('/auth/users/get/<int:user_id>/')
# def users_get(user_id):
#     u = User.query.filter_by(id=user_id).first_or_404()
#     return render_template('auth/users_get.html', user=u)

@admin_required
@staff_required
@login_required
@mod.route('/auth/users/edit/<int:user_id>/', methods=['POST', 'GET'])
def users_edit(user_id):
    edditable_attrs = [
        'email', 'password', 'first_name',
        'last_name', 'group_id', 'confirmed',
        'is_admin', 'is_staff'
    ]
    user = User.query.filter_by(id=user_id).first_or_404()
    if request.method == "POST":
        email = request.form.get('email')
        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')
        password = request.form.get('password')
        confirmed = request.form.get('confirmed', type=bool)
        is_admin = request.form.get('is_admin', type=bool)
        is_staff = request.form.get('is_staff', type=bool)
        
        if not email or not first_name or not last_name or not password:
            flash('gettext(email, first name, last name and password fields can not be empty!)', 'error')    
        user._email = email
        user.first_name = first_name
        user.last_name = last_name
        user.password = password
        user.confirmed = confirmed
        user.is_admin = is_admin
        user.is_staff = is_staff
        db.session.commit()
        return redirect(url_for('panel.users_list'))
    return render_template('auth/users_form.html', user=user)

@admin_required
@staff_required
@login_required
@mod.route('/auth/users/create/', methods=['POST', 'GET'])
def users_create():
    if request.method == "POST":
        pass
    return render_template('auth/users_form.html')

@admin_required
@staff_required
@login_required
@mod.route('/auth/users/delete/<int:user_id>/')
def users_delete(user_id):
    abort(404)

################
# STAFFMEMBERS #
################

@permission_required("can_get_users")
@admin_required
@staff_required
@login_required
@mod.route('/auth/staffs/list/')
def staffs_list():
    page = request.args.get('page', type=int, default=1)
    per_page = request.args.get('per_page', type=int, default=40)
    query = User.query.filter(or_(User.is_staff==True, User.is_admin==True))
    pages = math.ceil(query.count() / per_page)
    users = query.paginate(
        page=page, per_page=per_page, error_out=False).items
    return render_template('auth/users_list.html',
        users=users, pages=pages, page=page)

@admin_required
@staff_required
@login_required
@mod.route('/auth/staffs/edit/<int:user_id>/')
def staffs_edit(user_id):
    abort(404)

@admin_required
@staff_required
@login_required
@mod.route('/auth/staffs/create/')
def staffs_create():
    abort(404)

###############
# PERMISSIONS #
###############

@permission_required('can_get_permissions')
@staff_required
@login_required
@mod.route('/auth/permissions/list/')
def permissions_get():
    return jsonify({
        'permissions': [obj.dict() for obj in 
            Permission.query.all()]
    })

###########
# GRPOUPS #
###########

@permission_required('can_get_groups')
@staff_required
@login_required
@mod.route('/auth/groups/list/')
def groups_list():
    abort(404)
    if group_id:
        g = Group.query.filter_by(id=group_id).first()
        if not g:
            return {"message": "Group not found"}, 404
        return {'group': g.dict()}

    return {
        "groups": [obj.dict() for obj in 
            Group.query.all()]
    }

@admin_required
@staff_required
@login_required
@mod.route('/auth/permissions/create/')
def groups_create(self):
    abort(404)
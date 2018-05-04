from flask import request, abort, jsonify, render_template
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
    per_page = request.args.get('per_page', type=int, default=32)
    users = User.query.paginate(
        page=page, per_page=per_page, error_out=False).items
    return render_template('', users=users)

@permission_required("can_get_users")
@staff_required
@login_required
@mod.route('/auth/users/get/<int:user_id>/')
def users_get(user_id):
    u = User.query.filter_by(id=user_id).first_or_404()
    return render_template('', user=u)

@admin_required
@staff_required
@login_required
@mod.route('/auth/users/edit/<int:user_id>/')
def users_edit(user_id):
    if not user_id:
        return self.obj_id_required()

    u = User.query.filter_by(id=user_id).first()
    if not u:
        return {"message": "User not found"}, 404

    data = request.get_json()
    edditable_attrs = [
        'email', 'password', 'first_name',
        'last_name', 'group_id', 'confirmed',
        'is_admin', 'is_staff'
    ]
    for attr in edditable_attrs:
        if data.get(attr):
            setattr(u, attr, data[attr])
    db.session.commit()

    return {"message":"User successfully updated", 'user':u.dict()}

@admin_required
@staff_required
@login_required
@mod.route('/auth/users/create/')
def users_create():
    abort(404)

@admin_required
@staff_required
@login_required
@mod.route('/auth/users/delete/<int:user_id>/')
def users_delete(user_id):
    if current_user.id == user_id:
        return {"message":"You can't delete yourself"}, 422

    if not user_id:
        abort(403)

    deleteds = User.query.filter_by(id=user_id).delete()
    db.session.commit()
    if deleteds == 1:
        return {"message":"User successfully deleted"}
    return {"message":"No user deleted"}, 404

################
# STAFFMEMBERS #
################

@permission_required("can_get_users")
@staff_required
@login_required
@mod.route('/auth/staffs/list/')
def staffs_list():
    page = request.args.get('page', type=int, default=1)
    per_page = request.args.get('per_page', type=int, default=32)
    users = User.query.paginate(
        page=page, per_page=per_page, error_out=False).items
    return render_template('', users=users)

@permission_required("can_get_users")
@staff_required
@login_required
@mod.route('/auth/staffs/get/<int:user_id>/')
def staffs_get(user_id):
    u = User.query.filter_by(id=user_id).first_or_404()
    return render_template('', user=u)

@admin_required
@staff_required
@login_required
@mod.route('/auth/staffs/edit/<int:user_id>/')
def staffs_edit(user_id):
    if not user_id:
        return self.obj_id_required()

    u = User.query.filter_by(id=user_id).first()
    if not u:
        return {"message": "User not found"}, 404

    data = request.get_json()
    edditable_attrs = [
        'email', 'password', 'first_name',
        'last_name', 'group_id', 'confirmed',
        'is_admin', 'is_staff'
    ]
    for attr in edditable_attrs:
        if data.get(attr):
            setattr(u, attr, data[attr])
    db.session.commit()

    return {"message":"User successfully updated", 'user':u.dict()}

@admin_required
@staff_required
@login_required
@mod.route('/auth/staffs/create/')
def staffs_create():
    abort(404)

@admin_required
@staff_required
@login_required
@mod.route('/auth/staffs/delete/<int:user_id>/')
def staffs_delete(user_id):
    if current_user.id == user_id:
        return {"message":"You can't delete yourself"}, 422

    if not user_id:
        abort(403)

    deleteds = User.query.filter_by(id=user_id).delete()
    db.session.commit()
    if deleteds == 1:
        return {"message":"User successfully deleted"}
    return {"message":"No user deleted"}, 404

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
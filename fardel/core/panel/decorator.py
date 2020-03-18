from functools import wraps
from flask import abort

from flask_jwt_extended import current_user
from flask_login import current_user as fl_current_user
from flask_restful import abort as rest_abort

__all__ = [
    'permission_required',
    'staff_required',
    'staff_required_rest',
    'admin_required',
    'admin_required_rest',
]


def permission_required(permission):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if fl_current_user and fl_current_user.can(permission):
                return f(*args, **kwargs)
            return abort(403)
        return decorated_function
    return decorator


def permission_required_rest(permission):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if current_user and current_user.can(permission):
                return f(*args, **kwargs)
            return rest_abort(403)
        return decorated_function
    return decorator


def staff_required(func):
    if not hasattr(func, 'decorators'):
        func.decorators = {}
    func.decorators['staff_required'] = True

    @wraps(func)
    def wrapper(*args, **kwargs):
        if fl_current_user and (fl_current_user.is_staff or fl_current_user.is_admin):
            return func(*args, **kwargs)
        return abort(403)
    return wrapper


def staff_required_rest(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if current_user and (current_user.is_staff or current_user.is_admin):
            return func(*args, **kwargs)
        return rest_abort(403)
    return wrapper


def admin_required(func):
    if not hasattr(func, 'decorators'):
        func.decorators = {}
    func.decorators['admin_required'] = True

    @wraps(func)
    def wrapper(*args, **kwargs):
        if fl_current_user and fl_current_user.is_authenticated and fl_current_user.is_admin:
            return func(*args, **kwargs)
        return abort(403)
    return wrapper


def admin_required_rest(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if current_user and current_user.is_admin:
            return func(*args, **kwargs)
        return rest_abort(403)
    return wrapper

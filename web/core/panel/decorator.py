from functools import wraps
from flask import abort

from flask_login import current_user
from flask_restful import abort as rest_abort

__all__ = [
    'permission_required',
    'staff_required_rest',
    'admin_required_rest',
]

def permission_required(permission):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.can(permission):
                rest_abort(403)
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def staff_required_rest(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if current_user.is_authenticated:
            if current_user.is_staff:
                return func(*args, **kwargs)
        return rest_abort(403)
    return wrapper

def admin_required_rest(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if current_user.is_authenticated:
            if current_user.is_admin:
                return func(*args, **kwargs)
        return rest_abort(403)
    return wrapper
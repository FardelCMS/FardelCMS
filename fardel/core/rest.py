from flask_restful import Api, abort, Resource
from flask_babel import gettext

__all__ = (
	'create_api', 'abort'
)

errors = {
    'NoAuthorizationError': {
        'message': gettext("Missing Authorization header"),
        'status': 403,
    },
    'ExpiredSignatureError': {
    	'message': gettext("Token is already expired"),
    	'status': 401
    }
}

def create_api(module):
	return Api(module, errors=errors)
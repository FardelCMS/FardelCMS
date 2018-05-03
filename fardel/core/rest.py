from flask_restful import Api, abort, Resource

__all__ = (
	'create_api', 'abort'
)

errors = {
    'NoAuthorizationError': {
        'message': "Missing Authorization header",
        'status': 403,
    },
    'ExpiredSignatureError': {
    	'message': "Token is already expired",
    	'status': 401
    }
}

def create_api(module):
	return Api(module, errors=errors)
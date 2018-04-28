from flask_restful import Api, abort, Resource

__all__ = (
	'create_api', 'abort'
)

errors = {
    'NoAuthorizationError': {
        'message': "Missing Authorization header",
        'status': 403,
    }
}

def create_api(module):
	return Api(module, errors=errors)
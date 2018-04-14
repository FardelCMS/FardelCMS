from flask import jsonify

from flask_restful import Resource, abort


class BaseResource(Resource):

    def bad_request(self):
        return {'message':'Unvalid form submitted'}, 400

    def check_data(self, data, requires):
        for r in requires:
            if r not in data:
                return False
            if not data[r]:
                return False
        return True

    def get(self, *args, **kwargs):
        abort(405)

    def post(self, *args, **kwargs):
        abort(405)

    def put(self, *args, **kwargs):
        abort(405)

    def patch(self, *args, **kwargs):
        abort(405)

    def delete(self, *args, **kwargs):
        abort(405)
import sqlalchemy
from flask import jsonify, request

from flask_restful import Resource, abort
from flask_babel import gettext

from fardel.ext import db

__all__ = (
    'BaseResource', 'GetBaseResource'
)


class BaseResource(Resource):

    def bad_request(self):
        return {'message': gettext('Invalid form submitted')}, 400

    def check_data(self, data, *or_requires):
        for requires in or_requires:
            satisfied = True

            if not isinstance(requires, list):
                raise Exception("or_requires are list each item not %s" % type(requires))

            for r in requires:
                if r not in data:
                    satisfied = False
                if not data[r]:
                    satisfied = False

            if satisfied:
                return True

        return False


class GetBaseResource(BaseResource):
    resource_class = None

    def check_implemented(self):
        if self.resource_class == None:
            raise NotImplementedError("resource_class have to be assigned")

    def obj_id_required(self):
        return {"message": gettext("obj_id must be provided")}, 422

    def get(self, obj_id=None):
        self.check_implemented()

        if obj_id:
            u = self.resource_class.query.filter_by(id=obj_id).first()
            if not u:
                return {"message": "%s not found" % self.resource_class.__name__}, 404
            return {self.resource_class.__name__.lower(): u.dict()}
        resource_name = "%ss" % self.resource_class.__name__.lower()
        page = request.args.get('page', type=int, default=1)
        return {
            resource_name: [obj.dict() for obj in
                            self.resource_class.query.paginate(
                page=page, per_page=32, error_out=False).items]
        }


class PostBaseResource(GetBaseResource):
    required_to_create = None
    optional_fields = ()

    def check_implemented(self):
        super(PostBaseResource, self).check_implemented()
        if self.required_to_create == None:
            raise NotImplementedError("required_to_create have to be assigned")

    def post(self, obj_id=None):
        self.check_implemented()

        fields = {}
        data = request.get_json()
        for field in self.required_to_create:
            if not data.get(field):
                return {'message': '%s must be provided.' % field}, 422
            fields[field] = data[field]

        for field in self.optional_fields:
            fields[field] = data.get(field)

        obj = self.resource_class(**fields)
        db.session.add(obj)
        try:
            db.session.commit()
        except sqlalchemy.exc.IntegrityError:
            return {"message": "%s already exists" % self.resource_class.__name__}, 422
        return {
            'message': "%s successfully added" % self.resource_class.__name__,
            self.resource_class.__name__.lower(): obj.dict()
        }


class DeleteBaseResource(GetBaseResource):
    def delete(self, obj_id=None):
        self.check_implemented()
        if not obj_id:
            abort(403)

        deleteds = self.resource_class.query.filter_by(id=obj_id).delete()
        db.session.commit()
        if deleteds == 1:
            return {"message": "%s successfully deleted" % self.resource_class.__name__}
        elif deleteds > 1:
            return {
                "message": "%ss successfully deleted, count: %d" % (
                    self.resource_class.__name__, deleteds
                )}
        return {"message": "No %s deleted" % self.resource_class.__name__.lower()}, 404

import os

from flask import request, current_app
from flask_restful import Api, abort
from flask_jwt_extended import jwt_required

from web.ext import db

from .. import mod, staff_required_rest, permission_required
from ...base import BaseResource
from ...media.models import File

panel_media_api = Api(mod)

panel_decorators = [staff_required_rest, jwt_required]


def rest_resource(resource_cls):
    """ Decorator for adding resources to Api App """
    panel_media_api.add_resource(resource_cls, *resource_cls.endpoints)
    return resource_cls


def is_safe_path(basedir, path, follow_symlinks=True):
    # resolves symbolic links
    if follow_symlinks:
        return os.path.realpath(path).startswith(basedir)

    return os.path.abspath(path).startswith(basedir)


@rest_resource
class FileApi(BaseResource):
    endpoints = ['/files/']
    # method_decorators = {
    #     'post': [permission_required('can_create_files')] + panel_decorators,
    #     'delete': [permission_required('can_delete_files')] + panel_decorators,
    # }
    def get(self):
        """ Directory listing of upload folder """
        uploads_folder = current_app.config['UPLOAD_FOLDER']
        path = request.args.get('path', '')
        lookup_folder = uploads_folder / path
        if is_safe_path(str(os.getcwd() / lookup_folder), str(lookup_folder)):
            response = {'files': [], 'directories':[]}
            for obj in os.listdir(lookup_folder):
                if os.path.isdir(lookup_folder / obj):
                    response['directories'].append(obj)
                else:
                    file = File(path, file_name=obj)
                    file = {'name':obj, 'url':file.url}
                    response['files'].append(file)
            return response
        return {"message":"Invalid path"}, 422

    def post(self):
        """ To create file """
        pass

    def delete(self):
        """ To delete file """
        pass
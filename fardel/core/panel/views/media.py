"""

Objects
=======

1. File
    :name: 
    :url:
    :path:


2. Directory
    :name: Name of the directory
    :path: Path of the folder


"""

import os

from flask import request, current_app
from flask_jwt_extended import jwt_required

from fardel.core.rest import create_api, abort, Resource
from fardel.ext import db

from .. import mod, staff_required_rest, permission_required
from ...base import BaseResource
from ...media.models import File


panel_media_api = create_api(mod)

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
class FileApi(Resource):
    """
    :URL: ``/api/panel/files/``
    """
    endpoints = ['/files/']
    method_decorators = {
        'get': [permission_required('can_see_directory')] + panel_decorators,
        'post': [permission_required('can_create_files')] + panel_decorators,
        'delete': [permission_required('can_delete_files')] + panel_decorators,
    }
    def get(self):
        """
        Directory listing of upload folder
        
        :user permission required: can_see_directory

        """
        uploads_folder = current_app.config['UPLOAD_FOLDER']
        path = request.args.get('path', '')
        lookup_folder = uploads_folder / path
        if not os.path.exists(str(os.getcwd() / lookup_folder)):
            return {"message": "No such a folder"}, 404

        if is_safe_path(str(os.getcwd() / uploads_folder), str(lookup_folder)):
            response = {'files': [], 'directories':[]}
            for obj in os.listdir(lookup_folder):
                if os.path.isdir(lookup_folder / obj):
                    response['directories'].append({'name':obj, 'path':os.path.join(path, obj)})
                else:
                    file = File(path, file_name=obj)
                    file = {
                        'name':obj,
                        'url':file.url,
                        'path':os.path.join(path, obj)
                    }
                    response['files'].append(file)
            return response
        return {"message":"Invalid path"}, 422

    def post(self):
        """ To create file """
        file = request.files.get('file')
        path = request.form.get('path', '')
        if not file:
            return {"message":"No file to upload"}, 422

        uploads_folder = current_app.config['UPLOAD_FOLDER']
        lookup_folder = uploads_folder / path
        if is_safe_path(str(os.getcwd() / lookup_folder), str(lookup_folder)):
            file = File(path, file=file)
            file.save()
            return {'message':'File saved successfully', 'file':{"url":file.url}}
        return {"message":"Invalid path"}, 422

    def delete(self):
        """ To delete file """
        data = request.get_json()
        if not data.get('url'):
            return {"message": "No file url specified"}, 422

        url = data['url']
        path_to_file = current_app.config['UPLOAD_FOLDER'] / url.replace('/uploads/', '', 1)

        if os.path.isdir(path_to_file):
            try:
                os.rmdir(path_to_file)
            except:
                return {"message":"Directory must be empty"}, 422
            return {"message":"File deleted successfully"}
            
        if os.path.isfile(path_to_file):
            os.remove(path_to_file)
            return {"message":"File deleted successfully"}

        return {"message":"File not found"}, 404


@rest_resource
class ImageAlbumApi(BaseResource):
    """
    :URL: ``/api/panel/image_album/``    
    """
    endpoints = ['/image_album/']
    method_decorators = {
        'get': [permission_required('can_see_directory')] + panel_decorators,
        'post': [permission_required('can_create_files')] + panel_decorators,
        'delete': [permission_required('can_delete_files')] + panel_decorators,
    }
    def get(self):
        """ Directory listing of upload folder """
        uploads_folder = current_app.config['UPLOAD_FOLDER']
        path = 'images'
        lookup_folder = uploads_folder / path
        response = {'images': []}
        for obj in os.listdir(lookup_folder):
            if not os.path.isdir(lookup_folder / obj):
                file = File(path, file_name=obj)
                file = {'name':obj, 'url':file.url}
                response['images'].append(file)
        return response

    def post(self):
        """ To create file """
        file = request.files.get('file')
        path = 'images'
        if not file:
            return {"message":"No file to upload"}, 422

        uploads_folder = current_app.config['UPLOAD_FOLDER']
        lookup_folder = uploads_folder / path
        file = File(path, file=file)
        file.save()
        return {'message':'Image saved successfully', 'file':{"url":file.url}}

    def delete(self):
        """ To delete file """
        data = request.get_json()
        if not data.get('url'):
            return {"message": "No file url specified"}, 422

        url = data['url']
        path_to_file = current_app.config['UPLOAD_FOLDER'] / url.replace('/uploads', 'images', 1)
            
        if os.path.isfile(path_to_file):
            os.remove(path_to_file)
            return {"message":"Image deleted successfully"}

        return {"message":"Image not found"}, 404

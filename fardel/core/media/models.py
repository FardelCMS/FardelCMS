import os
import uuid

from pathlib import Path
from flask import current_app, url_for
from werkzeug.utils import secure_filename

from ..auth.models import AbstractModelWithPermission

__all__ = ('File', 'setup_permissions')

def setup_permissions():
    File.setup_permissions()


class File(AbstractModelWithPermission):
    __slot__ = [
        'uuid', 'file_name', 'file', 'location', '_extension', '_name',
        '_url', '_abs_folder_path', '_abs_path'
    ]
    def __init__(self, location, file=None, file_name=None):
        attributes = ('_extension', '_name','_url', '_abs_folder_path', '_abs_path')
        self.uuid = uuid.uuid4()
        self.file_name = file_name or str(self.uuid)
        self.file = file
        self.location = location
        
        for attr in attributes:
            setattr(self, attr, None)

    @property
    def extension(self):
        if self._extension is None:
            self._extension = self.file.filename.rsplit('.', 1)[1].lower()
            return self._extension
        return self._extension

    @property
    def name(self):
        if self._name is None:
            self._name = "%s.%s" % (self.file_name, self.extension)
            return self._name
        return self._name

    def create_folders(self):
        if not os.path.isdir(str(self.abs_folder_path)):
            os.makedirs(str(self.abs_folder_path))

    def save(self):
        self.create_folders()
        filename = secure_filename(self.name)
        self.file.save(os.path.join(str(self.abs_folder_path), filename))

    @property
    def url(self):
        if self._url is None:
            path_format = '%s/%s'
            if self.file:
                path = path_format % (self.location, self.name)
                self._url = url_for('media.file_loader',
                    path_to_file=path)
            else:
                path = path_format % (self.location, self.file_name)
                self._url = url_for('media.file_loader',
                    path_to_file=path, _external=True)
            return self._url
        return self._url

    @property
    def abs_folder_path(self):
        if self._abs_folder_path is None:
            self._abs_folder_path = current_app.config['UPLOAD_FOLDER'] / self.location
            return self._abs_folder_path
        return self._abs_folder_path

    @property
    def abs_path(self):
        if self._abs_path is None:
            self._abs_path = self.abs_folder_path / self.name
            return self._abs_path
        return self._abs_path

    class Meta:
        permissions = (
            ('can_see_directory', 'Can see directory listing'),
            ('can_create_files', 'Can create files'),
            ('can_delete_files', 'Can delete files'),
        )
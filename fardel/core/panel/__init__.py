from .decorator import *

from flask import Blueprint

mod = Blueprint('panel', 'panel', url_prefix='/api/panel')
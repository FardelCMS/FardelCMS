import math

from flask import (request, render_template, redirect, url_for,
    jsonify, abort)
from flask_login import login_required

from fardel.ext import db
from ..panel import mod

from fardel.core.panel.decorator import staff_required

@staff_required
@mod.route('/orders/list/')
@login_required
def orders_list():
    pass
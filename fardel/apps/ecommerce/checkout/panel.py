import os
import datetime
import math

from flask import (request, render_template, redirect, url_for,
    jsonify, abort, current_app)
from flask_login import login_required

from fardel.core.panel.views.media import is_safe_path
from fardel.core.media.models import File
from fardel.ext import db
from ..panel import mod
from .models import *

from fardel.core.panel.decorator import staff_required

@staff_required
@mod.route('/payments/list/')
@login_required
def payments_list():
	page = request.args.get('page', default=1, type=int)
	per_page = request.args.get('per_page', default=20, type=int)
	query = Payment.query.order_by(Payment.create_time.asc())
	pages = math.ceil(query.count() / per_page)
	payments = query.paginate(page=page, per_page=per_page, error_out=False).items
	return render_template('payment/payments_list.html',
		payments=payments)

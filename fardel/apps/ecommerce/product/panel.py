from flask_login import login_required

from ..panel import mod

from fardel.core.panel.decorator import staff_required


@staff_required
@mod.route('/products/list/')
@login_required
def products_list():
	pass

@staff_required
@mod.route('/products/edit/<int:product_id>/', methods=["POST", "GET"])
@login_required
def products_edit(product_id):
	pass

@staff_required
@mod.route('/products/delete/<int:product_id>/')
@login_required
def products_delete(product_id):
	pass

@staff_required
@mod.route('/products/create/', methods=["POST", "GET"])
@login_required
def products_create(product_id):
	pass

@staff_required
@mod.route('/products/types/list/')
@login_required
def products_types_list():
	pass

@staff_required
@mod.route('/products/types/edit/<int:pt_id>/', methods=["POST", "GET"])
@login_required
def products_types_edit(pt_id):
	pass

@staff_required
@mod.route('/products/types/delete/<int:pt_id>/')
@login_required
def products_types_delete(pt_id):
	pass

@staff_required
@mod.route('/products/types/create/', methods=["POST", "GET"])
@login_required
def products_types_create():
	pass

@staff_required
@mod.route('/categories/list/')
@login_required
def categories_list():
	pass

@staff_required
@mod.route('/categories/edit/<int:c_id>/', methods=["POST", "GET"])
@login_required
def categories_edit(c_id):
	pass

@staff_required
@mod.route('/categories/delete/<int:c_id>/')
@login_required
def categories_delete(c_id):
	pass

@staff_required
@mod.route('/categories/create/', methods=["POST", "GET"])
@login_required
def categories_create():
	pass
import math

from flask import request, render_template, redirect, url_for
from flask_login import login_required

from fardel.ext import db
from ..panel import mod
from .models import *

from fardel.core.panel.decorator import staff_required


@staff_required
@mod.route('/products/list/')
@login_required
def products_list():
    page = request.args.get('page', default=1, type=int)
    per_page = request.args.get('per_page', default=20, type=int)
    query = Product.query.order_by(Product.id.desc())
    pages = math.ceil(query.count() / per_page)
    posts = query.paginate(page=page, per_page=per_page, error_out=False).items
    return render_template('product/products_list.html')

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
def products_create():
    if request.method == "POST":
        pass
    return render_template("product/products_form.html")

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
    pcs = ProductCategory.query.filter_by(parent_id=None).all()
    return render_template('product/categories_list.html', categories=pcs)

@staff_required
@mod.route('/categories/create/', methods=["POST", "GET"])
@login_required
def categories_create():
    if request.method == "POST":
        name = request.form.get('name')
        description = request.form.get('description')
        hidden = request.form.get('hidden', type=bool, default=False)

        seo_title = request.form.get('seo-title', default="")
        seo_description = request.form.get('seo-desc', default="")

        if not name:
            flash(gettext("Name is required"))
            return redirect(url_for('ecommerce_panel.categories_create'))

        pc = ProductCategory(name=name,
                             description=description,
                             seo_title=seo_title,
                             seo_description=seo_description,
                             hidden=hidden)
        db.session.add(pc)
        db.session.commit()
        return redirect(url_for('ecommerce_panel.categories_list'))
    return render_template('product/categories_form.html')

@staff_required
@mod.route('/categories/<int:c_id>/')
@login_required
def categories_info(c_id):
    pc = ProductCategory.query.filter_by(id=c_id).first_or_404()
    return render_template('product/categories_info.html', category=pc)

@staff_required
@mod.route('/categories/<int:c_id>/addsub/', methods=["POST", "GET"])
@login_required
def categories_addsub(c_id):
    ppc = ProductCategory.query.filter_by(id=c_id).first_or_404()
    if request.method == "POST":
        name = request.form.get('name')
        description = request.form.get('description')
        hidden = request.form.get('hidden', type=bool, default=False)

        seo_title = request.form.get('seo-title', default="")
        seo_description = request.form.get('seo-desc', default="")

        if not name:
            flash(gettext("Name is required"))
            return redirect(url_for('ecommerce_panel.categories_create'))

        pc = ProductCategory(name=name,
                             description=description,
                             hidden=hidden,
                             seo_title=seo_title,
                             seo_description=seo_description,
                             parent_id=ppc.id)
        db.session.add(pc)
        db.session.commit()
        return redirect(url_for('ecommerce_panel.categories_info', c_id=ppc.id))
    return render_template('product/categories_form.html')

@staff_required
@mod.route('/categories/edit/<int:c_id>/', methods=["POST", "GET"])
@login_required
def categories_edit(c_id):
    pc = ProductCategory.query.filter_by(id=c_id).first_or_404()
    if request.method == "POST":
        name = request.form.get('name')
        description = request.form.get('description')
        hidden = request.form.get('hidden', type=bool, default=False)

        seo_title = request.form.get('seo-title', default="")
        seo_description = request.form.get('seo-desc', default="")

        if not name:
            flash(gettext("Name is required"))
            return redirect(url_for('ecommerce_panel.categories_create'))

        pc.name = name
        pc.description = description
        pc.hidden = hidden
        pc.seo_title = seo_title
        pc.seo_description = seo_description

        db.session.commit()
        if pc.parent_id == None:
            return redirect(url_for('ecommerce_panel.categories_list'))
        return redirect(url_for('ecommerce_panel.categories_info', c_id=pc.parent_id))
    return render_template('product/categories_form.html', category=pc)

@staff_required
@mod.route('/categories/delete/<int:c_id>/')
@login_required
def categories_delete(c_id):
    pc = ProductCategory.query.filter_by(id=c_id).first_or_404()
    db.session.delete(pc)
    db.session.commit()
    if pc.parent_id:
        return redirect(url_for('ecommerce_panel.categories_info', c_id=pc.parent_id))
    return redirect(url_for('ecommerce_panel.categories_list'))

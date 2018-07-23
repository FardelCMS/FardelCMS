import os
import datetime
import math

from flask import (request, render_template, redirect, url_for,
    jsonify, abort, current_app, flash)
from flask_login import login_required
from flask_babel import gettext, pgettext

from fardel.core.panel.views.media import is_safe_path
from fardel.core.media.models import File
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
    products = query.paginate(page=page, per_page=per_page, error_out=False).items
    products_types = ProductType.query.all()
    return render_template('product/products_list.html',
        products=products, products_types=products_types)

@staff_required
@mod.route('/products/info/<int:product_id>/')
@login_required
def products_info(product_id):
    p = Product.query.filter_by(id=product_id).first_or_404()
    if not p.product_type.has_variants:
        abort(404)
    return render_template('product/products_info.html', product=p)

@staff_required
@mod.route('/products/album/<int:product_id>/', methods=["POST", "GET"])
@login_required
def products_images(product_id):
    p = Product.query.filter_by(id=product_id).first_or_404()
    if request.method == "POST":
        file = request.files.get('file')
        path = "images/%s" % datetime.datetime.now().year
        if not file:
            return jsonify({"message":"No file to upload"}), 422

        uploads_folder = current_app.config['UPLOAD_FOLDER']
        lookup_folder = uploads_folder / path
        if is_safe_path(str(os.getcwd() / lookup_folder), str(lookup_folder)):
            file = File(path, file=file)
            file.save()
            if not isinstance(p.images, list):
                images = []
            else:
                images = p.images[:]
            images.append(file.url)
            p.images = images
            db.session.commit()
            return "OK"
        return "FAIL", 400
    return render_template('product/products_images.html', product=p)

@staff_required
@mod.route('/products/album/<int:product_id>/delete/<int:image_index>/')
@login_required
def product_images_delete(product_id, image_index):
    p = Product.query.filter_by(id=product_id).first_or_404()
    images = p.images[:]
    del images[image_index]
    p.images = images
    db.session.commit()
    return redirect(url_for('ecommerce_panel.products_images', product_id=p.id))

@staff_required
@mod.route('/products/info/<int:product_id>/variants/add/',
    methods=["POST", "GET"])
@login_required
def variants_add(product_id):
    p = Product.query.filter_by(id=product_id).first_or_404()
    if request.method == "POST":
        sku = request.form.get('sku')
        price_override = request.form.get('price_override', type=int)
        quantity = request.form.get('quantity', type=int)

        attributes = {}
        for attr in p.product_type.variant_attributes:
            if request.form.get('variant-attr-%d' % attr.id):
                attributes[attr.id] = request.form.get('variant-attr-%d' % attr.id)
        
        check_pv = ProductVariant.query.filter_by(product_id=p.id, attributes=attributes).first()
        if check_pv:
            flash(gettext("You can't have same attributes for two variant."), 'error')
            return redirect(url_for('ecommerce_panel.products_info', product_id=p.id))

        pv = ProductVariant(
            product_id=p.id,
            sku=sku,
            attributes=attributes,
            quantity=quantity
        )
        if price_override and price_override > 0:
            pv.price_override = price_override
        pv.generate_name()
        db.session.add(pv)
        db.session.commit()
        return redirect(url_for('ecommerce_panel.products_info', product_id=p.id))
    return render_template('product/variants_form.html', product=p)

@staff_required
@mod.route('/products/info/<int:product_id>/variants/edit/<int:var_id>/',
    methods=["POST", "GET"])
@login_required
def variants_edit(product_id, var_id):
    p = Product.query.filter_by(id=product_id).join(ProductVariant).first_or_404()
    pv = ProductVariant.query.filter_by(id=var_id).first_or_404()
    if pv.product_id != p.id:
        abort(404)
    if request.method == "POST":
        sku = request.form.get('sku')
        price_override = request.form.get('price_override', type=int)
        quantity = request.form.get('quantity', type=int)

        attributes = {}
        for attr in p.product_type.variant_attributes:
            if request.form.get('variant-attr-%d' % attr.id):
                attributes[attr.id] = request.form.get('variant-attr-%d' % attr.id)

        pv.sku = sku
        if price_override and price_override > 0:
            pv.price_override = price_override 
        pv.attributes = attributes
        pv.quantity = quantity
        pv.generate_name()
        db.session.commit()
        return redirect(url_for('ecommerce_panel.products_info', product_id=p.id))
    return render_template('product/variants_form.html', variant=pv, product=p)

@staff_required
@mod.route('/products/info/<int:product_id>/variants/delete/<int:var_id>/')
@login_required
def variants_delete(product_id, var_id):
    p = Product.query.filter_by(id=product_id).join(ProductVariant).first_or_404()
    pv = ProductVariant.query.filter_by(id=var_id).first_or_404()
    if pv.product_id != p.id:
        abort(404)

    db.session.delete(pv)
    db.session.commit()
    return redirect(url_for('ecommerce_panel.products_info', product_id=p.id))

@staff_required
@mod.route('/products/edit/<int:product_id>/', methods=["POST", "GET"])
@login_required
def products_edit(product_id):
    p = Product.query.filter_by(id=product_id).first_or_404()
    product_type = p.product_type
    if request.method == "POST":
        name = request.form.get("name")
        description = request.form.get("description", default="")
        seo_title = request.form.get("seo-title", default="")
        seo_description = request.form.get("seo-description", default="")
        price = request.form.get("price", type=int)
        sku = request.form.get("sku")
        category_id = request.form.get('category_id', type=int)
        publish = request.form.get('publish', type=bool)
        featured = request.form.get('featured', type=bool)
        quantity = request.form.get("quantity", type=int, default=0)
        attributes = {}
        for attr in product_type.product_attributes:
            if request.form.get('attribute-%d' % attr.id):
                attributes[attr.id] = request.form.get('attribute-%d' % attr.id)

        p.name = name
        p.description = description
        p.seo_title = seo_title
        p.seo_description = seo_description
        p.price = price
        p.sku = sku
        p.category_id = category_id
        p.is_published = publish
        p.is_featured = featured
        p.attributes = attributes
        if not product_type.has_variants:
            p.variants[0].quantity = quantity
            p.variants[0].sku = sku
        db.session.commit()

        return redirect(url_for('ecommerce_panel.products_list'))
    categories = ProductCategory.query.all()
    return render_template('product/products_form.html',
        product=p, product_type=product_type, categories=categories)

@staff_required
@mod.route('/products/delete/<int:product_id>/')
@login_required
def products_delete(product_id):
    pt = Product.query.filter_by(id=product_id).first_or_404()
    db.session.delete(pt)
    db.session.commit()
    return redirect(url_for('ecommerce_panel.products_list'))

@staff_required
@mod.route('/products/create/type_<int:pt_id>/', methods=["POST", "GET"])
@login_required
def products_create(pt_id):
    product_type = ProductType.query.filter_by(id=pt_id).first_or_404()
    if request.method == "POST":
        name = request.form.get("name")
        description = request.form.get("description", default="")
        seo_title = request.form.get("seo-title", default="")
        seo_description = request.form.get("seo-description", default="")
        price = request.form.get("price", type=int)
        sku = request.form.get("sku")
        category_id = request.form.get('category_id', type=int)
        publish = request.form.get('publish', type=bool)
        featured = request.form.get('featured', type=bool)
        quantity = request.form.get("quantity", type=int, default=0)
        attributes = {}
        for attr in product_type.product_attributes:
            if request.form.get('attribute-%d' % attr.id):
                attributes[attr.id] = request.form.get('attribute-%d' % attr.id)

        product = Product(
            name=name, description=description,
            seo_title=seo_title, seo_description=seo_description,
            price=price, category_id=category_id, is_published=publish,
            is_featured=featured, attributes=attributes,
            product_type_id=product_type.id
        )
        db.session.add(product)
        db.session.flush()
        if not product_type.has_variants:
            pv = ProductVariant(sku=sku, product_id=product.id, quantity=quantity)
            db.session.add(pv)
        db.session.commit()

        return redirect(url_for('ecommerce_panel.products_list'))
    categories = ProductCategory.query.all()
    return render_template("product/products_form.html",
        categories=categories, product_type=product_type)

@staff_required
@mod.route('/products/types/list/')
@login_required
def products_types_list():
    pts = ProductType.query.all()
    return render_template('product/products_types_list.html', products_types=pts)

@staff_required
@mod.route('/products/types/create/', methods=["POST", "GET"])
@login_required
def products_types_create():
    if request.method == "POST":
        name = request.form.get("name")
        has_variants = request.form.get("has_variants", type=bool)
        product_attributes = request.form.getlist('product_attributes', type=int)
        variant_attributes = request.form.getlist('product_variants', type=int)
        is_shipping_required = request.form.get('is_shipping_required', type=bool)
        is_file_required = request.form.get('is_file_required', type=bool)

        if not name:
            flash(gettext('Name is required'))
            return redirect(url_for('ecommerce_panel.products_types_create'))

        pt = ProductType(name=name, has_variants=has_variants,
                         is_shipping_required=is_shipping_required,
                         is_file_required=is_file_required)
        db.session.add(pt)
        db.session.flush()
        pt.set_attributes(product_attributes)
        if has_variants:
            pt.set_variants(variant_attributes)
        db.session.commit()
        return redirect(url_for('ecommerce_panel.products_types_list'))
    attributes = ProductAttribute.query.all()
    return render_template('product/products_types_form.html', attributes=attributes)

@staff_required
@mod.route('/products/types/edit/<int:pt_id>/', methods=["POST", "GET"])
@login_required
def products_types_edit(pt_id):
    pt = ProductType.query.filter_by(id=pt_id).first()
    if request.method == "POST":
        name = request.form.get("name")
        has_variants = request.form.get("has_variants", type=bool)
        product_attributes = request.form.getlist('product_attributes', type=int)
        variant_attributes = request.form.getlist('product_variants', type=int)
        is_shipping_required = request.form.get('is_shipping_required', type=bool)
        is_file_required = request.form.get('is_file_required', type=bool)
        
        if not name:
            flash(gettext('Name is required'), 'error')
            return redirect(url_for('ecommerce_panel.products_types_create'))

        pt.name = name
        pt.has_variants = has_variants
        pt.is_shipping_required = is_shipping_required
        pt.set_attributes(product_attributes)
        pt.is_file_required = is_file_required
        if has_variants:
            pt.set_variants(variant_attributes)
        db.session.commit()
        return redirect(url_for('ecommerce_panel.products_types_list'))
    attributes = ProductAttribute.query.all()        
    return render_template('product/products_types_form.html',
        product_type=pt, attributes=attributes)

@staff_required
@mod.route('/products/types/delete/<int:pt_id>/')
@login_required
def products_types_delete(pt_id):
    pt = ProductType.query.filter_by(id=pt_id).first_or_404()
    db.session.delete(pt)
    db.session.commit()
    return redirect(url_for('ecommerce_panel.products_types_list'))

@staff_required
@mod.route('/api/products/attributes/')
@login_required
def products_attributes_api():
    pas = ProductAttribute.query.all()
    _type = request.args.get('type')
    product_type_id = request.args.get('product_type_id', type=int)
    if product_type_id and _type:
        results = []
        pt = ProductType.query.filter_by(id=product_type_id).first_or_404()
        for pa in pas:
            _dict = pa.dict()
            if _type == "variant" and pa.id in pt.variant_ids:
                _dict['selected'] = True
            elif _type == "attribute" and pa.id in pt.attr_ids:
                _dict['selected'] = True
            results.append(_dict)
        return jsonify({"results":results})
    else:
        return jsonify({"results":[pa.dict() for pa in pas]})

@staff_required
@mod.route('/products/attributes/list/')
@login_required
def products_attributes_list():
    pas = ProductAttribute.query.all()
    return render_template('product/products_attributes_list.html', attributes=pas)

@staff_required
@mod.route('/products/attributes/create/', methods=["POST", "GET"])
@login_required
def products_attributes_create():
    if request.method == "POST":
        name = request.form.get('name')
        if not name:
            flash(gettext('Name is required'), 'error')
            return redirect(url_for('ecommerce_panel.products_attributes_create'))
        pa = ProductAttribute(name=name)
        db.session.add(pa)
        db.session.commit()
        return redirect(url_for('ecommerce_panel.products_attributes_info',
            attr_id=pa.id))
    return render_template('product/products_attributes_form.html')

@staff_required
@mod.route('/products/attributes/info/<int:attr_id>/')
@login_required
def products_attributes_info(attr_id):
    pa = ProductAttribute.query.filter_by(id=attr_id).first_or_404()
    return render_template('product/products_attributes_info.html', attribute=pa)

@staff_required
@mod.route('/products/attributes/edit/<int:attr_id>/', methods=["POST", "GET"])
@login_required
def products_attributes_edit(attr_id):
    pa = ProductAttribute.query.filter_by(id=attr_id).first_or_404()
    if request.method == "POST":
        name = request.form.get('name')
        if not name:
            flash(gettext('Name is required'), 'error')
            return redirect(url_for('ecommerce_panel.products_attributes_create'))
        pa.name = name
        db.session.commit()
        return redirect(url_for('ecommerce_panel.products_attributes_list'))
    return render_template('product/products_attributes_form.html', attribute=pa)

@staff_required
@mod.route('/products/attributes/delete/<int:attr_id>/')
@login_required
def products_attributes_delete(attr_id):
    pa = ProductAttribute.query.filter_by(id=attr_id).first_or_404()
    db.session.delete(pa)
    db.session.commit()
    return redirect(url_for('ecommerce_panel.products_attributes_list'))

@staff_required
@mod.route('/products/attributes/<int:attr_id>/add_value/', methods=["POST", "GET"])
@login_required
def products_attributes_add_value(attr_id):
    pa = ProductAttribute.query.filter_by(id=attr_id).first_or_404()
    if request.method == "POST":
        name = request.form.get('name')
        if not name:
            flash(gettext('Name is required'), 'error')
            return redirect(url_for('ecommerce_panel.products_attributes_add_value',
                attr_id=attr_id))

        acv = AttributeChoiceValue(name=name, attribute_id=attr_id)
        db.session.add(acv)
        db.session.commit()
        return redirect(url_for('ecommerce_panel.products_attributes_info',
            attr_id=attr_id))
    return render_template('product/products_attributes_add_value_form.html')

@staff_required
@mod.route('/products/attributes/delete_value/<int:val_id>/')
@login_required
def products_attributes_delete_value(val_id):
    pa = AttributeChoiceValue.query.filter_by(id=val_id).first_or_404()
    db.session.delete(pa)
    db.session.commit()
    return redirect(url_for('ecommerce_panel.products_attributes_info',
        attr_id=pa.attribute_id))

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
            flash(gettext("Name is required"), 'error')
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
            flash(gettext("Name is required"), 'error')
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
            flash(gettext("Name is required"), 'error')
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
import math

from flask import request, render_template, redirect, url_for, jsonify
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
    products = query.paginate(page=page, per_page=per_page, error_out=False).items
    products_types = ProductType.query.all()
    return render_template('product/products_list.html',
        products=products, products_types=products_types)

@staff_required
@mod.route('/products/info/<int:product_id>/')
@login_required
def products_info(product_id):
    p = Product.query.filter_by(id=product_id).first_or_404()
    return render_template('product/products_info.html', product=p)

@staff_required
@mod.route('/products/info/<int:product_id>/variants/add/',
    methods=["POST", "GET"])
@login_required
def variants_add():
    pass

@staff_required
@mod.route('/products/info/<int:product_id>/variants/edit/<int:var_id>/',
    methods=["POST", "GET"])
@login_required
def variants_edit(product_id, var_id):
    pass

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
        category_id = request.form.get('category_id')
        publish = request.form.get('publish', type=bool)
        featured = request.form.get('featured', type=bool)
        attributes = []
        for attr in product_type.product_attributes:
            attributes.append(
                {"name":attr.name,
                 "value":request.form.get('attribute-%d' % attr.id)}
            )

        product.name = name
        product.description = description
        product.seo_title = seo_title
        product.seo_description = seo_description
        product.price = price
        product.sku = sku
        product.category_id = category_id
        product.is_published = publish
        product.is_featured = featured
        product.attributes = attributes
        if not product_type.has_variants:
            product.product_variants[0].sku = sku
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
        category_id = request.form.get('category_id')
        publish = request.form.get('publish', type=bool)
        featured = request.form.get('featured', type=bool)
        attributes = []
        for attr in product_type.product_attributes:
            attributes.append(
                {"name":attr.name,
                 "value":request.form.get('attribute-%d' % attr.id)}
            )

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
            pv = ProductVariant(sku=sku, product_id=product.id)
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
        has_variants = request.form.get("has_variants", type=bool, default=True)
        product_attributes = request.form.getlist('product_attributes', type=int)
        product_variants = request.form.getlist('product_variants', type=int)
        is_shipping_required = request.form.get('is_shipping_required',
            type=bool, default=True)

        if not name:
            flash(gettext('Name is required'))
            return redirect(url_for('ecommerce_panel.products_types_create'))

        pt = ProductType(name=name, has_variants=has_variants,
                         is_shipping_required=is_shipping_required)
        db.session.add(pt)
        db.session.flush()
        pt.set_attributes(product_attributes)
        if has_variants:
            pt.set_variants(product_variants)
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
        
        if not name:
            flash(gettext('Name is required'))
            return redirect(url_for('ecommerce_panel.products_types_create'))

        pt.name = name
        pt.has_variants = has_variants
        pt.is_shipping_required = is_shipping_required
        pt.set_attributes(product_attributes)
        if has_variants:
            pt.set_variants(product_variants)
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
            flash(gettext('Name is required'))
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
            flash(gettext('Name is required'))
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
            flash(gettext('Name is required'))
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

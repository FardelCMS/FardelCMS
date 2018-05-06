import pathlib

from flask import Blueprint, url_for
from flask_babel import gettext, pgettext

from .product import views
from fardel.core.panel.sidebar import panel_sidebar, Section, Link, ChildLink

PATH_TO_ECOMMERCE_APP = pathlib.Path(__file__).parent

mod = Blueprint(
    'ecommerce_panel',
    'ecommerce_panel',
    url_prefix="/panel/ecommrece/",
    static_folder=str(PATH_TO_ECOMMERCE_APP / "static"),
    template_folder=str(PATH_TO_ECOMMERCE_APP / "templates"),
)


@mod.before_app_first_request
def add_blog_section():
    section = Section(gettext('Online Shop'))
    product_link = Link('fa fa-product-hunt ', gettext('Products'),
            permission="can_get_products")
    product_link.add_child(ChildLink(gettext("All Products"),
        url_for('ecommerce_panel.products_list'), permission="can_get_products"))
    product_link.add_child(ChildLink(gettext("New Product"),
        url_for('ecommerce_panel.products_list'), permission="can_create_products"))

    product_link.add_child(ChildLink(gettext("All Categories"),
        url_for('ecommerce_panel.categories_list'), permission="can_get_categories"))
    product_link.add_child(ChildLink(gettext("New Category"),
        url_for('ecommerce_panel.categories_create'), permission="can_create_categories"))

    product_link.add_child(ChildLink(gettext("All Product Types"),
        url_for('ecommerce_panel.products_types_list'), permission="can_get_products_types"))
    product_link.add_child(ChildLink(gettext("New Product Type"),
        url_for('ecommerce_panel.products_types_create'), permission="can_create_products_types"))

    section.add_link(product_link)

    discount_link = Link('fa fa-clipboard', gettext('Discounts'),
            permission="can_get_sales")
    discount_link.add_child(ChildLink(pgettext("Discounts section", "All Sales"),
        url_for('ecommerce_panel.categories_list'), permission="can_get_discounts"))
    discount_link.add_child(ChildLink(pgettext("Discounts section", "Create Sales"),
        url_for('ecommerce_panel.categories_create'), permission="can_create_discounts"))

    discount_link.add_child(ChildLink(pgettext("Discounts section", "All Vouchers"),
        url_for('ecommerce_panel.categories_create'), permission="can_get_vouchers"))
    discount_link.add_child(ChildLink(pgettext("Discounts section", "Create Voucher"),
        url_for('ecommerce_panel.categories_create'), permission="can_create_vouchers"))
    section.add_link(discount_link)

    sales_link = Link('fa fa-clipboard', pgettext('Sales sections', 'Sales'),
            permission="can_get_sales")
    sales_link.add_child(ChildLink(pgettext("Sales sections", 'Orders'),
        url_for('ecommerce_panel.categories_list'), permission="can_get_discounts"))
    section.add_link(sales_link)

    panel_sidebar.add_section(section)

import fardel.apps.ecommerce.product.panel
from flask import redirect, url_for, render_template, abort, request, flash
from flask_login import (current_user, login_user,
                         logout_user, login_required, logout_user)
from flask_babel import gettext

from fardel.core.auth.models import User

from .. import mod

from . import auth
from . import media
from . import email

from ..sidebar import panel_sidebar, Section, Link, ChildLink


@mod.before_app_first_request
def add_home_section():
    section = Section('')
    section.add_link(Link('fas fa-home', gettext('home'), url_for('panel.home')))
    panel_sidebar.add_section(section)


@mod.before_app_first_request
def add_auth_section():
    section = Section(gettext("Authentication"))
    link = Link("fas fa-users", gettext("Users"))
    link.add_child(ChildLink(gettext("Users"), url_for('panel.users_list')))
    link.add_child(ChildLink(gettext("Staffmembers"), url_for('panel.staffs_list')))
    section.add_link(link)

    link = Link("fas fa-layer-group", gettext("Groups"), url_for('panel.groups_list'))
    section.add_link(link)
    panel_sidebar.add_section(section)

    section = Section(gettext("Communication"))
    link = Link("fas fa-envelope", gettext("Email"))
    link.add_child(ChildLink(gettext("Send Email"), url_for('panel.email_send')))
    section.add_link(link)

    panel_sidebar.add_section(section)


# @mod.before_app_first_request
# def add_media_section():
# 	section = Section(gettext("Uploads"))
# 	link = Link("fa fa-file", gettext("Files"))
# 	link.add_child(ChildLink(gettext("Files"), "#"))
# 	# link.add_child(ChildLink("آلبوم عکس", "#"))
# 	section.add_link(link)

# 	panel_sidebar.add_section(section)


@mod.route('/login/', methods=['POST', 'GET'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('panel.home'))

    if request.method == "POST":
        email = request.form.get('email')
        password = request.form.get('password')

        u = User.query.filter_by(_email=email).first()
        if u and (u.is_staff or u.is_admin) and u.check_password(password):
            login_user(u)
            return redirect(url_for('panel.home'))
        flash(gettext('Email or password is wrong...'))
    return render_template('login.html')


@mod.route('/logout/')
@login_required
def logout():
    logout_user()
    return redirect('/')


@mod.route('/')
def index():
    if not current_user.is_authenticated:
        abort(404)
    return redirect(url_for('panel.home'))


@mod.route('/home/')
@login_required
def home():
    return render_template('dashboard.html')

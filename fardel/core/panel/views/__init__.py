from flask import redirect, url_for, render_template, abort, request
from flask_login import (current_user, login_user,
	logout_user, login_required, logout_user)

from fardel.core.auth.models import User

from .. import mod

from . import auth
from . import media

from ..sidebar import panel_sidebar, Section, Link, ChildLink


@mod.before_app_first_request
def add_home_section():
	section = Section('')
	section.add_link(Link('fa fa-home', 'خانه', url_for('panel.home')))
	panel_sidebar.add_section(section)


@mod.before_app_first_request
def add_auth_section():
	section = Section("احراز هویت")
	link = Link("fa fa-user", "کاربران")
	link.add_child(ChildLink("کاربران", url_for('panel.users_list')))
	link.add_child(ChildLink("کارمندان", url_for('panel.staffs_list')))
	section.add_link(link)

	link = Link("fa fa-users", "گروه ها", url_for('panel.groups_list'))
	section.add_link(link)
	panel_sidebar.add_section(section)


@mod.route('/login/', methods=['POST', 'GET'])
def login():
	if request.method == "POST":
		email = request.form.get('email')
		password = request.form.get('password')

		u = User.query.filter_by(email=email).first()
		print(u)
		if u and (u.is_staff or u.is_admin) and u.check_password(password):
			login_user(u)
			return redirect(url_for('panel.dashboard'))
		return 'Email or password is wrong...'
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
	return redirect(url_for('panel.dashboard'))

@mod.route('/home/')
@login_required
def home():
	return render_template('dashboard.html')
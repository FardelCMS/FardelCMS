from fardel.app import Fardel
from gettext import lgettext

from fardel.core.forms import BaseForm
from .forms import LoginForm


class AlreadyRegistered(Exception):
    pass


class ModelAdmin:
    fields = []
    excludes = []
    form = None

    def create_form(self):
        class ModelAdminForm(BaseForm):
            pass

        if self.fields:
            for field in self.fields:
                getattr(self.)
                setattr(ModelAdminForm, field, )

        if not self.fields and self.excludes:
            for field in self.excludes:
                pass

        return ModelAdminForm


class RegisteredModel:
    def __init__(self, model, admin_model):
        self.model = model
        self.admin_model = model
        if not self.admin_model.form:
            self.admin_model.form = self.admin_model._create_form()

    def __eq__(self, other):
        return self.model == other.model and self.admin_model == other.admin_model


class AdminSite:
    site_title = lgettext('Fardel site admin')
    site_header = lgettext('Fardel Administration')
    index_title = lgettext('Fardel Administration')

    templates = {
        "login": "login.html",
        "logout": "logout.html",
        "dashboard": "dashboard.html",
        "base": "panel_base.html",
        "sidebar": "panel_sidebar.html"
    }

    login_form = LoginForm

    # password_change_template = None
    # password_change_done_template = None

    def __init__(self, name="admin"):
        self.registered_models = {}
        self.name = name

    def register(self, model, model_admin: ModelAdmin):
        reg_model = RegisteredModel(model, model_admin)
        if reg_model in self.registered_models:
            raise AlreadyRegistered("Model already registered : %s with %s" % (model, model_admin))

        self.registered_models.append(RegisteredModel(model, model_admin))

    def apply_rules(self, app: Fardel):
        for model in self.registered_models:
            pass


site = AdminSite()

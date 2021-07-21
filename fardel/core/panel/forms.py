from fardel.core.forms import BaseForm, StringField, validators


class LoginForm(BaseForm):
    email = StringField("Email", validators=validators.input_required())
    password = StringField("Email", validators=validators.input_required())

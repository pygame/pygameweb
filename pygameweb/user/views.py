from flask import Blueprint, render_template, abort, redirect, url_for, request, Response

from pygameweb.user.models import User, Group
from pygameweb.wiki.forms import WikiForm

user_blueprint = Blueprint('user',
                           __name__,
                           template_folder='../templates/')


# http://flask-sqlalchemy-session.readthedocs.org/en/v1.1/
from flask_sqlalchemy_session import current_session

# https://flask-security-fork.readthedocs.io/en/latest/customizing.html#views
# https://flask-security-fork.readthedocs.io/en/latest/quickstart.html#id1

from flask_security import Security, login_required
from flask_security.utils import get_identity_attributes
from flask_security.datastore import SQLAlchemyDatastore, UserDatastore


# create a SQLAlchemyUserDatastore which doesn't use a flask db session.
# inside create app.
class PretendFlaskSQLAlchemyDb(object):
    """ This is a pretend db object, so we can just pass in a session.
    """
    def __init__(self, session):
        self.session = session

class SQLAlchemyUserDatastore(SQLAlchemyDatastore, UserDatastore):
    """A SQLAlchemy datastore implementation for Flask-Security that assumes the
    use of the Flask-SQLAlchemy extension.
    """
    def __init__(self, db, user_model, role_model):
        SQLAlchemyDatastore.__init__(self, db)
        UserDatastore.__init__(self, user_model, role_model)

    def get_user(self, identifier):
        if self._is_numeric(identifier):
            return self.db.session.query(self.user_model).get(identifier)
        for attr in get_identity_attributes():
            query = getattr(self.user_model, attr).ilike(identifier)
            rv = self.db.session.query(self.user_model).filter(query).first()
            if rv is not None:
                return rv

    def _is_numeric(self, value):
        try:
            int(value)
        except (TypeError, ValueError):
            return False
        return True

    def find_user(self, **kwargs):
        return self.db.session.query(self.user_model).filter_by(**kwargs).first()

    def find_role(self, role):
        return self.db.session.query(self.role_model).filter_by(name=role).first()


class SQLAlchemySessionUserDatastore(SQLAlchemyUserDatastore):
    """A SQLAlchemy datastore implementation for Flask-Security that assumes the
       use of the flask_sqlalchemy_session extension.
    """
    def __init__(self, session, user_model, role_model):
        SQLAlchemyUserDatastore.__init__(self,
                                         PretendFlaskSQLAlchemyDb(session),
                                         user_model,
                                         role_model)


def monkey_patch_email():
    """The email validator in wtforms has issues. So we monkey patch it.
       https://github.com/wtforms/wtforms/pull/294
    """
    import re
    import wtforms.validators
    from wtforms.validators import HostnameValidation, ValidationError

    class Email(object):
        """
        Validates an email address. Note that this uses a very primitive regular
        expression and should only be used in instances where you later verify by
        other means, such as email activation or lookups.
        :param message:
            Error message to raise in case of a validation error.
        """

        user_regex = re.compile(
            r"(^[-!#$%&'*+/=?^_`{}|~0-9A-Z]+(\.[-!#$%&'*+/=?^_`{}|~0-9A-Z]+)*\Z"  # dot-atom
            r'|^"([\001-\010\013\014\016-\037!#-\[\]-\177]|\\[\001-\011\013\014\016-\177])*"\Z)',  # quoted-string
            re.IGNORECASE)

        def __init__(self, message=None):
            self.message = message
            self.validate_hostname = HostnameValidation(
                require_tld=True,
            )

        def __call__(self, form, field):
            value = field.data

            message = self.message
            if message is None:
                message = field.gettext('Invalid email address.')

            if not value or '@' not in value:
                raise ValidationError(message)

            user_part, domain_part = value.rsplit('@', 1)

            if not self.user_regex.match(user_part):
                raise ValidationError(message)

            if not self.validate_hostname(domain_part):
                raise ValidationError(message)
    wtforms.validators.Email = Email


def monkey_patch_email_field(form_class):
    """ We use our monkey patched Email validator, and also a html5 email input.
    """
    from wtforms.fields.html5 import EmailField
    from flask_security.forms import (email_required,
                                      unique_user_email,
                                      get_form_field_label)
    import wtforms.validators
    email_validator = wtforms.validators.Email(message='INVALID_EMAIL_ADDRESS')
    form_class.email = EmailField(get_form_field_label('email'),
                                  validators=[email_required,
                                              email_validator,
                                              unique_user_email])


def add_user_blueprint(app):
    """ to the app.
    """
    app.user_datastore = SQLAlchemySessionUserDatastore(current_session, User, Group)
    monkey_patch_email()

    # https://pythonhosted.org/Flask-Security-Fork/customizing.html
    from flask_security.forms import RegisterForm, ConfirmRegisterForm
    from wtforms.fields import StringField
    from wtforms.validators import Required, Regexp, Length, Email

    username_validators = [
        Required(),
        Regexp('^\w+$',
               message='Username must contain only letters numbers or underscore'),
        Length(min=5,
               max=25,
               message='Username must be betwen 5 & 25 characters')
    ]

    class ExtendedRegisterForm(RegisterForm):
        name = StringField('Username', username_validators)
        title = StringField('Title (eg. Real name)', [Required()])

    class ExtendedConfirmRegisterForm(ConfirmRegisterForm):
        name = StringField('Username', username_validators)
        title = StringField('Title (eg. Real name)', [Required()])

    monkey_patch_email_field(ExtendedRegisterForm)
    monkey_patch_email_field(ExtendedConfirmRegisterForm)

    # https://flask-wtf.readthedocs.io/en/latest/form.html#recaptcha
    # https://github.com/mattupstate/flask-security/issues/404
    # Unfortunately... Google collects private data.
    #     https://www.google.com/about/company/user-consent-policy.html
    # So probably won't use this.
    if app.config.get('SECURITY_RECAPTCHA_ENABLED'):
        class RecaptchaRegister(ExtendedRegisterForm):
            recaptcha = RecaptchaField()
        class RecaptchaConfirmRegister(ExtendedConfirmRegisterForm):
            recaptcha = RecaptchaField()
        register_form = RecaptchaRegister
        confirm_register_form = RecaptchaConfirmRegister
    else:
        register_form = ExtendedRegisterForm
        confirm_register_form = ExtendedConfirmRegisterForm

    security = Security(app,
                        app.user_datastore,
                        register_form=register_form,
                        confirm_register_form=confirm_register_form)

    from pygameweb.cache import limiter
    # login = app.view_functions['security.login']
    # limiter.limit("4/hour")(login)
    limiter.limit("4/hour")(security.app.blueprints['security'])

    # 'security.change_password',
    # 'security.confirm_email',
    # 'security.forgot_password',
    # 'security.login',
    # 'security.logout',
    # 'security.register',
    # 'security.reset_password',
    # 'security.send_confirmation',

    # https://pypi.python.org/pypi/Flask-Gravatar
    from flask_gravatar import Gravatar
    gravatar = Gravatar(app,
                        size=100,
                        rating='g',
                        default='retro',
                        force_default=False,
                        use_ssl=True,
                        base_url=None)

    from flask_security import user_confirmed
    @user_confirmed.connect_via(app)
    def when_the_user_is_confirmed(app, user):
        """ we can add a newbie role.
        """

        # we add a newbie role, once the user confirms their email.
        default_role = app.user_datastore.find_role("newbie")
        app.user_datastore.add_role_to_user(user, default_role)

        # TODO: After a couple of hours we can add a 'member' role.
        #   The idea with this magic spell would be to ward off spam a bit.
        member_role = app.user_datastore.find_role("members")
        app.user_datastore.add_role_to_user(user, member_role)

        current_session.commit()


    app.register_blueprint(user_blueprint)

from flask import Blueprint, request, abort
from flask_sqlalchemy_session import current_session


user_blueprint = Blueprint('user',
                           __name__,
                           template_folder='../templates/')


def monkey_patch_email():
    """The email validator in wtforms has issues. So we monkey patch it.
       https://github.com/wtforms/wtforms/pull/294
    """
    import re
    import wtforms.validators
    from wtforms.validators import HostnameValidation, ValidationError

    class Email(object):
        user_regex = re.compile(
            r"(^[-!#$%&'*+/=?^_`{}|~0-9A-Z]+(\.[-!#$%&'*+/=?^_`{}|~0-9A-Z]+)*\Z"  # dot-atom
            r'|^"([\001-\010\013\014\016-\037!#-\[\]-\177]|\\[\001-\011\013\014\016-\177])*"\Z)',  # quoted-string
            re.IGNORECASE)

        def __init__(self, message=None):
            self.message = message
            self.validate_hostname = HostnameValidation(require_tld=True)

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
    wtforms.validators.email = Email


def monkey_patch_email_field(form_class):
    """ We use our monkey patched Email validator, and also a html5 email input.
    """
    from wtforms.fields.html5 import EmailField
    from flask_security.forms import (email_required,
                                      unique_user_email,
                                      get_form_field_label)
    import wtforms.validators

    from pygameweb.user.rbl import rbl

    def rbl_spamlist_validator(form, field):
        """ If the ip address of the person signing up is listed in a spam list,
            we abort with an error.
        """
        remote_addr = request.remote_addr or None
        if rbl(remote_addr):
            abort(500)

    email_validator = wtforms.validators.Email(message='INVALID_EMAIL_ADDRESS')
    form_class.email = EmailField(get_form_field_label('email'),
                                  validators=[email_required,
                                              email_validator,
                                              rbl_spamlist_validator,
                                              unique_user_email])


def monkey_patch_sqlstore(app):
    """ This adds normal sqlalchemy session support to flask-security.
    """

    from pygameweb.user.models import User, Group

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
                rv = (self.db.session
                      .query(self.user_model).filter(query).first())
                if rv is not None:
                    return rv

        def _is_numeric(self, value):
            try:
                int(value)
            except (TypeError, ValueError):
                return False
            return True

        def find_user(self, **kwargs):
            return (self.db.session
                    .query(self.user_model).filter_by(**kwargs).first())

        def find_role(self, role):
            return (self.db.session
                    .query(self.role_model).filter_by(name=role).first())

    class SQLAlchemySessionUserDatastore(SQLAlchemyUserDatastore):
        """A SQLAlchemy datastore implementation for Flask-Security that assumes the
           use of the flask_sqlalchemy_session extension.
        """

        def __init__(self, session, user_model, role_model):
            SQLAlchemyUserDatastore.__init__(self,
                                             PretendFlaskSQLAlchemyDb(session),
                                             user_model,
                                             role_model)

    app.user_datastore = SQLAlchemySessionUserDatastore(current_session,
                                                        User,
                                                        Group)


def add_user_blueprint(app):
    """ to the app.
    """
    monkey_patch_email()

    # https://pythonhosted.org/Flask-Security-Fork/customizing.html
    from flask_security.forms import RegisterForm, ConfirmRegisterForm, LoginForm
    from wtforms.fields import StringField, BooleanField
    from wtforms.validators import Required, Regexp, Length

    # https://flask-security-fork.readthedocs.io/en/latest/customizing.html#views
    # https://flask-security-fork.readthedocs.io/en/latest/quickstart.html#id1

    from flask_security import Security

    monkey_patch_sqlstore(app)

    def unique_user_name(form, field):
        """ Make sure it is a unique user name.
        """
        from wtforms import ValidationError
        from pygameweb.user.models import User
        user = (current_session
                .query(User).filter(User.name == field.data).first())
        if user is not None:
            msg = f'{field.data} is already associated with an account.'
            raise ValidationError(msg)

    username_msg = 'Username must contain only letters numbers or underscore'
    username_validators = [
        Required(),
        Regexp('^\w+$',
               message=username_msg),
        Length(min=5,
               max=25,
               message='Username must be betwen 5 & 25 characters'),
        unique_user_name,
    ]


    class ExtendedLoginForm(LoginForm):
        remember = BooleanField('Remember Me', default = True)

    class ExtendedRegisterForm(RegisterForm):
        name = StringField('Username', username_validators)
        title = StringField('Title (eg. Real name)', [Required()])

    class ExtendedConfirmRegisterForm(ConfirmRegisterForm):
        name = StringField('Username', username_validators)
        title = StringField('Title (eg. Real name)', [Required()])

    monkey_patch_email_field(ExtendedRegisterForm)
    monkey_patch_email_field(ExtendedConfirmRegisterForm)

    security = Security(app,
                        app.user_datastore,
                        confirm_register_form=ExtendedConfirmRegisterForm,
                        login_form=ExtendedLoginForm,
                        register_form=ExtendedRegisterForm)

    from pygameweb.cache import limiter
    limiter.limit("4/hour")(security.app.blueprints['security'])

    # https://pypi.python.org/pypi/Flask-Gravatar
    from flask_gravatar import Gravatar
    Gravatar(app,
             size=100,
             rating='g',
             default='retro',
             force_default=False,
             use_ssl=True,
             base_url=None)

    # http://flask-security-fork.readthedocs.io/en/latest/api.html#signals
    from flask_security import user_confirmed, user_registered

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

    @user_registered.connect_via(app)
    def when_user_is_registered(app, user, confirm_token):
        """ we log their ip address so as to try and block spammers.
        """
        remote_addr = request.remote_addr or None
        user.registered_ip = remote_addr
        current_session.add(user)
        current_session.commit()

    app.register_blueprint(user_blueprint)

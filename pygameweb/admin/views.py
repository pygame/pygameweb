"""Admin views using flask_admin.
"""

from flask import Flask, render_template
from flask_security import current_user, login_required, Security, utils
from flask_admin import Admin, BaseView, expose, AdminIndexView
from flask_admin.contrib.sqla import ModelView
from wtforms.fields import PasswordField

from pygameweb.user.models import User, Group


class TheAdminIndexView(AdminIndexView):
    def is_accessible(self):
        return current_user.has_role('admin')


class UserAdmin(ModelView):
    column_exclude_list = list = ('password',)
    form_excluded_columns = ('password',)
    column_auto_select_related = True

    def is_accessible(self):
        return current_user.has_role('admin')

    def scaffold_form(self):
        form_class = super(UserAdmin, self).scaffold_form()
        form_class.password2 = PasswordField('New Password')
        return form_class

    def on_model_change(self, form, model, is_created):
        if len(model.password2):
            model.password = utils.encrypt_password(model.password2)


class GroupAdmin(ModelView):
    def is_accessible(self):
        return current_user.has_role('admin')


def add_admin(app):
    """ to the app.
    """
    admin = Admin(app, template_mode='bootstrap3', index_view=TheAdminIndexView())
    admin.add_view(UserAdmin(User, admin.app.scoped_session, endpoint='user_admin'))
    admin.add_view(GroupAdmin(Group, admin.app.scoped_session))

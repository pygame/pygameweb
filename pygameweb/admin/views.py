"""Admin views using flask_admin.
"""

from flask import Flask, render_template
from flask_security import current_user, login_required, Security, utils
from flask_admin import Admin, BaseView, expose, AdminIndexView
from flask_admin.contrib.sqla import ModelView
from wtforms.fields import PasswordField

from pygameweb.user.models import User, Group
from pygameweb.page.models import Page

from pygameweb.news.models import News
from pygameweb.project.models import Project, Release, Tags







class TheAdminIndexView(AdminIndexView):
    def is_accessible(self):
        return current_user.has_role('admin')


class UserAdmin(ModelView):
    column_exclude_list = list = ('password',)
    form_excluded_columns = ('password',)
    column_auto_select_related = True

    # Allow search by name (username), email or title (real name)
    column_searchable_list = ['name', 'email', 'title']

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

class NewsAdmin(ModelView):
    # Don't show the long text fields in the list, but allow a details view
    can_view_details = True
    column_exclude_list = ['description']

    # Allow search by title
    column_searchable_list = ['title']

    def is_accessible(self):
        return current_user.has_role('admin')

class ProjectAdmin(ModelView):
    # Don't show the long text fields in the list, but allow a details view
    can_view_details = True
    column_exclude_list = ['summary', 'description']

    # Allow search by title
    column_searchable_list = ['title']

    def is_accessible(self):
        return current_user.has_role('admin')

    def on_model_delete(self, project):
        # Delete associated tags and releases so we can delete the project.
        p = project
        self.session.query(Tags).filter(Tags.project_id == p.id).delete()
        self.session.query(Release).filter(Release.project_id == p.id).delete()

class ReleaseAdmin(ModelView):
    # Don't show the long text fields in the list, but allow a details view
    can_view_details = True
    column_exclude_list = ['description']

    def is_accessible(self):
        return current_user.has_role('admin')

class PageAdmin(ModelView):
    # Don't show the long text fields in the list, but allow a details view
    can_view_details = True
    column_exclude_list = ['content']

    # Allow search by title and name
    column_searchable_list = ['name', 'title']

    def is_accessible(self):
        return current_user.has_role('admin')


def add_admin(app):
    """ to the app.
    """
    admin = Admin(app, template_mode='bootstrap3', index_view=TheAdminIndexView())
    admin.add_view(UserAdmin(User, admin.app.scoped_session, endpoint='user_admin'))
    admin.add_view(GroupAdmin(Group, admin.app.scoped_session, endpoint='group_admin'))
    admin.add_view(NewsAdmin(News, admin.app.scoped_session, endpoint='news_admin'))
    admin.add_view(ProjectAdmin(Project, admin.app.scoped_session, endpoint='project_admin'))
    admin.add_view(ReleaseAdmin(Release, admin.app.scoped_session, endpoint='release_admin'))
    admin.add_view(PageAdmin(Page, admin.app.scoped_session, endpoint='page_admin'))

from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed, FileRequired

from wtforms.fields import StringField, HiddenField
from wtforms.fields.html5 import URLField
from wtforms.validators import DataRequired, Required, URL
from wtforms.widgets import TextArea


class ProjectForm(FlaskForm):
    title = StringField('Title', validators=[Required()])
    tags = StringField('Tags')
    summary = StringField('Summary', widget=TextArea(), validators=[Required()])
    description = StringField('Description', widget=TextArea())
    uri = URLField('Home URL', validators=[Required()])

    image = FileField('image', validators=[
        # FileRequired(),
        FileAllowed(['jpg', 'png'], 'Images only!')
    ])
    github_repo = URLField('Github repository URL', validators=[])
    youtube_trailer = URLField('Youtube trailer URL', validators=[])
    patreon = URLField('Patreon URL', validators=[])


class ReleaseForm(FlaskForm):
    version = StringField('version', validators=[Required()])
    description = StringField('description', widget=TextArea())
    srcuri = URLField('Source URL')
    winuri = URLField('Windows URL')
    macuri = URLField('Mac URL')


class FirstReleaseForm(ProjectForm, ReleaseForm):
    """Is for when the first release is being made.
    """


class ProjectCommentForm(FlaskForm):
    """ is for commenting on projects.
    """
    message = StringField('message', widget=TextArea(), validators=[Required()])
    parent_id = HiddenField('parent_id')
    thread_id = HiddenField('thread_id')

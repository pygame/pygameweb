from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed, FileRequired

from wtforms.fields import TextField, HiddenField, TextAreaField
from wtforms.fields.html5 import URLField
from wtforms.validators import DataRequired, Required, Length
from wtforms.widgets import TextArea


class NewsForm(FlaskForm):
    title = TextField('Title', validators=[Required()])
    description = TextAreaField('Description', validators=[Required()])
    summary = TextField('Summary', validators=[Required(), Length(min=6, max=140)])

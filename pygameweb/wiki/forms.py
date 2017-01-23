from flask_wtf import FlaskForm
from flask_wtf.file import StringField, HiddenField
from wtforms.validators import DataRequired


class WikiEditForm(FlaskForm):
    content = StringField('content')
    changes = StringField('changes')
    link = HiddenField('link')

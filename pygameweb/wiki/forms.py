from flask_wtf import FlaskForm
from wtforms.fields import StringField, HiddenField
from wtforms.validators import DataRequired
from wtforms.widgets import TextArea


class WikiForm(FlaskForm):
    content = StringField('content', widget=TextArea())
    changes = StringField('changes')
    link = HiddenField('link')

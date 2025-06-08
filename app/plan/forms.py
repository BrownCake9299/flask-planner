from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, IntegerField
from wtforms.fields.simple import TextAreaField
from wtforms.validators import DataRequired, Length, NumberRange, Optional

class EventForm(FlaskForm):
    name = StringField('Event', validators=[DataRequired(), Length(min=1, max=64)])
    description = TextAreaField('Description')
    submit = SubmitField('Submit')
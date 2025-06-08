from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, IntegerField
from wtforms.fields.simple import TextAreaField
from wtforms.validators import DataRequired, Length, NumberRange, Optional

class NameForm(FlaskForm):
    name = StringField('What is your name?', validators=[DataRequired()])
    submit = SubmitField('Submit')

class EditProfileForm(FlaskForm):
    name = StringField('Real name', validators=[Length(0, 64)])
    location = StringField('Location', validators=[Length(0, 64)])
    about_me = TextAreaField('About me')
    sleep_time = IntegerField('Sleeping time', validators=[NumberRange(0, 23), Optional()])
    wake_time = IntegerField('Waking time', validators=[NumberRange(0, 23), Optional()])
    submit = SubmitField('Submit')
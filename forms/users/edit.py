from flask_wtf import FlaskForm
from wtforms import PasswordField, SubmitField, EmailField, BooleanField, StringField, FileField
from wtforms.validators import DataRequired


class EditForm(FlaskForm):
    surname = StringField('Фамилия:', validators=[DataRequired()])
    name = StringField('Имя:', validators=[DataRequired()])
    
    submit = SubmitField('Редактировать')
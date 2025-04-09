from flask_wtf import FlaskForm
from wtforms import PasswordField, StringField, TextAreaField, SubmitField, EmailField, IntegerField
from wtforms.validators import DataRequired


class RegisterFormFinal(FlaskForm):
    code = StringField('Код:', validators=[DataRequired()])
    submit = SubmitField('Подтвердить')

from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, IntegerField, RadioField, DateField
from wtforms.validators import DataRequired, NumberRange


class RegisterFormFirst(FlaskForm):
    surname = StringField('Фамилия:', validators=[DataRequired()])
    name = StringField('Имя:', validators=[DataRequired()])
    date_of_birth = DateField('Дата рождения:', validators=[DataRequired()])
    gender = RadioField('Пол:', choices=[('man','Мужчина'), ('woman','Женщина')], default='man')
    submit = SubmitField('Далее')

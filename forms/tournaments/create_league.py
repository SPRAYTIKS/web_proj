from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, IntegerField, RadioField, DateField, BooleanField
from wtforms.validators import DataRequired, NumberRange


class CreateLeagueForm(FlaskForm):
    level = RadioField('Уровень лиги:', choices=[('A', 'A'), ('B', 'B'), ('C', 'C')], default='A')
    type = RadioField('Тип лиги:', choices=[('ММ', 'ММ'), ('ЖЖ', 'ЖЖ'), ('МЖ', 'МЖ')], default='ММ')

    team_quantity = IntegerField('Количество команд:', validators=[DataRequired(), NumberRange(min=3, max=30)],
                            default=3)

    submit = SubmitField('Создать')
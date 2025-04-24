from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, IntegerField, RadioField, DateField, BooleanField
from wtforms.validators import DataRequired, NumberRange


class CreateTournamentForm(FlaskForm):
    name = StringField('Название турнира:', validators=[DataRequired()])
    type = RadioField('Тип турнира:', choices=[('zs', 'Золотая серия'), ('lm', 'Лайты/Медиум')], default='zs')
    quantity = IntegerField('Количество лиг:', validators=[DataRequired(), NumberRange(min=1, max=10)],
                            default=1)

    start_registration = DateField('Старт регистрации:', validators=[DataRequired()])
    end_registration = DateField('Завершение регистрации:', validators=[DataRequired()])
    start_tournament = DateField('Начало турнира:', validators=[DataRequired()])
    end_tournament = DateField('Конец турнира:', validators=[DataRequired()])

    is_visible = BooleanField('Видно турнир')
    is_register = BooleanField('Начать регистрацию')

    submit = SubmitField('Создать')

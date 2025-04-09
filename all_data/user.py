from contextlib import nullcontext
from email.policy import default
import sqlalchemy
from sqlalchemy import orm
from .db_session import SqlAlchemyBase
from werkzeug.security import generate_password_hash, check_password_hash
import datetime as dt
from flask_login import UserMixin


class User(SqlAlchemyBase, UserMixin):
    __tablename__ = 'users'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True,
                           autoincrement=True)
    surname = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    name = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    date_of_birth = sqlalchemy.Column(sqlalchemy.Date, nullable=False)
    gender = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    email = sqlalchemy.Column(sqlalchemy.String, index=True, nullable=False, unique=True)
    status = sqlalchemy.Column(sqlalchemy.String, default='default_user')
    hashed_password = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    register_date = sqlalchemy.Column(sqlalchemy.DateTime, default=dt.datetime.now)

    tournament = orm.relationship('Tournament', back_populates='user')

    def set_password(self, password):
        self.hashed_password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.hashed_password, password)

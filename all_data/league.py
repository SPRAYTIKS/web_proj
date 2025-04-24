from email.policy import default

import sqlalchemy
from sqlalchemy import orm
from .db_session import SqlAlchemyBase
from sqlalchemy_serializer import SerializerMixin


class League(SqlAlchemyBase, SerializerMixin):
    __tablename__ = 'leagues'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True,
                           autoincrement=True)
    is_tournament = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey('tournaments.id'), nullable=False)
    level = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    type = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    players = sqlalchemy.Column(sqlalchemy.String)
    team = sqlalchemy.Column(sqlalchemy.String)
    team_quantity = sqlalchemy.Column(sqlalchemy.Integer, nullable=False)
    is_finished = sqlalchemy.Column(sqlalchemy.Boolean, default=False)

    tournament = orm.relationship('Tournament')
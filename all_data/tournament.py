import sqlalchemy
from sqlalchemy import orm
from .db_session import SqlAlchemyBase
from sqlalchemy_serializer import SerializerMixin


class Tournament(SqlAlchemyBase, SerializerMixin):
    __tablename__ = 'tournaments'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True,
                           autoincrement=True)
    creator_tournament = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey('users.id'), nullable=False)
    name_tournament = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    type = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    players = sqlalchemy.Column(sqlalchemy.String)
    team = sqlalchemy.Column(sqlalchemy.String)
    league_group_quantity = sqlalchemy.Column(sqlalchemy.Integer, nullable=False)
    start_registration = sqlalchemy.Column(sqlalchemy.Date, nullable=False)
    end_registration = sqlalchemy.Column(sqlalchemy.Date, nullable=False)
    start_tournament = sqlalchemy.Column(sqlalchemy.Date, nullable=False)
    end_tournament = sqlalchemy.Column(sqlalchemy.Date, nullable=False)
    is_visible = sqlalchemy.Column(sqlalchemy.Boolean, default=False)
    is_finished = sqlalchemy.Column(sqlalchemy.Boolean, default=False)
    is_register = sqlalchemy.Column(sqlalchemy.Boolean, default=False)
    is_started = sqlalchemy.Column(sqlalchemy.Boolean, default=False)

    user = orm.relationship('User')
    league = orm.relationship('League', back_populates='tournament')
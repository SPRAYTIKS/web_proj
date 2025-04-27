import sqlalchemy
from sqlalchemy import orm
from .db_session import SqlAlchemyBase
from sqlalchemy_serializer import SerializerMixin


class GroupLeague(SqlAlchemyBase, SerializerMixin):
    __tablename__ = 'groupsLeague'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True,
                           autoincrement=True)
    is_league = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey('leagues.id'), nullable=False)
    name = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    players = sqlalchemy.Column(sqlalchemy.String)
    team = sqlalchemy.Column(sqlalchemy.String)
    players_quantity = sqlalchemy.Column(sqlalchemy.Integer, nullable=False)
    is_finished = sqlalchemy.Column(sqlalchemy.Boolean, default=False)

    tournament = orm.relationship('League')
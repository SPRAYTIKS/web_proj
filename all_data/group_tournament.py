import sqlalchemy
from sqlalchemy import orm
from .db_session import SqlAlchemyBase
from sqlalchemy_serializer import SerializerMixin


class GroupTournament(SqlAlchemyBase, SerializerMixin):
    __tablename__ = 'groupsTournament'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True,
                           autoincrement=True)
    is_tournament = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey('tournaments.id'), nullable=False)
    name = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    players = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    players_quantity = sqlalchemy.Column(sqlalchemy.Integer, nullable=False)
    is_finished = sqlalchemy.Column(sqlalchemy.Boolean)

    tournament = orm.relationship('Tournament')
import sqlalchemy
import sqlalchemy.schema
import sqlalchemy.orm
import sqlalchemy.orm.session
import sqlalchemy.ext.declarative

import database_config


Base = sqlalchemy.ext.declarative.declarative_base()
session = sqlalchemy.orm.session.Session()


class User(Base):
    __tablename__ = 'users'
    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
    name = sqlalchemy.Column(sqlalchemy.String(32), unique=True)


class Pattern(Base):
    __tablename__ = 'patterns'
    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
    user_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey('users.id'))
    user = sqlalchemy.orm.relationship('User', backref=sqlalchemy.orm.backref('patterns'))
    pattern = sqlalchemy.Column(sqlalchemy.String(64))
    __table_args__ = (sqlalchemy.schema.UniqueConstraint('user_id', 'pattern'),)


class Welcome(Base):
    __tablename__ = 'welcomes'
    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
    user_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey('users.id'))
    user = sqlalchemy.orm.relationship('User', backref=sqlalchemy.orm.backref('welcomes'))
    welcome = sqlalchemy.Column(sqlalchemy.String(128))
    __table_args__ = (sqlalchemy.schema.UniqueConstraint('user_id', 'welcome'),)


class Seen(Base):
    __tablename__ = 'seen'
    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
    time = sqlalchemy.Column(sqlalchemy.DateTime)
    nick = sqlalchemy.Column(sqlalchemy.String(32), unique=True)
    reason = sqlalchemy.Column(sqlalchemy.Enum('quit', 'part', 'kick', 'nick'), name='seen_reasons')
    args = sqlalchemy.Column(sqlalchemy.String(64))


def initialize():
    global session
    engine = sqlalchemy.create_engine(database_config.connection_string)
    _session = sqlalchemy.orm.sessionmaker(bind=engine)
    session = _session()
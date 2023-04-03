from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from sqlalchemy.sql.expression import text
from sqlalchemy.sql.sqltypes import TIMESTAMP
from sqlalchemy.orm import relationship
from .database import Base


# need to use alembic for updating.
class Post(Base):
    # if changes are made here, it won't update the postgreSQL db.
    # without alembic you have to delete the table and re-create it.
    __tablename__ = "posts"

    id = Column(Integer, primary_key=True, nullable=False)
    title = Column(String, nullable=False)
    content = Column(String, nullable=False)
    published = Column(Boolean, server_default='True', nullable=False)
    created_at = Column(
        TIMESTAMP(timezone=True),
        server_default=text('now()'),
        nullable=False)
    owner_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False)

    owner = relationship("User")


'''
   This class is from 'sqlalchemy' and defines what the columns should be
   in our postgreSQL database. used to help with our CRUD operations
   to our database.
'''


class User(Base):
    # if changes are made here, it won't update the postgreSQL db.
    # without alembic you have to delete the table and re-create it.
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, nullable=False)
    email = Column(String, nullable=False, unique=True)
    password = Column(String, nullable=False)
    created_at = Column(
        TIMESTAMP(timezone=True),
        server_default=text('now()'),
        nullable=False)


class Votes(Base):

    __tablename__ = 'votes'
    user_id = Column(Integer, ForeignKey('users.id', ondelete="CASCADE"), primary_key=True)
    post_id = Column(Integer, ForeignKey('posts.id', ondelete="CASCADE"), primary_key=True)

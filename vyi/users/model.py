from sqlalchemy import Column, String
from vyi.model import Base


class User(Base):

    __tablename__ = 'users'

    id = Column('id', String, primary_key=True)
    nickname = Column('nickname', String, primary_key=True)

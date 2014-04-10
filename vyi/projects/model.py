from sqlalchemy import Column, Integer, String
from vyi.model import Base, genuuid


class Vote(Base):

    __tablename__ = 'votes'

    id = Column('id', String, default=genuuid, primary_key=True)
    up = Column('up', Integer, default=0)
    down = Column('down', Integer, default=0)


class Project(Base):

    __tablename__ = 'projects'

    id = Column('id', String, default=genuuid, primary_key=True)
    initiator_id = Column('initiator_id', String, primary_key=True)
    vote_id = Column('vote_id', String, primary_key=True)
    name = Column('name', String)
    description = Column('description', String, default=None)

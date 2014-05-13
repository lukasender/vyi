from sqlalchemy import Column, String
from crate.client.sqlalchemy.types import Object
from vyi.app.model import Base, genuuid


class Project(Base):

    __tablename__ = 'projects'

    id = Column('id', String, default=genuuid, primary_key=True)
    initiator_id = Column('initiator_id', String, primary_key=True)
    name = Column('name', String)
    description = Column('description', String, default=None)
    votes = Column('votes', Object) # {'up': 0, 'down': 0}

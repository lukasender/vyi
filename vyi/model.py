from sqlalchemy.orm import scoped_session
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from zope.sqlalchemy import ZopeTransactionExtension
from functools import wraps
import uuid
from hashlib import sha1

DB_SESSION = scoped_session(sessionmaker(extension=ZopeTransactionExtension()))
Base = declarative_base()

REFRESH_TABLES = ['projects', 'users', 'votes']


def genuuid():
    return str(uuid.uuid4())


def genid(str):
    """ generate a deterministic id for 'str' """
    if isinstance(str, unicode):
        str_8bit = str.encode('UTF-8')
    else:
        str_8bit = str
    return sha1('salt' + str_8bit).hexdigest()


def refresh_tables():
    """Refresh all tables"""
    DB_SESSION.flush()
    connection = Base.metadata.bind.raw_connection().connection.cursor()
    for table in REFRESH_TABLES:
        connection.execute("REFRESH TABLE " + table)


def refresher(function):
    @wraps(function)
    def wrapper(*args, **kwargs):
        """ wrapper function """
        result = function(*args, **kwargs)
        refresh_tables()
        return result
    return wrapper

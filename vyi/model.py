from sqlalchemy.orm import scoped_session
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from zope.sqlalchemy import ZopeTransactionExtension
from functools import wraps
import uuid
from hashlib import sha1

from crate.client import connect


class CrateConnection(object):

    def __init__(self):
        self.connection = None

    def __call__(self):
        return self.connection

    def configure(self, hosts):
        self.connection = connect(hosts)
        return self.connection


DB_SESSION = scoped_session(sessionmaker(extension=ZopeTransactionExtension()))
CRATE_CONNECTION = CrateConnection()
Base = declarative_base()


REFRESH_TABLES = ['projects', 'users']


def genuuid():
    return str(uuid.uuid4())


def genid(s):
    """ generate a deterministic id for 's' """
    if isinstance(s, unicode):
        str_8bit = s.encode('UTF-8')
    else:
        str_8bit = s
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

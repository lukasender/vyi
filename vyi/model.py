"""
Database cluster representation
"""

class DB(object):
    """ representation of the DB cluster """

    def __init__(self):
        self.connection = None

    def configure(self, connection):
        """ configure the connection """
        self.connection = connection

    def client(self):
        """ returns the client of a connection """
        return self.connection.client

    def cursor(self):
        """ returns the cursor of a connection """
        return self.connection.cursor

    def execute(self, statement):
        """ executes a SQL statement and returns a cursor """
        return self.cursor().execute(statement)

    def close(self):
        """ closes the cursor and connection """
        self.cursor().close()
        self.connection.close()


DB = DB()

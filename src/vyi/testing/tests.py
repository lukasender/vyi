import unittest
import doctest
import os

from crate.testing.layer import CrateLayer
from crate.client import connect

from pyramid import paster

from webtest import TestApp

here = os.path.dirname(__file__)

conf = os.path.join(here, 'testing.ini')

default_app = None
app = None

crate_port = 44209
crate_transport_port = 44309
crate_host = "127.0.0.1:{port}".format(port=crate_port)


def docs_path(*parts):
    return os.path.join(os.path.dirname(os.path.dirname(__file__)), *parts)


def crate_path(*parts):
    return docs_path('..', '..', 'parts', 'crate', *parts)


crate_layer = CrateLayer('crate',
                         crate_home=crate_path(),
                         crate_exec=crate_path('bin', 'crate'),
                         port=crate_port,
                         transport_port=crate_transport_port)


def get_app():
    global default_app, app
    if default_app is None:
        default_app = paster.get_app(conf, 'main')
    app = default_app
    return app


def setUp(test, app_func=get_app):
    t_app = app_func()
    test_app = TestApp(t_app)
    test.globs['crate_path'] = crate_path
    test.globs['app'] = test_app


def setUpVyiTransactions(test):
    setUp(test)
    test.globs['crate_host'] = crate_host
    conn = connect(crate_host)
    cursor = conn.cursor()

    def refresh(table):
        cursor.execute("refresh table %s" % table)
    test.globs["refresh"] = refresh
    test.globs["cursor"] = cursor

    mappings = [
        '../../etc/mappings/users.sql',
        '../../etc/mappings/projects.sql',
        '../../etc/mappings/stats.sql',
        '../../etc/mappings/transactions.sql',
    ]

    for mapping in mappings:
        with open(docs_path(mapping)) as m:
            stmt = m.read()
            cursor.execute(stmt)


def tearDownVyiTransactions(test):
    conn = connect(crate_host)
    cursor = conn.cursor()
    cursor.execute("drop table users")
    cursor.execute("drop table projects")
    cursor.execute("drop table stats")
    cursor.execute("drop table transactions")


def test_suite():
    suite = unittest.TestSuite()

    s = doctest.DocFileSuite(
        '../../../docs/transactions.txt',
        setUp=setUpVyiTransactions,
        tearDown=tearDownVyiTransactions,
        optionflags=doctest.NORMALIZE_WHITESPACE | doctest.ELLIPSIS
    )
    s.layer = crate_layer
    suite.addTest(s)

    return suite

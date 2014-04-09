from crate import client
from pyramid.settings import aslist
from pyramid.config import Configurator

from .model import DB

def app_factory(global_config, **settings):
    """Setup the main application for paste

    This must be setup as the paste.app_factory in the egg entry-points.
    """
    config = Configurator(settings=settings,
                          # autocommit=True,
                          # authentication_policy=AuthTktAuthenticationPolicy(
                          #                       'str_token')
                          )
    config.include('vyi.probestatus.probestatus')
    config.scan('vyi.probestatus')
    crate_init(config)

    return config.make_wsgi_app()


def crate_init(config):
    """ returns the crate connection """
    settings = config.get_settings()
    crate_instances = aslist(settings['crate.hosts'])
    connection = client.connect(crate_instances)
    DB.configure(connection)
    print 'active connections:'
    print DB.client()._active_servers

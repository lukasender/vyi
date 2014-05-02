from pyramid.settings import aslist, asbool
from pyramid.config import Configurator
from sqlalchemy import create_engine

from .model import DB_SESSION, Base, CRATE_CONNECTION


def app_factory(global_config, **settings):
    """Setup the main application for paste

    This must be setup as the paste.app_factory in the egg entry-points.
    """
    config = Configurator(settings=settings,
                          autocommit=True,
                          )
    config.include('vyi.probestatus.probestatus')
    config.scan('vyi.probestatus')
    config.include('vyi.users.service')
    config.scan('vyi.users')
    config.include('vyi.projects.service')
    config.scan('vyi.projects')
    config.include('vyi.stats.service')
    config.scan('vyi.stats')
    crate_init(config)
    return config.make_wsgi_app()


def crate_init(config):
    settings = config.get_settings()
    engine = create_engine(
        'crate://',
        connect_args={
            'servers': aslist(settings['crate.hosts'])
        },
        echo=asbool(settings.get('crate.echo', 'False')),
        pool_size=int(settings.get('sql.pool_size', 5)),
        max_overflow=int(settings.get('sql.max_overflow', 5))
    )
    DB_SESSION.configure(bind=engine)
    Base.metadata.bind = engine
    CRATE_CONNECTION.configure(aslist(settings['crate.hosts']))

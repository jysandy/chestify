import os

from pyramid.authentication import AuthTktAuthenticationPolicy
from pyramid.authorization import ACLAuthorizationPolicy
from pyramid.config import Configurator
from pyramid.session import SignedCookieSessionFactory
import sqlalchemy

from .security import principal_callback
from .models import DBSession, Base


def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application.
    """
    config = Configurator(settings=settings)
    config.include('pyramid_chameleon')

    #adding session factory
    chestify_session_factory = SignedCookieSessionFactory(settings.get('chestify.secret'))
    config.set_session_factory(chestify_session_factory)

    # Database connection
    def read_local_db_creds():
        if os.path.isfile('creds.txt'):
            with open('creds.txt') as inf:
                return tuple(inf.read().split('\n')[:2])
        else:
            return None, None

    local_uname, local_pwd = read_local_db_creds()
    username = os.environ.get('CHESTIFY_DB_USER', local_uname)
    password = os.environ.get('CHESTIFY_DB_PASSWORD', local_pwd)
    host = os.environ.get('OPENSHIFT_POSTGRESQL_DB_HOST', '127.0.0.1')
    port = os.environ.get('OPENSHIFT_POSTGRESQL_PORT', '5432')
    database = 'chestify'
    connect_url = sqlalchemy.engine.url.URL(username=username, password=password,
                    host=host, port=port, database=database, drivername='postgresql')

    engine = sqlalchemy.create_engine(connect_url)
    DBSession.configure(bind=engine)
    Base.metadata.bind = engine
    Base.metadata.create_all()

    # Security policies
    secret_key = os.environ.get('CHESTIFY_SECRET_KEY', settings.get('chestify.secret'))
    authn_policy = AuthTktAuthenticationPolicy(
        secret_key, callback=principal_callback,
        hashalg='sha512')
    authz_policy = ACLAuthorizationPolicy()
    config.set_authentication_policy(authn_policy)
    config.set_authorization_policy(authz_policy)

    # Routes
    config.add_static_view('static', 'static', cache_max_age=3600)
    config.add_route('home', '/')
    config.add_route('list', '/list')
    config.add_route('download-url', '/download-url')
    config.add_route('upload-url', '/upload-url')
    config.add_route('create-dir', '/makedir')
    config.add_route('generate-shared', '/generate-shared')
    config.add_route('shared-download', '/shared')
    config.add_route('login', '/login')
    config.add_route('logout', '/logout')
    config.add_route('auth_test', '/auth')
    config.add_route('database_test','/dbtest')
    config.add_route('json_test','/json_test')
    config.scan()
    return config.make_wsgi_app()

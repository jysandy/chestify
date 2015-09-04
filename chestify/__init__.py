import os

from pyramid.authentication import AuthTktAuthenticationPolicy
from pyramid.authorization import ACLAuthorizationPolicy
from pyramid.config import Configurator
import sqlalchemy

from .security import principal_callback
from .models import DBSession, Base

#TODO: Make this properly secure
DEVEL_SECRET_KEY = 'huehuehuehuehue'

def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application.
    """
    config = Configurator(settings=settings, root_factory='.resources.Root')
    config.include('pyramid_chameleon')

    #TODO: Create the SQLALchemy engine here
    username = os.environ.get('CHESTIFY_DB_USER')
    password = os.environ.get('CHESTIFY_DB_PASSWORD')
    host = os.environ.get('OPENSHIFT_POSTGRESQL_DB_HOST')
    port = os.environ.get('OPENSHIFT_POSTGRESQL_PORT')
    database = 'chestify'
    connect_url = sqlalchemy.engine.url.URL(username=username, password=password,
                    host=host, port=port, database=database, drivername='postgresql')
    if host is not None:
        #If we are on Openshift
        engine = sqlalchemy.create_engine(connect_url)
        DBSession.configure(bind=engine)
        Base.metadata.bind = engine
        Base.metadata.create_all()

    secret_key = os.environ.get('CHESTIFY_SECRET_KEY', settings['chestify.secret'])
	# Security policies
    authn_policy = AuthTktAuthenticationPolicy(
        secret_key, callback=principal_callback,
        hashalg='sha512')
    authz_policy = ACLAuthorizationPolicy()
    config.set_authentication_policy(authn_policy)
    config.set_authorization_policy(authz_policy)

    #Routes
    config.add_static_view('static', 'static', cache_max_age=3600)
    config.add_route('home', '/')
    config.add_route('list', '/{user_id}/list')
    config.add_route('download-url', '/{user_id}/download-url')
    config.add_route('upload-url', '/{user_id}/upload-url')
    config.add_route('generate-shared', '/{user_id}/generate-shared')
    config.scan()
    return config.make_wsgi_app()

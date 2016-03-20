from pyramid.paster import get_app, setup_logging
import os

repo_folder = os.environ.get('OPENSHIFT_REPO_DIR', os.path.dirname(__file__))

ini_path = os.path.join(repo_folder, 'production.ini')
setup_logging(ini_path)
application = get_app(ini_path, 'main')
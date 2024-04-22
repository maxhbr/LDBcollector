import os
from pyramid.paster import get_app, setup_logging

try:
    import mod_wsgi
    environment = mod_wsgi.process_group.split('-')[-1]
except ImportError:
    environment = os.environ.get('PASTE_INI', 'production')

conf_file = os.path.join(os.path.dirname(__file__), environment + '.ini')

setup_logging(conf_file)
application = get_app(conf_file)

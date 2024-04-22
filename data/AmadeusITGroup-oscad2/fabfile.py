from fabric.api import run, env, path, cd, put, local
from fabric.colors import green
import os

env.use_ssh_config = True

HERE = os.path.dirname(__file__)
BASE_DIR = '/var/www/oscad'

import logging
logging.basicConfig()


def pack():
    # create a new source distribution as tarball
    local('python setup.py sdist --formats=gztar', capture=False)


def _dist():
    return local('python setup.py --fullname', capture=True).strip()


def mkvirtualenv(dir):
    try:
        run('rm -r ' + dir)
    except:
        pass
    run('virtualenv --setuptools -p /usr/bin/python2 ' + dir)


def print_modwsgi_info(basedir):
    print(green("""
To use this deployment add the following to your apache configuration:

    WSGIDaemonProcess oscad python-path={0}/venv/lib/python2.7/site-packages
    WSGIScriptAlias /oscad {0}/wsgi.py
    <Location /oscad>
      WSGIProcessGroup oscad
    </Location>
    """.format(basedir)))


def deploy(directory=BASE_DIR):
    dist_file = '{}.tar.gz'.format(_dist())
    dist = 'dist/' + dist_file

    with cd(directory):
        mkvirtualenv(directory + '/venv')

        put(dist, '.')
        put('wsgi.py', '.')
        put('requirements.txt', '.')

        with path('venv/bin', 'prepend'):

            run('pip install --download-cache=cache -r requirements.txt')
            run('pip install --download-cache=cache  ' + dist_file)

        # run('rm ' + dist_file)

    print_modwsgi_info(directory)

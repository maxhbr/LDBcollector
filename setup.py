# coding=utf-8

from setuptools import setup
from setuptools.command.test import test as TestCommand
from sys import version_info, exit

import os.path
import re

PY2 = version_info[0] == 2
PY26 = PY2 and version_info[1] == 6


class PyTest(TestCommand):
    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = []
        self.test_suite = True

    def run_tests(self):
        #import here, cause outside the eggs aren't loaded
        import pytest
        errno = pytest.main(self.test_args)
        exit(errno)


def get_version():
    here = os.path.dirname(__file__)
    version_file = os.path.join(here, 'oscad', 'version.py')

    with open(version_file, 'r') as f:
        matches = re.search("__version__ = '([^']+)'", f.read())
        return matches.group(1)


requires = [
    'pyramid_jinja2',
    'pyramid',
    'PyYAML',
    'pyScss',
    'markupsafe',
    'Babel',
    ]

extras_require = {
    'dev': [
        'pyramid_debugtoolbar',
        'flake8',
    ],
    'serve': [
        'waitress',
    ],
    'translate': [
        'translate-toolkit',
    ]
}

tests_require = [
    'pytest',
    'webtest',
    'beautifulsoup4',
    'requests',
]

if PY2:
    extras_require['dev'].append('lingua')

if PY26:
    requires.append('ordereddict')
    tests_require.append('lxml')

setup(name='oscad',
      version=get_version(),
      description='oscad',
      classifiers=[
           "Programming Language :: Python",
           "Framework :: Pyramid",
           "Topic :: Internet :: WWW/HTTP",
           "Topic :: Internet :: WWW/HTTP :: WSGI :: Application",
      ],
      author='Thomas Wei\xc3\x9fschuh, Amadeus IT Group',
      author_email='thomas.weissschuh@de.amadeus.com',
      url='https://github.com/dtag-dbu/oscad',
      keywords='web pyramid pylons',
      packages=[
          'oscad',
          'oscad_data',
          'oscad_i18n',
          'oscad_theme_basic',
          'oscad_theme_amadeus',
      ],
      package_data={
          '': [
              'static/bootstrap/js/*.js',
              'static/bootstrap/fonts/*.eot',
              'static/bootstrap/fonts/*.svg',
              'static/bootstrap/fonts/*.ttf',
              'static/bootstrap/fonts/*.woff',
              'static/jquery/*.js',
              'static/img/*.png',
              'static/img/*.svg',
              'static/agpl-3.0.txt',
              'assets/scss/*.scss',
              'assets/scss/bootstrap/*.scss',
              'templates/*.jinja2',
              'templates/*/*.jinja2',
              'locale/*.pot',
              'locale/*/LC_MESSAGES/*.po',
              'locale/*/LC_MESSAGES/*.mo',
          ],
          'oscad_data': [
              'data/*.yml',
          ],
      },
      install_requires=requires,
      extras_require=extras_require,
      tests_require=tests_require,
      test_suite="tests",
      cmdclass={
          'test': PyTest,
      },
      entry_points={
          'paste.app_factory': [
              'main = oscad:main',
          ],
          'babel.extractors': [
              'oscad_lsuc       = oscad_data.extractors:extract_lsuc',
              'oscad_osuc       = oscad_data.extractors:extract_osuc',
              'oscad_parameters = oscad_data.extractors:extract_parameters',
          ],
          'console_scripts': [
              'oscad-po2xliff = oscad_tools.po2xliff:main',
          ],
      },
      message_extractors={
          'oscad': [
              ('**.py', 'python', None),
              ('**.jinja2', 'jinja2', None),
              ('static/**', 'ignore', None),
          ],
          'oscad_theme_amadeus_internal': [
              ('**.py', 'lingua_python', None),
          ],
      },
      )

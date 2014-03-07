import unittest
import oscad

from pyramid.paster import get_appsettings
from webtest import TestApp


class FunctionalTests(unittest.TestCase):
    def setUp(self):
        settings = get_appsettings('development.ini#main')
        app = oscad.main(settings)
        self.app = TestApp(app)

    def test_dummy(self):
        assert True

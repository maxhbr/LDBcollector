import unittest

class InstalledTests(unittest.TestCase):

    def _getTargetClass(self):
        from pkginfo2.installed import Installed
        return Installed

    def _makeOne(self, filename=None, metadata_version=None):
        if metadata_version is not None:
            return self._getTargetClass()(filename, metadata_version)
        return self._getTargetClass()(filename)

    def test_ctor_w_egg_info_as_file(self):
        import os
        where, _ = os.path.split(__file__)
        funny = os.path.join(where, 'funny')
        installed = self._makeOne(funny)
        self.assertEqual(installed.metadata_version, '1.0')
        self.assertTrue(installed.package.endswith('funny'))
        self.assertEqual(installed.name , 'funny')
        self.assertEqual(installed.package_name , 'funny')
        self.assertEqual(installed.version, '0.1')


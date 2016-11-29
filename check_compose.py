#!/usr/bin/env python

import os
import modulemd

from avocado import main
from avocado import Test


class ComposeTest(Test):

    """
    Validate overall module compose.

    params:
    :param repo: Path to the module repository.
    :param modulemd: Path to the modulemd file.
    """

    def setUp(self):
        """
        Verify required repository parameter has been specified and can be opened.
        Verify required modulemd file parameter has been specified, exists,
        and can be loaded. The file name and loaded metadata are saved.
        """
        repo = self.params.get('repo')
        if repo is None:
            self.error("repo parameter must be supplied")
        self.log.warn("repo %s must be checked" % repo)

        mdfile = self.params.get('modulemd')
        if mdfile is None:
            self.error("modulemd parameter must be supplied")

        mdfile = str(mdfile)
        if not os.path.isfile(mdfile):
            self.error("modulemd file %s must exist" % mdfile)

        try:
            mmd = modulemd.ModuleMetadata()
            mmd.load(mdfile)
        except:
            self.error("Could not load modulemd file %s" % mdfile)

        self.mdfile = mdfile
        self.mmd = mmd


    def test_repo_debugdump(self):
        """
        Make sure we can dump repository details to the logs for
        debugging.
        """
        self.log.warn("Not yet implemented")

    def test_modulemd_debugdump(self):
        """
        Make sure we can dump a copy of the module metadata to the logs for
        debugging.
        """
        data = self.mmd.dumps()
        if not data:
            self.error("Could not dump metadata for modulemd file %s" %
                       self.mdfile)

        self.log.debug("Metadata dump for modulemd file %s:\n%s" %
                       (self.mdfile, data))

    def test_closure(self):
        """
        Check whether the repository passes repoclosure.
        """
        self.log.warn("Not yet implemented")

    def test_component_availability(self):
        """
        Are all the components we reference in the packages section available?
        """
        # verify that the specified ref (if any, defaults to master HEAD) is available in the
        # specified repository (if any, defaults to Fedora [stg] dist-git).
        self.log.warn("Not yet implemented")
        for p in self.mmd.components.rpms.values():
            self.log.warn(
                "Need to check availability of component RPM %s" % p.name)
        for p in self.mmd.components.modules.values():
            self.log.warn(
                "Need to check availability of component module %s" % p.name)

    def test_package_references(self):
        """
        Check that installation profiles, API and filters reference packages
        actually included in the compose.
        """
        self.log.warn("Not yet implemented")

    def test_install_profiles(self):
        """
        Check that installation profiles can actually be installed.
        """
        self.log.warn("Not yet implemented")

    def tearDown(self):
        """
        Do any required teardown here
        """

if __name__ == "__main__":
    main()

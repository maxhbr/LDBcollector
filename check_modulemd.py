#!/usr/bin/env python

import os
import modulemd

from avocado import main
from avocado import Test


class ModulemdTest(Test):

    """
    Validate modulemd

    params:
    :param modulemd: Path to the modulemd file.
    """

    def setUp(self):
        """
        Verify required modulemd file parameter has been specified and exists.
        """
        mdfile = self.params.get('modulemd')
        if mdfile is None:
            self.error("modulemd parameter must be supplied")

        mdfile = str(mdfile)
        if not os.path.isfile(mdfile):
            self.error("modulemd file %s must exist" % mdfile)

        self.modulemd = mdfile

    def test_modulemd(self):
        """
        Dummy test
        """
        self.log.info("Dummy test for modulemd file %s" % self.modulemd)

        self.log.info("Attempting to load modulemd file %s" % self.modulemd)
        mmd = modulemd.ModuleMetadata()
        mmd.load(self.modulemd)

        self.log.debug("Dump of modulemd: %s" % mmd.dumps())

        # Do we provide an API?
        self.log.info("Checking for presence of API definition")
        self.assertTrue(mmd.api)

        # Do we include any components?
        self.log.info("Checking for presence of components")
        self.assertTrue(mmd.components)

        # Do our module-level dependencies look sane?

        # Any spellcheck failures?

        # Stretch: Does the description end with a period?
        self.log.info(
            "Checking for presence of description that is properly punctuated")
        if mmd.description and len(mmd.description) > 0:
            if not mmd.description.endswith('.'):
                self.error("Description should end with a period: %s" %
                           mmd.description)
        else:
            self.error("No description")

        # Stretch: And the summary does not?
        self.log.info(
            "Checking for presence of summary that is properly punctuated")
        if mmd.summary and len(mmd.summary) > 0:
            if mmd.summary.endswith('.'):
                self.error("Summary should not end with a period: %s" %
                           mmd.summary)
        else:
            self.error("No summary")

        # Stretch: Do all the rationales end with a period?
        # Are all the components we reference in the packages section available?
        # If we decide to store core module component list definitions
        # someplace else, check that the modulemd file actually follows those
        # definitions

    def tearDown(self):
        """
        Do any required teardown here
        """

if __name__ == "__main__":
    main()

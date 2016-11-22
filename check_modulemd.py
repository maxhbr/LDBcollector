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
        Verify required modulemd file parameter has been specified, exists,
        and can be loaded. The file name and loaded metadata are saved.
        """
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

    def test_debugdump(self):
        """
        Make sure we can dump a copy of the metadata to the logs for debugging.
        """
        data = self.mmd.dumps()
        if not data:
            self.error("Could not dump metadata for modulemd file %s" %
                       self.mdfile)

        self.log.debug("Metadata dump for modulemd file %s:\n%s" %
                       (self.mdfile, data))

    def test_api(self):
        """
        Do we provide an API?
        """
        self.log.info("Checking for presence of proper API definition")
        self.assertTrue(self.mmd.api)
        self.assertIsInstance(self.mmd.api.rpms, set)
        self.assertGreater(len(self.mmd.api.rpms), 0)

    def test_components(self):
        """
        Do we include any components?
        """
        self.log.info("Checking for presence of components")
        self.assertTrue(self.mmd.components)
        self.assertIsInstance(self.mmd.components.rpms, dict)
        self.assertIsInstance(self.mmd.components.modules, dict)
        self.assertGreater(len(self.mmd.components.rpms) +
                           len(self.mmd.components.modules), 0)

    def test_dependencies(self):
        """
        Do our module-level dependencies look sane?
        """
        self.log.warn("Not yet implemented")

    def test_spellcheck(self):
        """
        Any spellcheck failures?
        """
        self.log.warn("Not yet implemented")

    def test_description(self):
        """
        Does the description end with a period?
        """
        self.log.info(
            "Checking for presence of description that is properly punctuated")
        if self.mmd.description and len(self.mmd.description) > 0:
            if not self.mmd.description.endswith('.'):
                self.error("Description should end with a period: %s" %
                           self.mmd.description)
        else:
            self.error("No description")

    def test_summary(self):
        """
        Does the summary not end with a period?
        """
        self.log.info(
            "Checking for presence of summary that is properly punctuated")
        if self.mmd.summary and len(self.mmd.summary) > 0:
            if self.mmd.summary.endswith('.'):
                self.error("Summary should not end with a period: %s" %
                           self.mmd.summary)
        else:
            self.error("No summary")

    def test_rationales(self):
        """
        Do all the rationales end with a period?
        """
        self.log.warn("Not yet implemented")

    def test_component_availability(self):
        """
        Are all the components we reference in the packages section available?
        """
        self.log.warn("Not yet implemented")

    def tearDown(self):
        """
        Do any required teardown here
        """

if __name__ == "__main__":
    main()

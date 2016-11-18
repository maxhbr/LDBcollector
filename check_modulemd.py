#!/usr/bin/env python

import os

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


    def tearDown(self):
        """
        Do any required teardown here
        """

if __name__ == "__main__":
    main()

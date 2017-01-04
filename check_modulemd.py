#!/usr/bin/env python

import os
import modulemd
from enchant.checker import SpellChecker
from enchant import DictWithPWL

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

        # Infer the module name from the mdfile name and check that it is sane
        mdfileModuleName, mdfileExtension = os.path.basename(mdfile).split('.', 1)
        if (mdfileExtension != 'yaml') and (mdfileExtension != 'yml'):
            self.error("modulemd file %s must have a .y[a]ml extension" % mdfile)
        if mmd.name == '':
            # The name can be missing from the metadata because the builder
            # knows how to infer it
            mmd.name = mdfileModuleName
        elif mmd.name != mdfileModuleName:
            self.error("modulemd file name %s and module name %s do not match" % (
                mdfileModuleName, mmd.name))

        self.mdfile = mdfile
        self.mmd = mmd

        try:
            jargonfile = self.params.get('jargonfile')
            if jargonfile is not None:
                jargonfile = str(jargonfile)
                dict = DictWithPWL("en_US", jargonfile)
                for w in self.mmd.name.split('-'):
                    dict.add_to_session(w)
                self.chkr = SpellChecker(dict)
            else:
                self.chkr = SpellChecker("en_US")
        except:
            self.error(
                "Could not initialize spell checker with dictionary %s" % dict)

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
        # check that all the references modules and stream are registered in the PDC (i.e. they exist)
        self.log.warn("Not yet implemented")
        self.log.info("Checking sanity of module level dependencies")
        if self.mmd.requires:
            for p in self.mmd.requires.keys():
                self.log.warn("Need to sanity check requires %s (stream: %s)" % (
                    p, self.mmd.requires[p]))
        else:
            self.log.info("No dependencies to sanity check")

        self.log.info("Checking sanity of module level build dependencies")
        if self.mmd.buildrequires:
            for p in self.mmd.buildrequires.keys():
                self.log.warn("Need to sanity check build requires %s (stream: %s)" % (
                    p, self.mmd.buildrequires[p]))
        else:
            self.log.info("No build dependencies to sanity check")

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

    def test_description_spelling(self):
        """
        Any spellcheck failures in description?
        """
        self.log.info("Checking for spelling errors in description")
        self.chkr.set_text(self.mmd.description)
        for err in self.chkr:
            self.log.warn(
                "Potential spelling problem in description: %s" % err.word)

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

    def test_summary_spelling(self):
        """
        Any spellcheck failures in summary?
        """
        self.log.info("Checking for spelling errors in summary")
        self.chkr.set_text(self.mmd.summary)
        for err in self.chkr:
            self.log.warn(
                "Potential spelling problem in summary: %s" % err.word)

    def test_rationales(self):
        """
        Do all the rationales end with a period?
        """
        self.log.info(
            "Checking for presence of component rationales that are properly punctuated")

        for p in self.mmd.components.rpms.values():
            if p.rationale and len(p.rationale) > 0:
                if not p.rationale.endswith('.'):
                    self.error("Rationale for component RPM %s should end with a period: %s" % (
                        p.name, p.rationale))
            else:
                self.error("No rationale for component RPM %s" % p.name)
        for p in self.mmd.components.modules.values():
            if p.rationale and len(p.rationale) > 0:
                if not p.rationale.endswith('.'):
                    self.error("Rationale for component module %s should end with a period: %s" % (
                        p.name, p.rationale))
            else:
                self.error("No rationale for component module %s" % p.name)

    def test_rationales_spelling(self):
        """
        Any spellcheck failures in rationales?
        """
        self.log.info("Checking for spelling errors in component rationales")

        for p in self.mmd.components.rpms.values():
            self.chkr.set_text(p.rationale)
            for err in self.chkr:
                self.log.warn("Potential spelling problem in component RPM %s rationale: %s" % (
                    p.name, err.word))
        for p in self.mmd.components.modules.values():
            self.chkr.set_text(p.rationale)
            for err in self.chkr:
                self.log.warn("Potential spelling problem in component module %s rationale: %s" % (
                    p.name, err.word))

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

    def tearDown(self):
        """
        Do any required teardown here
        """

if __name__ == "__main__":
    main()

#!/usr/bin/env python

import os
import modulemd
import requests
import re
from enchant.checker import SpellChecker
from enchant import DictWithPWL
from pdc_client import PDCClient

from avocado import main
from avocado import Test
import yaml
import tempfile
from moduleframework import module_framework
from moduleframework import common


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
        mmd = modulemd.ModuleMetadata()
        mdfile = self.params.get("modulemd")
        self.tmdfile = None

        if not mdfile:
            # try to use module testing farmework if possible
            # https://pagure.io/modularity-testing-framework
            try:
                mtf_backend = module_framework.CommonFunctions()
                self.tmdfile = tempfile.mkstemp(suffix=".yaml")[1]
                with open(self.tmdfile, "w+b") as yamlfile:
                    yaml.dump(mtf_backend.getModulemdYamlconfig(), yamlfile, default_flow_style=False)
                mdfile = self.tmdfile
            except common.ConfigExc:
                pass

        if mdfile is None:
            self.error("modulemd parameter must be supplied")

        mdfile = str(mdfile)
        if not os.path.isfile(mdfile):
            self.error("modulemd file %s must exist" % mdfile)
        try:
            mmd.load(mdfile)
        except Exception as ex:
            self.error("There was an error while processing modulemd file %s: %s" % (mdfile, ex))

        # Infer the module name from the mdfile name and check that it is sane
        mdfileModuleName, mdfileExtension = os.path.basename(mdfile).split('.', 1)
        if (mdfileExtension != "yaml") and (mdfileExtension != "yml"):
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

    def _init_spell_checker(self):
        """
        Initialize spell checker dictionary
        """

        default_dict = "en_US"
        spell_dict = None

        jargonfile = self.params.get('jargonfile')
        if not jargonfile:
            jargonfile = os.environ.get('JARGONFILE')
        if jargonfile is not None:
            try:
                jargonfile = str(jargonfile)
                spell_dict = DictWithPWL(default_dict, jargonfile)
            except:
                self.error(
                    "Could not initialize dictionary using %s file" % jargonfile)

        if not spell_dict:
            try:
                spell_dict = DictWithPWL(default_dict)
            except:
                self.error(
                    "Could not initialize spell checker with dictionary %s" % default_dict)

            #Check if there is jargonfile on module repo
            url = ("https://src.fedoraproject.org/cgit/modules/%s.git/plain/jargon.txt" %
                   self.mmd.name)
            resp = requests.get(url)
            if resp.status_code >= 200 and resp.status_code < 300:
                for w in resp.content.split("\n"):
                    if w != '':
                        spell_dict.add_to_session(w)

        #add words from module name as jargon
        for w in self.mmd.name.split('-'):
            spell_dict.add_to_session(w)

        try:
            chkr = SpellChecker(spell_dict)
        except:
            self.error("Could not initialize spell checker")

        return chkr

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
        #API is not mandatory, but most modules should have it
        if not self.mmd.api:
            self.log.warn("API is not defined for module file: %s" %
                          self.mdfile)
            return
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


    def _query_pdc(self, module_name, stream):
        """
        Check if module and stream are built successfully on PDC server
        """
        pdc_server = "https://pdc.fedoraproject.org/rest_api/v1/unreleasedvariants"
        #Using develop=True to not authenticate to the server
        pdc_session = PDCClient(pdc_server, ssl_verify=True, develop=True)
        pdc_query = dict(
            variant_id = module_name,
            variant_version = stream,
            #active=True returns only succesful builds
            active = True
        )
        try:
            mod_info = pdc_session(**pdc_query)
        except Exception as ex:
            self.error("Could not query PDC server for %s (stream: %s) - %s" % (
                       module_name, stream, ex))
        if not mod_info or "results" not in mod_info.keys() or not mod_info["results"]:
            self.error("%s (stream: %s) is not available on PDC" % (
                       module_name, stream))

    def test_dependencies(self):
        """
        Do our module-level dependencies look sane?
        """
        # check that all the references modules and stream are registered in the PDC (i.e. they exist)
        self.log.info("Checking sanity of module level dependencies")
        if self.mmd.requires:
            for p in self.mmd.requires.keys():
                self._query_pdc(p, self.mmd.requires[p])
        else:
            self.log.info("No dependencies to sanity check")

        self.log.info("Checking sanity of module level build dependencies")
        if self.mmd.buildrequires:
            for p in self.mmd.buildrequires.keys():
                self._query_pdc(p, self.mmd.buildrequires[p])
        else:
            self.log.info("No build dependencies to sanity check")

    def test_description(self):
        """
        Does the description end with a period?
        """
        self.log.info(
            "Checking for presence of description that is properly punctuated")
        if self.mmd.description and len(self.mmd.description) > 0:
            if len(self.mmd.description) != len(self.mmd.description.rstrip()):
                self.log.warn("Description should not end with newline/whitespace '%s'" %
                           self.mmd.description)
            if not self.mmd.description.rstrip().endswith('.'):
                self.log.warn("Description should end with a period: '%s'" %
                           self.mmd.description)
        else:
            self.error("No description")

    def test_description_spelling(self):
        """
        Any spellcheck failures in description?
        """
        self.log.info("Checking for spelling errors in description")
        chkr = self._init_spell_checker()
        chkr.set_text(self.mmd.description)
        for err in chkr:
            self.log.warn(
                "Potential spelling problem in description: %s" % err.word)


    def _read_license_file(self, filename):
        """
        Read all licenses from a file and return them as a list
        """
        try:
            with open(filename) as f:
                data = f.readlines()
        except Exception as ex:
            self.error("Could not open file %s (%s)" % (filename, ex))
        licenses = []
        for line in data:
            #remove all comments from the file
            license = re.sub("#.*","", line).strip()
            if not license:
                continue
            licenses.append(license)
        return licenses

    def _split_license(self, license):
        license_regex = re.compile(r'\(([^)]+)\)|\s(?:and|or|AND|OR)\s')
        return (x.strip() for x in
                (l for l in license_regex.split(license) if l))

    def test_license(self):
        """
        Does the module provide license?
        Based on code from: https://github.com/rpm-software-management/rpmlint/blob/master/TagsCheck.py
        """
        self.log.info(
            "Checking for presence of license")
        if not self.mmd.module_licenses:
            self.error("No module license")

        self.assertIsInstance(self.mmd.module_licenses, set)
        self.assertGreater(len(self.mmd.module_licenses), 0)

        valid_licenses = []
        license_files = [
            "valid_sw_licenses.txt",
            "valid_doc_licenses.txt",
            "valid_content_licenses.txt"
        ]

        for license_file in license_files:
            licenses = self._read_license_file(license_file)
            if not licenses:
                continue
            valid_licenses.extend(licenses)

        #remove duplicated entries
        valid_licenses = list(set(valid_licenses))

        for license in self.mmd.module_licenses:
            if license in valid_licenses:
                continue
            for l1 in self._split_license(license):
                if l1 in valid_licenses:
                    continue
                for l2 in self._split_license(l1):
                    if l2 not in valid_licenses:
                        self.error("License '%s' is not valid" % l2)

    def test_summary(self):
        """
        Does the summary not end with a period?
        """
        self.log.info(
            "Checking for presence of summary that is properly punctuated")
        if self.mmd.summary and len(self.mmd.summary) > 0:
            if len(self.mmd.summary) != len(self.mmd.summary.rstrip()):
                self.log.warn("Summary should not end with newline/whitespace: '%s'" %
                           self.mmd.summary)
            if self.mmd.summary.rstrip().endswith('.'):
                self.log.warn("Summary should not end with a period: '%s'" %
                           self.mmd.summary)
        else:
            self.error("No summary")

    def test_summary_spelling(self):
        """
        Any spellcheck failures in summary?
        """
        self.log.info("Checking for spelling errors in summary")
        chkr = self._init_spell_checker()
        chkr.set_text(self.mmd.summary)
        for err in chkr:
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
                if len(p.rationale) != len(p.rationale.rstrip()):
                    self.log.warn("Rationale for component RPM %s should" % p.name +
                                  " not end with newline/whitespace: '%s'" % p.rationale)
                if not p.rationale.rstrip().endswith('.'):
                    self.log.warn("Rationale for component RPM %s should end with a period: %s" % (
                                  p.name, p.rationale))
            else:
                self.error("No rationale for component RPM %s" % p.name)
        for p in self.mmd.components.modules.values():
            if p.rationale and len(p.rationale) > 0:
                if len(p.rationale) != len(p.rationale.rstrip()):
                    self.log.warn("Rationale for component module %s should" % p.name +
                                  " not end with newline/whitespace: '%s'" % p.rationale)
                if not p.rationale.rstrip().endswith('.'):
                    self.log.warn("Rationale for component module %s should end with a period: '%s'" % (
                        p.name, p.rationale))
            else:
                self.error("No rationale for component module %s" % p.name)

    def test_rationales_spelling(self):
        """
        Any spellcheck failures in rationales?
        """
        self.log.info("Checking for spelling errors in component rationales")

        chkr = self._init_spell_checker()
        for p in self.mmd.components.rpms.values():
            chkr.set_text(p.rationale)
            for err in chkr:
                self.log.warn("Potential spelling problem in component RPM %s rationale: %s" % (
                    p.name, err.word))
        for p in self.mmd.components.modules.values():
            chkr.set_text(p.rationale)
            for err in chkr:
                self.log.warn("Potential spelling problem in component module %s rationale: %s" % (
                    p.name, err.word))

    def _is_commit_ref_available(self, package, namespace):
        """
        Check if commit ref is available on git repository
        """
        if not package or not namespace:
            self.error("Missing parameter to check if commit is available")

        repository = "https://src.fedoraproject.org/cgit/%s/%s.git" % (namespace, package.name)

        if package.repository:
            repository = package.repository

        ref = "HEAD"
        if package.ref:
            ref = package.ref
        patch_path = "/patch/?id=%s" % ref

        url = repository + patch_path
        resp = requests.head(url)
        if resp.status_code < 200 or resp.status_code >= 300:
            self.error("Could not find ref '%s' on '%s'. returned exit status %d; output:\n%s" %
                       (ref, package.name, resp.status_code, resp.text))

        self.log.info("Found ref: %s for %s" % (ref, package.name))

    def test_component_availability(self):
        """
        Are all the components we reference in the packages section available?
        """
        # verify that the specified ref (if none, defaults to master HEAD) is available in the
        # specified repository (if none, defaults to Fedora dist-git).
        for p in self.mmd.components.rpms.values():
            self._is_commit_ref_available(p, "rpms")

        for p in self.mmd.components.modules.values():
            self._is_commit_ref_available(p, "modules")

    def tearDown(self):
        """
        Do any required teardown here
        """
        if self.tmdfile:
            os.remove(self.tmdfile)

if __name__ == "__main__":
    main()

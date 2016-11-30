#!/usr/bin/env python

import os
import modulemd
import dnf

from avocado import main
from avocado import Test


class ComposeTest(Test):

    """
    Validate overall module compose.

    params:
    :param repo: Path to the module repository.
    :param modulemd: Path to the modulemd file.
    """

    def _setup_static_repo(self, reponame, path):
        """
        Initialize the specified local repo.
        """
        repo = dnf.repo.Repo(reponame, self.base.conf.cachedir)
        repo.mirrorlist = None
        repo.metalink = None
        repo.baseurl = "file://" + path
        repo.name = reponame
        self.base.repos.add(repo)
        repo.load()
        repo.enable()

    def _setup_repo(self):
        """
        Initialise the DNF interface using the module compose repository.
        """
        repo = self.params.get('repo')
        if repo is None:
            self.error("repo parameter must be supplied")

        repo = str(repo)
        repo_dir = os.path.abspath(repo)
        if not os.path.isdir(repo_dir):
            self.error("repo directory %s must exist" % repo_dir)

        # initialize DNF interface
        self.base = dnf.Base()
        self.base.reset(repos=True)
        # add just our module compose repo and load what's there
        self._setup_static_repo("module-compose", repo_dir)
        self.base.fill_sack(load_system_repo=False, load_available_repos=True)

    def _find_pkg(self, pkgname):
        """
        Is specified RPM present?
        """
        q = self.base.sack.query()
        matched = q.filter(name=pkgname)
        return len(matched) > 0

    def _find_module(self, modname):
        """
        Is specified module present?
        """
        # How do we do this??
        self.log.warn("Need to find module %s" % modname)
        return False

    def _setup_modulemd(self):
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

    def setUp(self):
        """
        Verify required repository parameter has been specified and can be opened.
        Verify required modulemd file parameter has been specified, exists,
        and can be loaded. The file name and loaded metadata are saved.
        """

        self._setup_repo()
        self._setup_modulemd()

    def test_repo_debugdump(self):
        """
        Make sure we can dump repository details to the logs for
        debugging.
        """
        for repo in self.base.repos.all():
            self.log.debug("Dump of repo [%s]:\n%s" % (repo.id, repo.dump()))

        self.log.debug("List of all repo packages:")
        for pkg in self.base.sack.query():
            self.log.debug("    %s" % pkg.name)

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
        missing = 0

        self.log.info("Checking availability of component RPMs")
        for p in self.mmd.components.rpms.values():
            if not self._find_pkg(p.name):
                self.log.warn("Component RPM %s is missing" % p.name)
                missing += 1

        self.log.info("Checking availability of component modules")
        for p in self.mmd.components.modules.values():
            if not self._find_module(p.name):
                self.log.warn("Component module %s is missing" % p.name)
                missing += 1

        if missing > 0:
            self.error("Missing components detected")

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

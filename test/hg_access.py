#!/usr/bin/env python

# standard library modules, , ,
import unittest
import os
import subprocess
from collections import namedtuple
import hgapi

# hg_access, , access to components available from hg repositories, internal
from yotta.lib import hg_access
# fsutils, , misc filesystem utils, internal
from yotta.lib import fsutils
# version, , represent versions and specifications, internal
from yotta.lib import version
# install, , install components, internal
from yotta import install


Test_Name = 'hg-testing-dummy'
Test_Repo = "hg+ssh://hg@bitbucket.org/autopulated/hg-testing-dummy"
Test_Repo_With_Spec = "hg+ssh://hg@bitbucket.org/autopulated/hg-testing-dummy#0.0.1"
Test_Deps_Name = 'hg-access-testing'
Test_Deps_Target = 'x86-osx,*'


def ensureHGConfig():
    # test if we have a hg user set up, if not we need to set one
    info = hgapi.Repo.command(".", os.environ, "showconfig")
    if info.find("ui.username") == -1:
        # hg doesn't provide a way to set the username from the command line.
        # The HGUSER environment variable can be used for that purpose.
        os.environ['HGUSER'] = 'Yotta Test <test@yottabuild.org>'

class TestHGAccess(unittest.TestCase):
    def setUp(self):
        ensureHGConfig()
        self.remote_component = hg_access.HGComponent.createFromNameAndSpec(Test_Repo, Test_Name)
        self.assertTrue(self.remote_component)
        self.working_copy = self.remote_component.clone()
        self.assertTrue(self.working_copy)
        
    def tearDown(self):
        fsutils.rmRf(self.working_copy.directory)

    def test_installDeps(self):
        Args = namedtuple('Args', ['component', 'target', 'act_globally', 'install_linked'])
        install.installComponent(Args(Test_Deps_Name, Test_Deps_Target, False, False))
    def test_availableVersions(self):
        versions = self.working_copy.availableVersions()
        self.assertIn(version.Version('v0.0.1'), versions)

    def test_versionSpec(self):
        spec = hg_access.HGComponent.createFromNameAndSpec(Test_Repo_With_Spec, Test_Name).versionSpec()
        v = spec.select(self.working_copy.availableVersions())
        self.assertTrue(v)

if __name__ == '__main__':
    unittest.main()

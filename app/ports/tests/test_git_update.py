import os
import shutil

from django.test import TestCase

from parsing_scripts import git_update
from ports.models import LastPortIndexUpdate
from MacPorts.config import MACPORTS_PORTS_DIR


class TestGitUpdates(TestCase):
    def test_between_new_old(self):
        ports = git_update.get_list_of_changed_ports("7646d61853154b9dc523e3d0382960aea562e7ab",
                                                     "ee0fc9c4ca59685f33628fc41c6946920869ab71",
                                                     )
        self.assertEquals(ports, ['ideviceinstaller', 'openblas', 'nomad'])

    def test_between_new_and_database(self):
        LastPortIndexUpdate.update_or_create_first_object("7646d61853154b9dc523e3d0382960aea562e7ab")

        ports = git_update.get_list_of_changed_ports("f3527caa506b1b944f43f47085dd35a8b8e2b050")
        self.assertEquals(ports, ['nomad', 'terraform'])

    def test_broken_repo(self):
        os.chdir(MACPORTS_PORTS_DIR)
        shutil.rmtree('.git')
        ports = git_update.get_list_of_changed_ports("7646d61853154b9dc523e3d0382960aea562e7ab",
                                                     "ee0fc9c4ca59685f33628fc41c6946920869ab71",
                                                     )
        self.assertEquals(ports, ['ideviceinstaller', 'openblas', 'nomad'])

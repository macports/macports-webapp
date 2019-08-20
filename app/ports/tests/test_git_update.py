import os
import shutil

from django.test import TransactionTestCase
from django.core.management import call_command

from parsing_scripts import git_update
from ports.models import LastPortIndexUpdate, Port
from MacPorts.config import MACPORTS_PORTS_DIR


class TestGitUpdates(TransactionTestCase):
    reset_sequences = True

    def test_between_new_old(self):
        ports = git_update.get_list_of_changed_ports("7646d61853154b9dc523e3d0382960aea562e7ab",
                                                     "ee0fc9c4ca59685f33628fc41c6946920869ab71",
                                                     )
        self.assertEquals(ports, set(['devel/ideviceinstaller', 'math/openblas', 'net/nomad']))

    def test_between_new_and_database(self):
        LastPortIndexUpdate.update_or_create_first_object("7646d61853154b9dc523e3d0382960aea562e7ab")

        call_command('update-portinfo', 'f3527caa506b1b944f43f47085dd35a8b8e2b050')
        found = False
        try:
            port1 = Port.objects.get(name='nomad')
            port2 = Port.objects.get(name='terraform')
            found = True
        except Port.DoesNotExist:
            found = False
        self.assertEquals(found, True)

    def test_broken_repo(self):
        os.chdir(MACPORTS_PORTS_DIR)
        shutil.rmtree('.git')
        ports = git_update.get_list_of_changed_ports("7646d61853154b9dc523e3d0382960aea562e7ab",
                                                     "ee0fc9c4ca59685f33628fc41c6946920869ab71",
                                                     )
        self.assertEquals(ports, set(['devel/ideviceinstaller', 'math/openblas', 'net/nomad']))

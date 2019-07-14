import os

from django.test import TestCase

from parsing_scripts import git_update
from ports.models import LastPortIndexUpdate

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TEST_REPO_PARENT = os.path.join(BASE_DIR, 'tests', 'sample_data')


class TestGitUpdates(TestCase):
    def test_between_new_old(self):
        ports = git_update.get_list_of_changed_ports("7646d61853154b9dc523e3d0382960aea562e7ab",
                                                     "ee0fc9c4ca59685f33628fc41c6946920869ab71",
                                                     TEST_REPO_PARENT
                                                     )
        self.assertEquals(ports, ['ideviceinstaller', 'openblas', 'nomad'])

    def test_between_new_and_database(self):
        if LastPortIndexUpdate.objects.count() > 0:
            last_commit = LastPortIndexUpdate.objects.all().first()
            last_commit.git_commit_hash = "7646d61853154b9dc523e3d0382960aea562e7ab"
            last_commit.save()
        else:
            LastPortIndexUpdate.objects.create(git_commit_hash="7646d61853154b9dc523e3d0382960aea562e7ab")

        ports = git_update.get_list_of_changed_ports("f3527caa506b1b944f43f47085dd35a8b8e2b050",
                                                     False,
                                                     TEST_REPO_PARENT
                                                     )
        self.assertEquals(ports, ['nomad', 'terraform'])

    def test_broken_repo(self):
        broken_repo_parent = os.path.join(TEST_REPO_PARENT, 'broken_directory')
        ports = git_update.get_list_of_changed_ports("7646d61853154b9dc523e3d0382960aea562e7ab",
                                                     "ee0fc9c4ca59685f33628fc41c6946920869ab71",
                                                     broken_repo_parent
                                                     )
        self.assertEquals(ports, ['ideviceinstaller', 'openblas', 'nomad'])

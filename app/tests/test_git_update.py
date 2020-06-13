import os

from django.test import TransactionTestCase

from parsing_scripts import git_update
import config


class TestGitUpdates(TransactionTestCase):
    reset_sequences = True

    def test_cloning_repo(self):
        os.mkdir(config.DATA_DIR)
        git_update.rebuild_repo(config.MACPORTS_PORTS_DIR, config.MACPORTS_PORTS_URL, config.MACPORTS_PORTS)
        git_update.rebuild_repo(config.MACPORTS_CONTRIB_DIR, config.MACPORTS_CONTRIB_URL, config.MACPORTS_CONTRIB)

        self.assertTrue(os.path.isdir(config.MACPORTS_PORTS_DIR))
        self.assertTrue(os.path.isdir(config.MACPORTS_CONTRIB_DIR))

from unittest import TestCase as _TestCase

import pytest


class Test(_TestCase):

    @classmethod
    @pytest.fixture(autouse=True, scope='module')
    def _checkAndSetup(cls):
        # TODO: nothing here yet

        # run the test
        yield

import unittest

from .client import app

class TestIntegration(unittest.TestCase):

    def test_sanity(self):
        r = app.get()

        self.assertEqual(r.text, 'Hello world!')

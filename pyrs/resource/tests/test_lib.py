import unittest

from .. import lib


class TestPathParse(unittest.TestCase):

    def test_basic(self):
        path, args = lib.parse_path('/')

        self.assertEqual(path, '/')
        self.assertEqual(args, {})

    def test_with_simple(self):
        path, args = lib.parse_path('/user/<id>')

        self.assertEqual(path, '/user/{id}')
        self.assertEqual(args, {'id': ('default', (), {})})

    def test_with_int_type(self):
        path, args = lib.parse_path('/user/<int:id>/set_password')

        self.assertEqual(path, '/user/{id}/set_password')
        self.assertEqual(args, {'id': ('int', (), {})})

    def test_with_unicode_type(self):
        path, args = lib.parse_path(
            '/user/<string(minlength=1):uid>/set_password'
        )

        self.assertEqual(path, '/user/{uid}/set_password')
        self.assertEqual(args, {'uid': ('string', (), {'minlength': 1})})

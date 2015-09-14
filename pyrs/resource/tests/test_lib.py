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


class TestFQName(unittest.TestCase):

    def test_function(self):
        self.assertEqual(
            lib.fqname(lib.fqname), 'pyrs.resource.lib.fqname'
        )

    def test_class(self):
        self.assertEqual(
            lib.fqname(TestFQName), 'pyrs.resource.tests.test_lib.TestFQName'
        )

    def test_instance(self):
        self.assertEqual(
            lib.fqname(self), 'pyrs.resource.tests.test_lib.TestFQName'
        )

    def test_class_method(self):
        self.assertEqual(
            lib.fqname(TestFQName.test_class_method),
            'pyrs.resource.tests.test_lib.TestFQName.test_class_method'
        )

    def test_instance_method(self):
        self.assertEqual(
            lib.fqname(self.test_instance_method),
            'pyrs.resource.tests.test_lib.TestFQName.test_instance_method'
        )

    def test_builtin_exception_class(self):
        self.assertIn('.Exception', lib.fqname(Exception))

    def test_builtin_exception_instance(self):
        ex = Exception
        self.assertIn('.Exception', lib.fqname(ex))

    def test_builtin(self):
        self.assertIn('.id', lib.fqname(id))

    def test_builtin_class(self):
        self.assertIn('.dict', lib.fqname(dict))

    def test_builtin_instance(self):
        self.assertIn('dict', lib.fqname({}))

    def test_builtin_class_method(self):
        self.assertIn('dict', lib.fqname(dict.get))

    def test_builtin_instance_method(self):
        self.assertIn('dict', lib.fqname(dict.get))

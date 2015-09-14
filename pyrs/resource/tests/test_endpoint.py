import unittest

from .. import endpoints


class TestEndpointAsString(unittest.TestCase):

    def setUp(self):
        self.endpoint = endpoints.Endpoint('name')

    def test_type(self):
        self.assertIsInstance(self.endpoint, dict)
        self.assertEqual(self.endpoint['name'], 'name')

    def test_hash(self):
        self.assertEqual(hash(self.endpoint), hash('name'))

    def test_string(self):
        self.assertEqual(str(self.endpoint), 'name')

    def test_repr(self):
        self.assertEqual(repr(self.endpoint), repr('name'))

    def test_equal(self):
        self.assertEqual(self.endpoint, 'name')

    def test_name(self):
        self.assertEqual(self.endpoint.name, 'name')


class TestEndpointAsDictionary(unittest.TestCase):

    def test_update_name(self):
        endpoint = endpoints.Endpoint('name')
        endpoint['name'] = 'updated'

        self.assertEqual(endpoint, 'updated')

    def test_as_dict(self):
        endpoint = endpoints.Endpoint('name', value1='111')
        endpoint['value2'] = '222'

        self.assertEqual(endpoint['value1'], '111')
        self.assertEqual(endpoint['value2'], '222')
        self.assertEqual(endpoint['name'], 'name')

    def test_using_another_dict(self):
        endpoint = endpoints.Endpoint('name', {'value': '111'})

        self.assertEqual(endpoint['value'], '111')
        self.assertEqual(endpoint['name'], 'name')


class TestEndpointRelation(unittest.TestCase):

    def test_parent_unset(self):
        endpoint = endpoints.Endpoint('name')

        self.assertEqual(endpoint.parent, endpoint)
        self.assertEqual(id(endpoint.parent), id(endpoint))

    def test_parent(self):
        parent = endpoints.Endpoint('parent')
        endpoint = endpoints.Endpoint('name', parent=parent)

        self.assertEqual(id(endpoint.parent), id(parent))

    def test_root_unset(self):
        endpoint = endpoints.Endpoint('name')

        self.assertEqual(endpoint.root, endpoint)
        self.assertEqual(id(endpoint.root), id(endpoint))

    def test_root_set(self):
        root = endpoints.Endpoint('root')
        parent = endpoints.Endpoint('parent', parent=root)
        endpoint = endpoints.Endpoint('name', parent=parent)

        self.assertEqual(id(endpoint.parent), id(parent))
        self.assertEqual(id(endpoint.root), id(root))

    def test_chain(self):
        root = endpoints.Endpoint('root')
        parent = endpoints.Endpoint('parent', parent=root)
        endpoint = endpoints.Endpoint('name', parent=parent)

        self.assertEqual(list(map(id, root.chain)), [id(root)])
        self.assertEqual(list(map(id, parent.chain)), [id(root), id(parent)])
        self.assertEqual(
            list(map(id, endpoint.chain)), [id(root), id(parent), id(endpoint)]
        )

    def test_fqname(self):
        root = endpoints.Endpoint('root')
        parent = endpoints.Endpoint('parent', parent=root)
        endpoint = endpoints.Endpoint('name', parent=parent)

        self.assertEqual(root.fqname, 'root')
        self.assertEqual(parent.fqname, 'root.parent')
        self.assertEqual(endpoint.fqname, 'root.parent.name')


class TestFactory(unittest.TestCase):

    def test_make(self):
        factory = endpoints.Factory()

        def func():
            pass

        target = factory.make(func)

        self.assertEqual(target, func)
        self.assertIsInstance(target.__endpoint__, endpoints.Endpoint)
        self.assertEqual(target.__endpoint__['name'], 'func')
        self.assertTrue(
            target.__endpoint__['fqname'].startswith(
                'pyrs.resource.tests.test_endpoint.'
            )
        )
        self.assertTrue(target.__endpoint__['fqname'].endswith('.func'))

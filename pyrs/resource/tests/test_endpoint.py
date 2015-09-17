import unittest

from .. import endpoints


class TestPath(unittest.TestCase):

    def test_as_string(self):
        path = endpoints.Path('/')

        self.assertIsInstance(path, endpoints.Path)
        self.assertEqual(path, '/')

    def test_template(self):
        path = endpoints.Path('/<id>')

        self.assertEqual(path.template, '/{id}')

    def test_args(self):
        path = endpoints.Path('/<id>')

        self.assertEqual(path.args, {'id': ('default', (), {})})

    def test_extend_with_a_string(self):
        path = endpoints.Path('/<id>') + '/'

        self.assertEqual(path.template, '/{id}/')

    def test_extend_with_a_path(self):
        path = endpoints.Path('/<id>') + endpoints.Path('/')

        self.assertEqual(path.template, '/{id}/')

    def test_format(self):
        path = endpoints.Path('/<id>')

        self.assertEqual(path.format(id=12), '/12')
        self.assertEqual(path % {'id': 12}, '/12')


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

    def test_copy(self):
        endpoint = endpoints.Endpoint('name')
        copy = endpoint.copy()

        self.assertIsInstance(copy, endpoints.Endpoint)
        self.assertEqual(copy['name'], 'name')
        self.assertNotEqual(id(copy), id(endpoint))


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


class TestFactoryBase(unittest.TestCase):

    def test_make(self):
        factory = endpoints.Factory()

        def func():
            pass

        target = factory.RESOURCE(func)

        self.assertEqual(target, func)
        self.assertIsInstance(target._endpoint_, endpoints.Endpoint)
        self.assertEqual(target._endpoint_['name'], 'func')
        self.assertEqual(target._endpoint_['realname'], 'func')

    def test_make_as_decorator_without_params(self):
        factory = endpoints.Factory()

        @factory.RESOURCE
        def func():
            pass

        self.assertIsInstance(func._endpoint_, endpoints.Endpoint)
        self.assertEqual(func._endpoint_['name'], 'func')
        self.assertEqual(func._endpoint_['realname'], 'func')

    def test_make_as_decorator_with_extra_params(self):
        factory = endpoints.Factory()

        @factory.RESOURCE(extra='extra')
        def func():
            pass

        self.assertIsInstance(func._endpoint_, endpoints.Endpoint)
        self.assertEqual(func._endpoint_['name'], 'func')
        self.assertEqual(func._endpoint_['realname'], 'func')
        self.assertEqual(func._endpoint_['extra'], 'extra')

    def test_rename(self):
        factory = endpoints.Factory()

        @factory.RESOURCE(name='fancyname')
        def func():
            pass

        self.assertIsInstance(func._endpoint_, endpoints.Endpoint)
        self.assertEqual(func._endpoint_['name'], 'fancyname')
        self.assertEqual(func._endpoint_['realname'], 'func')

    def test_realname_cannot_change(self):
        factory = endpoints.Factory()

        @factory.RESOURCE(name='fancyname', realname='fancyname')
        def func():
            pass

        self.assertIsInstance(func._endpoint_, endpoints.Endpoint)
        self.assertEqual(func._endpoint_['name'], 'fancyname')
        self.assertEqual(func._endpoint_['realname'], 'func')

    def test_endpoint_default_behaviour(self):
        factory = endpoints.Factory()

        @factory.PATH
        def func():
            pass

        self.assertIsInstance(func._endpoint_, endpoints.Endpoint)
        [path] = func._endpoint_['paths']
        self.assertEqual(path, '/')

    def test_endpoint_specified_path(self):
        factory = endpoints.Factory()

        @factory.PATH(path='/path/<int(min=1):id>')
        def func():
            pass

        self.assertIsInstance(func._endpoint_, endpoints.Endpoint)
        [path] = func._endpoint_['paths']
        self.assertEqual(path, '/path/<int(min=1):id>')
        self.assertEqual(path.template, '/path/{id}')
        self.assertEqual(path.args, {'id': ('int', (), {'min': 1})})

    def test_factory(self):
        self.assertIsInstance(endpoints.factory, endpoints.Factory)


class TestEndpoints(unittest.TestCase):

    def test_GET(self):
        @endpoints.GET
        def func():
            pass
        self.assertEqual(func._endpoint_['methods'], ['GET'])

    def test_POST(self):
        @endpoints.POST
        def func():
            pass
        self.assertEqual(func._endpoint_['methods'], ['POST'])

    def test_PUT(self):
        @endpoints.PUT
        def func():
            pass
        self.assertEqual(func._endpoint_['methods'], ['PUT'])

    def test_DELETE(self):
        @endpoints.DELETE
        def func():
            pass
        self.assertEqual(func._endpoint_['methods'], ['DELETE'])

    def test_PATCH(self):
        @endpoints.PATCH
        def func():
            pass
        self.assertEqual(func._endpoint_['methods'], ['PATCH'])

    def test_RPC(self):
        @endpoints.RPC
        def func():
            pass
        self.assertEqual(func._endpoint_['methods'], ['POST'])

    def test_basic_shortcuts(self):
        self.assertEqual(endpoints.GET, endpoints.factory.GET)
        self.assertEqual(endpoints.POST, endpoints.factory.POST)
        self.assertEqual(endpoints.PUT, endpoints.factory.PUT)
        self.assertEqual(endpoints.DELETE, endpoints.factory.DELETE)
        self.assertEqual(endpoints.PATCH, endpoints.factory.PATCH)

    def test_special_shortcuts(self):
        self.assertEqual(endpoints.RPC, endpoints.factory.RPC)


class TestMultipleEndpoints(unittest.TestCase):

    def test_multiple_endpoint(self):
        @endpoints.PUT
        @endpoints.PATCH
        @endpoints.PATCH
        def func():
            pass
        self.assertEqual(
            sorted(func._endpoint_['methods']), ['PATCH', 'PUT']
        )

    def test_multiple_endpoint_given(self):
        @endpoints.PUT(methods=['PATCH'])
        def func():
            pass
        self.assertEqual(
            sorted(func._endpoint_['methods']), ['PATCH', 'PUT'])


class TestMultiplePaths(unittest.TestCase):

    def test_multiple_paths(self):
        @endpoints.factory.GET(path=['/user/<id>', '/admin'])
        def func():
            pass

        [path1, path2] = func._endpoint_['paths']
        self.assertEqual(path1, '/user/<id>')
        self.assertEqual(path2, '/admin')


class TestDecorators(unittest.TestCase):

    def _test_a(self):
        @endpoints.path('aaa')
        def func():
            pass

        self.assertEqual(endpoints.path.__name__, 'path')
        self.assertEqual(func._endpoint_['path'], 'aaa')

    def _test_b(self):
        @endpoints.get
        def func():
            pass

        self.assertEqual(func._endpoint_['method'], 'GET')

    def _test_c(self):
        @endpoints.get(method='POST')
        def func():
            pass

        self.assertEqual(func._endpoint_['method'], 'POST')

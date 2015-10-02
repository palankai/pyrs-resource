import unittest

from .. import operations


class TestPath(unittest.TestCase):

    def test_as_string(self):
        path = operations.Path('/')

        self.assertIsInstance(path, operations.Path)
        self.assertEqual(path, '/')
        self.assertEqual(path.args, {})
        self.assertEqual(list(path.keys), [])

    def test_template(self):
        path = operations.Path('/<id>')

        self.assertEqual(path.template, '/{id}')

    def test_args(self):
        path = operations.Path('/<id>')

        self.assertEqual(path.args, {'id': ('default', (), {})})
        self.assertEqual(list(path.keys), ['id'])

    def test_extend_with_a_string(self):
        path = operations.Path('/<id>') + '/'

        self.assertEqual(path.template, '/{id}/')

    def test_extend_with_a_path(self):
        path = operations.Path('/<id>') + operations.Path('/')

        self.assertEqual(path.template, '/{id}/')

    def test_format(self):
        path = operations.Path('/<id>')

        self.assertEqual(path.format(id=12), '/12')
        self.assertEqual(path % {'id': 12}, '/12')


class TestEndpointAsCallable(unittest.TestCase):

    def test_basic(self):

        def func():
            return 1
        operation = operations.Operation('name', target=func)

        res = operation()

        self.assertEqual(res, 1)

    def test_class_based(self):
        class Res(object):
            def func(self):
                return 1

        main = operations.Operation('Res', target=Res)
        operation = operations.Operation('func', target='func', upstream=main)

        self.assertIsInstance(main(), Res)
        self.assertEqual(operation(), 1)

    def test_upstream_with_args(self):
        class Res(object):

            def __init__(self, x):
                self.x = x

            def func(self, x):
                return x + self.x

        main = operations.Operation('Res', target=Res, kwargs={'x': 1})
        operation = operations.Operation('func', target='func', upstream=main)

        self.assertIsInstance(main(), Res)
        self.assertEqual(operation(x=1), 2)


class TestOperationAsString(unittest.TestCase):

    def setUp(self):
        self.operation = operations.Operation('name')

    def test_type(self):
        self.assertIsInstance(self.operation, dict)
        self.assertEqual(self.operation['name'], 'name')

    def test_hash(self):
        self.assertEqual(hash(self.operation), hash('name'))

    def test_string(self):
        self.assertEqual(str(self.operation), 'name')

    def test_repr(self):
        self.assertEqual(repr(self.operation), repr('name'))

    def test_equal(self):
        self.assertEqual(self.operation, 'name')

    def test_name(self):
        self.assertEqual(self.operation.name, 'name')


class TestOperationAsDictionary(unittest.TestCase):

    def test_update_name(self):
        operation = operations.Operation('name')
        operation['name'] = 'updated'

        self.assertEqual(operation, 'updated')

    def test_as_dict(self):
        operation = operations.Operation('name', value1='111')
        operation['value2'] = '222'

        self.assertEqual(operation['value1'], '111')
        self.assertEqual(operation['value2'], '222')
        self.assertEqual(operation['name'], 'name')

    def test_using_another_dict(self):
        operation = operations.Operation('name', {'value': '111'})

        self.assertEqual(operation['value'], '111')
        self.assertEqual(operation['name'], 'name')

    def test_copy(self):
        operation = operations.Operation('name')
        copy = operation.copy()

        self.assertIsInstance(copy, operations.Operation)
        self.assertEqual(copy['name'], 'name')
        self.assertNotEqual(id(copy), id(operation))


class TestOperationRelation(unittest.TestCase):

    def test_parent_unset(self):
        operation = operations.Operation('name')

        self.assertEqual(operation.parent, operation)
        self.assertEqual(id(operation.parent), id(operation))

    def test_parent(self):
        parent = operations.Operation('parent')
        operation = operations.Operation('name', parent=parent)

        self.assertEqual(id(operation.parent), id(parent))

    def test_root_unset(self):
        operation = operations.Operation('name')

        self.assertEqual(operation.root, operation)
        self.assertEqual(id(operation.root), id(operation))

    def test_root_set(self):
        root = operations.Operation('root')
        parent = operations.Operation('parent', parent=root)
        operation = operations.Operation('name', parent=parent)

        self.assertEqual(id(operation.parent), id(parent))
        self.assertEqual(id(operation.root), id(root))

    def test_chain(self):
        root = operations.Operation('root')
        parent = operations.Operation('parent', parent=root)
        operation = operations.Operation('name', parent=parent)

        self.assertEqual(list(map(id, root.chain)), [id(root)])
        self.assertEqual(list(map(id, parent.chain)), [id(root), id(parent)])
        self.assertEqual(
            list(map(id, operation.chain)),
            [id(root), id(parent), id(operation)]
        )

    def test_fqname(self):
        root = operations.Operation('root')
        parent = operations.Operation('parent', parent=root)
        operation = operations.Operation('name', parent=parent)

        self.assertEqual(root.fqname, 'root')
        self.assertEqual(parent.fqname, 'root.parent')
        self.assertEqual(operation.fqname, 'root.parent.name')


class TestFactoryBase(unittest.TestCase):

    def test_make(self):
        factory = operations.Factory()

        def func():
            pass

        target = factory.RESOURCE(func)

        self.assertEqual(target, func)
        self.assertIsInstance(target._descriptor_, operations.Operation)
        self.assertEqual(target._descriptor_['name'], 'func')
        self.assertEqual(target._descriptor_['realname'], 'func')

    def test_make_as_decorator_without_params(self):
        factory = operations.Factory()

        @factory.RESOURCE
        def func():
            pass

        self.assertIsInstance(func._descriptor_, operations.Operation)
        self.assertEqual(func._descriptor_['name'], 'func')
        self.assertEqual(func._descriptor_['realname'], 'func')

    def test_make_as_decorator_with_extra_params(self):
        factory = operations.Factory()

        @factory.RESOURCE(extra='extra')
        def func():
            pass

        self.assertIsInstance(func._descriptor_, operations.Operation)
        self.assertEqual(func._descriptor_['name'], 'func')
        self.assertEqual(func._descriptor_['realname'], 'func')
        self.assertEqual(func._descriptor_['extra'], 'extra')

    def test_rename(self):
        factory = operations.Factory()

        @factory.RESOURCE(name='fancyname')
        def func():
            pass

        self.assertIsInstance(func._descriptor_, operations.Operation)
        self.assertEqual(func._descriptor_['name'], 'fancyname')
        self.assertEqual(func._descriptor_['realname'], 'func')

    def test_descriptor_default_behaviour(self):
        factory = operations.Factory()

        @factory.PATH('/')
        def func():
            pass

        self.assertIsInstance(func._descriptor_, operations.Operation)
        [path] = func._descriptor_['paths']
        self.assertEqual(path, '/')

    def test_descriptor_specified_path(self):
        factory = operations.Factory()

        @factory.PATH(path='/path/<int(min=1):id>')
        def func():
            pass

        self.assertIsInstance(func._descriptor_, operations.Operation)
        [path] = func._descriptor_['paths']
        self.assertEqual(path, '/path/<int(min=1):id>')
        self.assertEqual(path.template, '/path/{id}')
        self.assertEqual(path.args, {'id': ('int', (), {'min': 1})})

    def test_factory(self):
        self.assertIsInstance(operations.factory, operations.Factory)


class TestOperations(unittest.TestCase):

    def test_GET(self):
        @operations.GET
        def func():
            pass
        self.assertEqual(func._descriptor_['methods'], ['GET'])

    def test_POST(self):
        @operations.POST
        def func():
            pass
        self.assertEqual(func._descriptor_['methods'], ['POST'])

    def test_PUT(self):
        @operations.PUT
        def func():
            pass
        self.assertEqual(func._descriptor_['methods'], ['PUT'])

    def test_DELETE(self):
        @operations.DELETE
        def func():
            pass
        self.assertEqual(func._descriptor_['methods'], ['DELETE'])

    def test_PATCH(self):
        @operations.PATCH
        def func():
            pass
        self.assertEqual(func._descriptor_['methods'], ['PATCH'])

    def test_RPC(self):
        @operations.RPC
        def func():
            pass
        self.assertEqual(func._descriptor_['methods'], ['POST'])

    def test_basic_shortcuts(self):
        self.assertEqual(operations.GET, operations.factory.GET)
        self.assertEqual(operations.POST, operations.factory.POST)
        self.assertEqual(operations.PUT, operations.factory.PUT)
        self.assertEqual(operations.DELETE, operations.factory.DELETE)
        self.assertEqual(operations.PATCH, operations.factory.PATCH)

    def test_special_shortcuts(self):
        self.assertEqual(operations.RPC, operations.factory.RPC)
        self.assertEqual(operations.PATH, operations.factory.PATH)


class TestMultipleOperations(unittest.TestCase):

    def test_multiple_endpoint(self):
        @operations.PUT
        @operations.PATCH
        @operations.PATCH
        def func():
            pass
        self.assertEqual(
            sorted(func._descriptor_['methods']), ['PATCH', 'PUT']
        )

    def test_multiple_descriptor_given(self):
        @operations.PUT(methods=['PATCH', 'PUT'])
        def func():
            pass
        self.assertEqual(
            sorted(func._descriptor_['methods']), ['PATCH', 'PUT'])


class TestMultiplePaths(unittest.TestCase):

    def test_multiple_paths(self):
        @operations.factory.GET(path=['/user/<id>', '/admin'])
        def func():
            pass

        [path1, path2] = func._descriptor_['paths']
        self.assertEqual(path1, '/user/<id>')
        self.assertEqual(path2, '/admin')

    def test_extend_paths(self):
        @operations.factory.GET(path=['/admin'])
        @operations.factory.PATH('/user/<id>')
        def func():
            pass

        [path1, path2] = func._descriptor_['paths']
        self.assertEqual(path1, '/user/<id>')
        self.assertEqual(path2, '/admin')


class TestDecorators(unittest.TestCase):

    def _test_a(self):
        @operations.path('aaa')
        def func():
            pass

        self.assertEqual(operations.path.__name__, 'path')
        self.assertEqual(func._descriptor_['path'], 'aaa')

    def _test_b(self):
        @operations.get
        def func():
            pass

        self.assertEqual(func._descriptor_['method'], 'GET')

    def _test_c(self):
        @operations.get(method='POST')
        def func():
            pass

        self.assertEqual(func._descriptor_['method'], 'POST')

import unittest

from pyrs import schema

from .. import base
from .. import resource
from .. import gateway


class TestBasicCases(unittest.TestCase):

    def setUp(self):
        app_users = [
            {'id': 1, 'name': 'admin', 'email': 'admin@example.com'},
            {'id': 2, 'name': 'guest', 'email': 'guest@example.com'},
        ]

        class UserSchema(schema.Object):
            id = schema.Integer()
            name = schema.String()
            email = schema.String()
            pk = schema.String()

        class UserSchemaResponse(UserSchema):
            pk = schema.String(min_len=2)

        class UserResource(object):

            @resource.GET(response=schema.Array(items=UserSchema()))
            def get_users(self):
                return app_users

            @resource.GET(path='/<name>', response=UserSchema)
            def get_user_by_name(self, name):
                for user in self.get_users():
                    if user['name'] == name:
                        # Workaround of pyrs-schema issue #14
                        return user.copy()

            @resource.POST(body=UserSchema, response=UserSchemaResponse)
            def create_user(self, body):
                body['id'] = 12
                return body

        class Application(base.App):
            pass

        self.app_users = app_users
        self.app = Application()
        self.app.add('/user', UserResource)

    def test_get_users(self):

        req = gateway.Request.from_values(
            path='/user/', method='GET'
        )
        res = self.app.dispatch(req)
        self.assertEqual(res.json, self.app_users)

    def test_get_user_by_name(self):

        req = gateway.Request.from_values(
            path='/user/admin', method='GET'
        )
        res = self.app.dispatch(req)
        self.assertEqual(res.json, self.app_users[0])

    def test_get_user_by_name_invalid_response(self):

        req = gateway.Request.from_values(
            path='/user/invalid', method='GET'
        )
        res = self.app.dispatch(req)

        self.assertEqual(res.status_code, 500)
        self.assertEqual(
            res.json['error'],
            'pyrs.schema.exceptions.ValidationErrors'
        )

    def test_valid_request(self):

        req = gateway.Request.from_values(
            path='/user/', method='POST', data={
                'id': 12,
                'name': 'hello',
                'email': 'email',
                'pk': 'aaa'
            }
        )
        res = self.app.dispatch(req)

        self.assertEqual(res.status_code, 201)
        self.assertEqual(
            res.json['pk'], 'aaa'
        )

    def test_invalid_request(self):

        req = gateway.Request.from_values(
            path='/user/', method='POST', data={'id': '"hello"'}
        )
        res = self.app.dispatch(req)

        self.assertEqual(res.status_code, 400)
        self.assertEqual(
            res.json['error'], 'BadRequest'
        )

    def test_invalid_response(self):

        req = gateway.Request.from_values(
            path='/user/', method='POST', data={
                'id': 12,
                'name': 'hello',
                'email': 'email',
                'pk': 'a'
            }
        )
        res = self.app.dispatch(req)

        self.assertEqual(res.status_code, 500)

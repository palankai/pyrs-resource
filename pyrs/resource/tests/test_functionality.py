import json
import unittest

from pyrs import schema

from .. import base
from .. import resource


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

        class UserResource(object):

            @resource.GET
            def get_users(self):
                return app_users

            @resource.GET(path='/<name>', response=UserSchema)
            def get_user_by_name(self, name):
                for user in self.get_users():
                    if user['name'] == name:
                        # Workaround of pyrs-schema issue #14
                        return user.copy()

            @resource.POST(request=UserSchema, inject_body='body')
            def create_user(self, body):
                body['id'] = 12
                return body

        class Application(base.App):
            pass

        self.app_users = app_users
        self.app = Application()
        self.app.add('/user', UserResource)

    def test_get_users(self):

        content, status, headers = self.app.dispatch('/user/', 'GET')
        self.assertEqual(content, self.app_users)

    def test_get_user_by_name(self):

        content, status, headers = self.app.dispatch('/user/admin', 'GET')
        self.assertEqual(json.loads(content), self.app_users[0])

    def test_get_user_by_name_invalid_response(self):

        content, status, headers = self.app.dispatch('/user/invalid', 'GET')
        self.assertEqual(status, 500)
        self.assertEqual(
            json.loads(content)['error'],
            'pyrs.schema.exceptions.ValidationErrors'
        )

    def test_invalid_request(self):

        content, status, headers = self.app.dispatch(
            '/user/', 'POST', body={'id': '"hello"'}
        )
        err = json.loads(content)

        self.assertEqual(status, 400)
        self.assertEqual(
            err['error'], 'BadRequest'
        )

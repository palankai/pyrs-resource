import json
import unittest

from pyrs import schema

from .. import application_old as application
from .. import exceptions
from .. import resource


class TestBasicCases(unittest.TestCase):

    def setUp(self):
        app_users = [
            {'id': 1, 'name': 'admin', 'email': 'admin@example.com'},
            {'id': 2, 'name': 'guest', 'email': 'guest@example.com'},
        ]

        class UserSchema(schema.Schema):
            name = schema.String()
            email = schema.String()

        class UserResource(object):

            @resource.GET
            def get_users(self):
                return app_users

            @resource.GET(path='/<name>')
            def get_user_by_name(self, name):
                for user in self.get_users():
                    if user['name'] == name:
                        return user
                raise exceptions.NotFound("User '%s' doesn't exist" % name)

            @resource.POST
            def create_user(self, user):
                user['id'] = 3
                return user

        class Application(application.Application):
            pass

        self.app_users = app_users
        self.app = Application()
        self.app.add('/user', UserResource)

    def test_get_users(self):

        r = self.app.dispatch('GET', '/user/')
        self.assertEqual(json.loads(r), self.app_users)

    def test_get_user_by_name(self):

        r = self.app.dispatch('GET', '/user/admin')
        self.assertEqual(json.loads(r), self.app_users[0])

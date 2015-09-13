import json
import unittest

from .client import app
from .. import demo


class TestIntegration(unittest.TestCase):

    def test_get_users(self):
        r = app.get('/user/')

        self.assertEqual(r.json, demo.users)

    def test_get_user_by_pk(self):
        r = app.get('/user/{}'.format(1))
        self.assertEqual(r.json, demo.users[0])

    def test_get_user_by_name(self):
        r = app.get('/user/{}'.format('admin'))
        self.assertEqual(r.json, demo.users[0])

    def test_get_user_groups(self):
        r = app.get('/user/{}/groups'.format(1))
        self.assertEqual(r.json, ['administrators', 'users'])

    def test_form_post(self):
        r = app.post('/user/', data={
            'username': 'editor', 'email': 'editor@example.com'
        })

        self.assertEqual(r.status_code, 201)
        self.assertEqual(
            r.json,
            {'pk':5, 'username': 'editor', 'email': 'editor@example.com'}
        )

    def test_json_post(self):
        user = {'username': 'editor', 'email': 'editor@example.com'}
        r = app.post('/user/', data=json.dumps(user))

        self.assertEqual(r.status_code, 201)
        self.assertEqual(
            r.json,
            {'pk':5, 'username': 'editor', 'email': 'editor@example.com'}
        )

    def test_patching_user(self):
        r = app.patch('/user/{}'.format(1), data={
            'email': 'updated@example.com'
        })

        self.assertEqual(r.status_code, 200)
        self.assertEqual(
            r.json,
            {'pk':1, 'username': 'admin', 'email': 'updated@example.com'}
        )

    def test_set_user(self):
        r = app.put('/user/', data={
            'pk':1, 'email': 'updated@example.com', 'username':'admin'
        })

        self.assertEqual(r.status_code, 200)
        self.assertEqual(
            r.json,
            {'pk':1, 'username': 'admin', 'email': 'updated@example.com'}
        )

    def test_delete_user(self):
        r = app.delete('/user/{}'.format(1))

        self.assertEqual(r.text, '')
        self.assertEqual(r.status_code, 200)

    def test_set_password_rpc(self):
        r = app.post('/user/{}/set_password'.format(1), data='"secret"')

        self.assertEqual(r.text, '')
        self.assertEqual(r.status_code, 200)

class TestErrors(unittest.TestCase):

    def test_form_post_with_extra_pk(self):
        r = app.post('/user/', data={
            'username': 'editor', 'email': 'editor@example.com', 'pk': 5
        })

        self.assertEqual(r.status_code, 400)
        self.assertEqual(r.json['error'], 'BadRequest')
        self.assertEqual(r.json['errors'][0]['error'], 'ValidationError')
        self.assertEqual(len(r.json['errors']), 1)

    def test_object_not_found(self):
        r = app.get('/user/{}'.format(11))

        self.assertEqual(r.status_code, 404)
        self.assertEqual(r.json['error'], 'NotFound')
        self.assertEqual(r.json['message'], 'User#11 not found')

    def test_set_password_rpc(self):
        r = app.post('/user/{}/set_password'.format(1), data='secret')

        self.assertEqual(r.status_code, 400)
        self.assertEqual(r.json['error'], 'BadRequest')

class TestErrorWrapping(unittest.TestCase):

    def test_general_error_handling(self):
        r = app.put('/user/unexpected-error')

        self.assertEqual(r.status_code, 500)
        self.assertIn('.Exception', r.json['error'])
        self.assertEqual(r.json['message'], 'Something happened')

    def test_internal_server_error_handling(self):
        r = app.put('/user/internal-server-error')

        self.assertEqual(r.status_code, 500)
        self.assertEqual(r.json['error'], 'InternalServerError')
        self.assertEqual(r.json['message'], 'Something happened')

    def test_builtin_error_handling(self):
        r = app.put('/user/builtin-error')

        self.assertEqual(r.status_code, 500)
        self.assertIn('.IndexError', r.json['error'])

    def test_interface_error_handling(self):
        r = app.put('/user/interface-error')

        self.assertEqual(r.status_code, 500)
        self.assertIn('.TypeError', r.json['error'])

    def test_not_implemented_error_handling(self):
        r = app.put('/user/not-implemented-error')

        self.assertEqual(r.status_code, 501)
        self.assertIn(r.json['error'], 'NotImplemented')


class TestWerkzeugErrors(unittest.TestCase):

    def test_not_found(self):
        r = app.get('/user2/')

        self.assertEqual(r.status_code, 404)
        self.assertEqual(r.json['error'], 'NotFound')
        self.assertIn('message', r.json)

    def test_method_not_allowed(self):
        r = app.delete('/user/')

        self.assertEqual(r.status_code, 405)
        self.assertEqual(r.json['error'], 'MethodNotAllowed')
        self.assertIn('message', r.json)

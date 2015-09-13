from pyrs.resource import *
from pyrs.schema import *


users = [
    {'pk': 1, 'username': 'admin', 'email': 'admin@example.com'},
    {'pk': 2, 'username': 'guest', 'email': 'guest@example.com'},
    {'pk': 3, 'username': 'foo', 'email': 'foo@example.com'},
    {'pk': 4, 'username': 'bar', 'email': 'bar@example.com'},
]

groups = [
    {'pk': 1, 'name': 'administrators', 'members': [1]},
    {'pk': 2, 'name': 'users', 'members': [1, 3, 4]},
    {'pk': 4, 'name': 'editors', 'members': []},
]


class UserSchema(Object):
    pk = Integer(tags=['readonly'])
    username = String()
    email = String()


class UserResource(object):

    @GET(output=Array(items=UserSchema()))
    def get_users(self):
        return users

    @POST(
        body=UserSchema(name='user', exclude_tags='readonly'),
        output=UserSchema
    )
    def add_user(self, user):
        user['pk'] = 5
        return user

    @PUT(body=UserSchema, output=UserSchema)
    def set_user(self, body):
        return body

    @DELETE(path='/<int:pk>')
    def delete_user(self, pk):
        self.get_user(pk)
        return

    @GET(path='/<int:pk>', output=UserSchema)
    def get_user(self, pk):
        for user in users:
            if user['pk'] == pk:
                return user

    @GET(path='/<int:pk>/groups', output=Array(items=String()))
    def get_user_groups(self, pk):
        self.get_user(pk)
        names = []
        for group in groups:
            if pk in group['members']:
                names.append(group['name'])
        return names

    @GET(path='/<string:name>', output=UserSchema)
    def get_user_by_name(self, name):
        for user in users:
            if user['username'] == name:
                return user

    @PATCH(
        path='/<int:pk>',
        body=UserSchema(exclude_tags='readonly'),
        output=UserSchema
    )
    def update_user(self, pk, body):
        user = self.get_user(pk).copy()
        user.update(body)
        return user


class DemoApplication(App):

    def setup(self):
        self.add('/user', UserResource)


application = DemoApplication()


if __name__ == '__main__':
    from werkzeug.serving import run_simple
    run_simple('127.0.0.1', 5000, application.wsgi, use_debugger=True)

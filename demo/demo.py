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


class GroupSchema(Object):
    pk = Integer()
    name = String()


class GroupsForUserResource(object):

    def __init__(self, user_pk):
        self.user_pk = user_pk
        self.groups = []
        for group in groups:
            if user_pk in group['members']:
                self.groups.append(group)

    @GET(output=Array(items=GroupSchema()))
    def get_groups(self):
        res = []
        for group in self.groups:
            res.append({'pk': group['pk'], 'name': group['name']})
        return res

    @GET(path='/<int:group_id>', output=GroupSchema())
    def get_group(self, group_id):
        for group in self.groups:
            if group['pk'] == group_id:
                return {'pk': group['pk'], 'name': group['name']}
        raise NotFound('Group #%s not found' % pk)


class UserResource(object):
    # The implemented methods doesn't modify the database, just emulate it

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

    @PUT(body=UserSchema, output=UserSchema, scope=True)
    def set_user(self, scope, body):
        if not self.has_user(body['pk']):
            scope.response.status_code = 201
        return body

    @DELETE(path='/<int:pk>')
    def delete_user(self, pk):
        self.get_user(pk)
        return

    @RPC(path='/<int:pk>/set_password', body=String(name='password'))
    def set_password(self, pk, password):
        self.get_user(pk)
        return

    @GET(path='/<int:pk>', output=UserSchema)
    def get_user(self, pk):
        for user in users:
            if user['pk'] == pk:
                return user
        raise NotFound('User#%s not found' % pk)

    def has_user(self, pk):
        for user in users:
            if user['pk'] == pk:
                return True
        return False

    @FORWARD(path='/<int:pk>/groups', forward=GroupsForUserResource)
    def get_user_groups(self, scope, pk, path='/'):
        resource = GroupsForUserResource(pk)
        return scope.forward(resource, path)

    @GET(path='/<string:name>', output=UserSchema)
    def get_user_by_name(self, name):
        for user in users:
            if user['username'] == name:
                return user
        raise NotFound('User(username=%s) not found' % name)

    @PATCH(
        path='/<int:pk>',
        body=UserSchema(exclude_tags='readonly'),
        output=UserSchema
    )
    def update_user(self, pk, body):
        user = self.get_user(pk).copy()
        user.update(body)
        return user

    # The following methods will raise errors

    @PUT(path='/unexpected-error')
    def unexpected_error(self):
        raise Exception('Something happened')

    @PUT(path='/builtin-error')
    def builtin_error(self):
        users[9]

    @PUT(path='/interface-error')
    def interface_error(self, pk):
        # Will raise TypeError because of pk argument
        pass

    @PUT(path='/not-implemented-error')
    def not_implemented_error(self):
        raise NotImplementedError()

    @PUT(path='/internal-server-error')
    def internal_server_error(self):
        raise InternalServerError('Something happened')


class DemoApplication(App):

    def setup(self):
        self.add('/user', UserResource)


application = DemoApplication()


if __name__ == '__main__':
    from werkzeug.serving import run_simple
    run_simple('127.0.0.1', 5000, application.wsgi, use_debugger=True)

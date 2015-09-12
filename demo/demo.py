from pyrs.resource import *


class UserResource(object):

    @GET
    def get_users(self):
        return 'Hello world!'


class DemoApplication(App):

    def setup(self):
        self.add('/', UserResource)


application = DemoApplication()


if __name__ == '__main__':
    from werkzeug.serving import run_simple
    run_simple('127.0.0.1', 5000, application.wsgi, use_debugger=True)

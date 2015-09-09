from pyrs.resource import App

class DemoApplication(App):

    def setup(self):
        pass


application = DemoApplication()


if __name__ == '__main__':
    from werkzeug.serving import run_simple
    run_simple(
        '127.0.0.1', 5000, application, use_debugger=True, use_reloader=True
    )

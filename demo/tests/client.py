import json

from werkzeug import test
from werkzeug.wrappers import Response

from .. import demo


class TestResponse(Response):

    @property
    def text(self):
        return self.get_data(True)

    @property
    def json(self):
        return json.loads(self.text)


app = test.Client(demo.application, response_wrapper=TestResponse)

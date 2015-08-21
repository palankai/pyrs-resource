import json
import unittest


from .. import errors


class TestResponse(unittest.TestCase):

    def test_general_exception(self):
        try:
            raise Exception('message', 12)
        except Exception as ex:
            content = errors.ErrorSchema(debug=False).dump(ex)
            name = ex.__class__.__module__+'.'+ex.__class__.__name__
            pass

        content = json.loads(content)

        self.assertEqual(content, {
            'error': name,
            'message': ['message', 12],
        })

    def test_base_error(self):
        try:
            raise errors.Error('message', 12)
        except Exception as ex:
            content = errors.ErrorSchema(debug=False).dump(ex)
            name = ex.__class__.__module__+'.'+ex.__class__.__name__
            pass

        content = json.loads(content)

        self.assertEqual(content, {
            'error': name,
            'message': ['message', 12],
        })

    def test_special_error(self):
        class Special(errors.Error):
            error = 'special'
            description = 'description of error'
            uri = 'http://example.com/special'
        try:
            raise Special()
        except Exception as ex:
            content = errors.ErrorSchema(debug=False).dump(ex)

        content = json.loads(content)

        self.assertEqual(content, {
            'error': 'special',
            'error_description': 'description of error',
            'error_uri': 'http://example.com/special',
        })

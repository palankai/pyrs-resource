import json
import unittest

from .. import errors


class TestError(unittest.TestCase):

    def test_wrap(self):
        original = Exception()
        name = original.__class__.__module__+'.'+original.__class__.__name__
        ex = errors.Error.wrap(original)

        self.assertIsInstance(ex, errors.Error)
        self.assertEqual(ex.cause, original)
        self.assertEqual(ex.error, name)

    def test_wrap_with_message(self):
        original = Exception('Error message')
        ex = errors.Error.wrap(original)

        self.assertEqual(ex.args, ('Error message',))


class TestSchema(unittest.TestCase):

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
            'message': 'message',
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

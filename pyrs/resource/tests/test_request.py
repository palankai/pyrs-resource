import unittest

from pyrs import schema

from .. import gateway


class TestParseInput(unittest.TestCase):

    def test_parse_without_parser(self):
        req = gateway.RequestMixin()

        value = req._parse_value('Hello', None, None)
        self.assertEqual(value, 'Hello')

    def test_parse_schema(self):
        req = gateway.RequestMixin()

        class MySchema(schema.Object):
            search = schema.String()
            limit = schema.Integer()

        consumer = lambda v, o: schema.JSONFormReader(o).read(v)

        value_part_cls = req._parse_value(
            {'search': 'hello'}, consumer, MySchema()
        )
        value_full_cls = req._parse_value(
            {'search': 'hello', 'limit': '1'}, consumer, MySchema()
        )
        value_part_obj = req._parse_value(
            {'search': 'hello'}, consumer, MySchema()
        )
        value_full_obj = req._parse_value(
            {'search': 'hello', 'limit': '1'}, consumer, MySchema()
        )

        self.assertEqual(value_part_cls, {'search': 'hello'})
        self.assertEqual(value_part_obj, {'search': 'hello'})

        self.assertEqual(value_full_cls, {'search': 'hello', 'limit': 1})
        self.assertEqual(value_full_obj, {'search': 'hello', 'limit': 1})

import unittest

from .. import gateway


class TestEnvelope(unittest.TestCase):

    def test_request(self):
        request = gateway.Request.from_values()
        envelope = gateway.Envelope(request)

        self.assertEqual(envelope.request, request)

    def test_response(self):
        request = gateway.Request.from_values()
        envelope = gateway.Envelope(request)

        self.assertIsInstance(envelope.response, gateway.Response)

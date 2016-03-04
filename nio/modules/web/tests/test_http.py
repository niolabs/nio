from nio.testing.test_case import NIOTestCase
from nio.modules.web.http import Request, Response, \
    HTTPNotImplemented, HTTPUnauthorized, HTTPNotFound


class TestWebClasses(NIOTestCase):

    def test_request(self):
        """ Test the request object has the correct attributes """
        the_body = 'My body'
        the_params = {'identifier': 'foo'}
        the_headers = {'content-type': 'application/json'}
        req = Request(the_body, the_params, the_headers)
        self.assertEqual(req.get_body(), the_body)
        self.assertEqual(req.get_identifier(), the_params['identifier'])
        self.assertDictEqual(req.get_params(), the_params)
        self.assertEqual(req.get_header('content-type'),
                         the_headers['content-type'])

    def test_response(self):
        """ Test the response object has the correct attributes """
        resp = Response()
        with self.assertRaises(NotImplementedError):
            resp.set_header('foo', 'bar')

        with self.assertRaises(NotImplementedError):
            resp.set_status(200, 'what a message')

        with self.assertRaises(NotImplementedError):
            resp.set_body('check it out')

    def test_errors(self):
        """ Test that the exceptions contain the correct HTTP statuses """
        try:
            raise HTTPNotImplemented()
        except Exception as e:
            self.assertEqual(e.status, 501)
            self.assertEqual(e.message, 'Not Implemented')

        try:
            raise HTTPUnauthorized()
        except Exception as e:
            self.assertEqual(e.status, 401)
            self.assertEqual(e.message, 'Unauthorized')

        try:
            raise HTTPNotFound()
        except Exception as e:
            self.assertEqual(e.status, 404)
            self.assertEqual(e.message, 'Not Found')

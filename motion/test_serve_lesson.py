import functools
import http.client
from http.server import ThreadingHTTPServer
from pathlib import Path
import tempfile
import threading
import unittest
from motion.serve_lesson import LessonHandler

class RangeTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory()
        Path(cls.tmp.name, 'test.mp4').write_bytes(b'0123456789')
        cls.server = ThreadingHTTPServer(('127.0.0.1', 0), functools.partial(LessonHandler, directory=cls.tmp.name))
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()
        cls.thread.join()
        cls.tmp.cleanup()

    def request(self, header=None, method='GET'):
        c = http.client.HTTPConnection(*self.server.server_address)
        c.request(method, '/test.mp4', headers={'Range': header} if header else {})
        r = c.getresponse()
        result = r.status, dict(r.getheaders()), r.read()
        c.close()
        return result

    def test_full_and_partial(self):
        for header, expected, span in [(None, b'0123456789', None), ('bytes=2-4', b'234', 'bytes 2-4/10'), ('bytes=7-', b'789', 'bytes 7-9/10'), ('bytes=-3', b'789', 'bytes 7-9/10'), ('bytes=8-99', b'89', 'bytes 8-9/10')]:
            with self.subTest(header=header):
                status, headers, body = self.request(header)
                self.assertEqual(status, 206 if header else 200)
                self.assertEqual(body, expected)
                self.assertEqual(headers.get('Content-Range'), span)
                self.assertEqual(int(headers['Content-Length']), len(expected))

    def test_invalid_and_head(self):
        for header in ['bytes=20-', 'bytes=3-1', 'bytes=-0', 'bytes=abc', 'bytes=0-1,3-4']:
            self.assertEqual(self.request(header)[0], 416)
        status, headers, body = self.request('bytes=2-4', 'HEAD')
        self.assertEqual((status, headers['Content-Length'], body), (206, '3', b''))

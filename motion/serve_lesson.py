"""Local lesson player server with byte-range support for native video seeking."""
import argparse
import os
import re
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from functools import partial

class LessonHandler(SimpleHTTPRequestHandler):
    def send_head(self):
        self.byte_range = None
        path = self.translate_path(self.path)
        if not os.path.isfile(path):
            return super().send_head()
        try:
            stream = open(path, 'rb')
        except OSError:
            self.send_error(404)
            return None
        size = os.fstat(stream.fileno()).st_size
        start, end = 0, size - 1
        header = self.headers.get('Range')
        if header:
            match = re.fullmatch(r'bytes=(\d*)-(\d*)', header)
            if match and any(match.groups()):
                a, b = match.groups()
                if a:
                    start = int(a)
                    end = min(int(b), size - 1) if b else size - 1
                else:
                    start = max(0, size - int(b))
                valid = 0 <= start <= end < size
            else:
                valid = False
            if not valid:
                stream.close()
                self.send_response(416)
                self.send_header('Content-Range', f'bytes */{size}')
                self.send_header('Content-Length', '0')
                self.end_headers()
                return None
            self.byte_range = (start, end)
        self.send_response(206 if header else 200)
        self.send_header('Content-Type', self.guess_type(path))
        self.send_header('Accept-Ranges', 'bytes')
        self.send_header('Content-Length', str(end - start + 1))
        self.send_header('Cache-Control', 'no-cache')
        if header:
            self.send_header('Content-Range', f'bytes {start}-{end}/{size}')
        self.end_headers()
        stream.seek(start)
        return stream

    def copyfile(self, source, outputfile):
        remaining = self.byte_range[1] - self.byte_range[0] + 1 if self.byte_range else None
        try:
            while remaining is None or remaining > 0:
                chunk = source.read(min(65536, remaining) if remaining is not None else 65536)
                if not chunk:
                    break
                outputfile.write(chunk)
                if remaining is not None:
                    remaining -= len(chunk)
        except (BrokenPipeError, ConnectionResetError):
            pass  # Seeking cancels the previous media request.

if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('directory')
    p.add_argument('--port', type=int, default=8767)
    args = p.parse_args()
    server = ThreadingHTTPServer(('127.0.0.1', args.port), partial(LessonHandler, directory=args.directory))
    print(f'Player: http://127.0.0.1:{args.port}/', flush=True)
    server.serve_forever()

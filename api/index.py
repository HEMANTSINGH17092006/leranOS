import io
import sys
import traceback
from http.server import BaseHTTPRequestHandler
from pathlib import Path

# Ensure project root is in sys.path
ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

try:
    from app import app as flask_app
except Exception as e:
    _import_err = traceback.format_exc()
    flask_app = None

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self._handle_request()

    def do_POST(self):
        self._handle_request()

    def do_PUT(self):
        self._handle_request()

    def do_DELETE(self):
        self._handle_request()

    def do_HEAD(self):
        self._handle_request()

    def do_OPTIONS(self):
        self._handle_request()

    def _handle_request(self):
        if flask_app is None:
            self.send_response(500)
            self.send_header('Content-Type', 'text/html; charset=utf-8')
            self.end_headers()
            self.wfile.write(f"<h1>LearnOS Startup Error</h1><pre>{_import_err}</pre>".encode('utf-8'))
            return

        try:
            content_length = int(self.headers.get('Content-Length', 0)) if self.headers.get('Content-Length') else 0
            body = self.rfile.read(content_length) if content_length > 0 else b""
            
            # Determine path and query
            full_path = self.path
            if '?' in full_path:
                path_info, query_string = full_path.split('?', 1)
            else:
                path_info, query_string = full_path, ''
                
            environ = {
                'wsgi.version': (1, 0),
                'wsgi.url_scheme': 'https',
                'wsgi.input': io.BytesIO(body),
                'wsgi.errors': sys.stderr,
                'wsgi.multithread': False,
                'wsgi.multiprocess': False,
                'wsgi.run_once': False,
                'REQUEST_METHOD': self.command,
                'SCRIPT_NAME': '',
                'PATH_INFO': path_info,
                'QUERY_STRING': query_string,
                'SERVER_NAME': 'learn-os.vercel.app',
                'SERVER_PORT': '443',
                'SERVER_PROTOCOL': self.request_version,
            }
            
            if 'Content-Type' in self.headers:
                environ['CONTENT_TYPE'] = self.headers['Content-Type']
            if 'Content-Length' in self.headers:
                environ['CONTENT_LENGTH'] = str(content_length)
                
            for header_name in self.headers:
                key = 'HTTP_' + header_name.upper().replace('-', '_')
                environ[key] = self.headers[header_name]

            status_code = 200
            headers_to_send = []

            def start_response(status, response_headers, exc_info=None):
                nonlocal status_code, headers_to_send
                status_code = int(status.split(' ')[0])
                headers_to_send = response_headers
                return lambda data: None

            response_iter = flask_app(environ, start_response)
            response_body = b''.join(response_iter)

            self.send_response(status_code)
            for header, value in headers_to_send:
                self.send_header(header, value)
            self.end_headers()
            self.wfile.write(response_body)

        except Exception as ex:
            tb = traceback.format_exc()
            self.send_response(500)
            self.send_header('Content-Type', 'text/html; charset=utf-8')
            self.end_headers()
            self.wfile.write(f"<h1>LearnOS Request Error</h1><pre>{tb}</pre>".encode('utf-8'))

    def log_message(self, format, *args):
        # Silence default stderr logging on Vercel
        pass

# Also export app for direct WSGI runners
app = flask_app



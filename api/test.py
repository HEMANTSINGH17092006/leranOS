from http.server import BaseHTTPRequestHandler
import sys

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-Type', 'text/plain')
        self.end_headers()
        self.wfile.write(f'Vercel Python OK. Python: {sys.version}'.encode('utf-8'))

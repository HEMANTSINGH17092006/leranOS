import sys
import traceback
from pathlib import Path

# Ensure project root is in sys.path
ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

try:
    from app import app
    
    _original_wsgi_app = app.wsgi_app
    def _debug_wsgi(environ, start_response):
        try:
            return _original_wsgi_app(environ, start_response)
        except Exception as e:
            tb = traceback.format_exc()
            start_response('200 OK', [('Content-Type', 'text/html; charset=utf-8')])
            return [f"<h1>LearnOS WSGI Exception</h1><pre>{tb}</pre>".encode('utf-8')]
            
    app.wsgi_app = _debug_wsgi

except Exception as import_err:
    import_tb = traceback.format_exc()
    from flask import Flask
    app = Flask(__name__)
    
    @app.route("/", defaults={"path": ""})
    @app.route("/<path:path>")
    def catch_all(path):
        return f"<h1>LearnOS Startup/Import Error</h1><pre>{import_tb}</pre>", 200


import sys
import traceback
from pathlib import Path

# Ensure project root is in sys.path
ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

try:
    from app import app as flask_app
    
    # WSGI Exception Handler Middleware for detailed production logging
    class WSGIDebugMiddleware:
        def __init__(self, wsgi_app):
            self.wsgi_app = wsgi_app

        def __call__(self, environ, start_response):
            try:
                return self.wsgi_app(environ, start_response)
            except Exception as e:
                err_trace = traceback.format_exc()
                print(f"[Vercel Request Error]:\n{err_trace}", flush=True)
                status = '500 Internal Server Error'
                headers = [('Content-Type', 'text/html; charset=utf-8')]
                start_response(status, headers)
                html = f"""<!DOCTYPE html>
<html>
<head><title>LearnOS Error</title></head>
<body style="font-family: monospace; padding: 2rem; background: #0f172a; color: #f8fafc;">
    <h2 style="color: #ef4444;">LearnOS Production Runtime Error</h2>
    <pre style="background: #1e293b; padding: 1.5rem; border-radius: 8px; overflow: auto; color: #fb7185; line-height: 1.5;">{err_trace}</pre>
</body>
</html>"""
                return [html.encode('utf-8')]

    app = WSGIDebugMiddleware(flask_app)

except Exception as e:
    startup_trace = traceback.format_exc()
    print(f"[Vercel Import Error]:\n{startup_trace}", flush=True)

    def app(environ, start_response):
        status = '500 Internal Server Error'
        headers = [('Content-Type', 'text/html; charset=utf-8')]
        start_response(status, headers)
        html = f"""<!DOCTYPE html>
<html>
<head><title>LearnOS Startup Error</title></head>
<body style="font-family: monospace; padding: 2rem; background: #0f172a; color: #f8fafc;">
    <h2 style="color: #ef4444;">LearnOS Startup / Import Failure</h2>
    <pre style="background: #1e293b; padding: 1.5rem; border-radius: 8px; overflow: auto; color: #fb7185; line-height: 1.5;">{startup_trace}</pre>
</body>
</html>"""
        return [html.encode('utf-8')]

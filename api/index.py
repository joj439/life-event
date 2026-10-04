import sys
import os

# Add backend directory to Python sys.path
backend_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend"))
if backend_path not in sys.path:
    sys.path.insert(0, backend_path)

from main import app as fastapi_app


class VercelASGIApp:
    """
    Transparent ASGI wrapper for Vercel serverless deployment.
    Preserves original request paths when Vercel rewrites forward to /api/index.py.
    """
    def __init__(self, inner_app):
        self.inner_app = inner_app

    async def __call__(self, scope, receive, send):
        if scope.get("type") == "http":
            path = scope.get("path", "")
            # Check if path was rewritten to entrypoint filename
            if path in ("/api/index.py", "/api/index", "/api"):
                headers = dict(scope.get("headers", []))
                forwarded_uri = headers.get(b"x-forwarded-uri") or headers.get(b"x-real-origin")
                if forwarded_uri:
                    real_path = forwarded_uri.decode("latin1").split("?")[0]
                    if real_path:
                        scope["path"] = real_path
        await self.inner_app(scope, receive, send)

    def __getattr__(self, name):
        return getattr(self.inner_app, name)


# Expose app for Vercel ASGI serverless handler
app = VercelASGIApp(fastapi_app)

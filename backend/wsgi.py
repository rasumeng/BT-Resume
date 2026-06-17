"""
WSGI entry point for Gunicorn.
Run with: gunicorn --bind 127.0.0.1:5000 backend.wsgi:app
"""

from backend.app import app

if __name__ == "__main__":
    app.run()

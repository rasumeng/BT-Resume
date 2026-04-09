"""
PyWebView wrapper for Resume AI
Launches Flask backend and opens in a native window (no browser chrome)
"""

import webview
import threading
import time
import requests
from web_app import app

def run_flask():
    """Run Flask server in background"""
    app.run(debug=False, host='127.0.0.1', port=5000, use_reloader=False)

def wait_for_server():
    """Wait for Flask server to be ready"""
    max_attempts = 30
    for attempt in range(max_attempts):
        try:
            response = requests.get('http://localhost:5000/api/health')
            if response.status_code == 200:
                return True
        except requests.exceptions.RequestException:
            pass
        time.sleep(0.5)
    return False

def main():
    """Launch app in native window"""
    # Start Flask in background thread
    flask_thread = threading.Thread(target=run_flask, daemon=True)
    flask_thread.start()

    # Wait for server to be ready
    print("Starting server...")
    if not wait_for_server():
        print("Failed to start server")
        return

    print("Opening application window...")

    # Create native window with web content
    webview.create_window(
        title='Beyond The Resume',
        url='http://localhost:5000',
        width=1200,
        height=800,
        min_size=(900, 600),
        background_color='#0D0D0B'
    )

    webview.start()

if __name__ == '__main__':
    main()

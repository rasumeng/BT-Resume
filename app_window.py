"""
PyWebView wrapper for Resume AI
Launches Flask backend and opens in a native window (no browser chrome)
"""

import webview
import threading
import time
import requests
import atexit
import signal
import sys
from web_app import app

# Global reference to Flask thread for cleanup
flask_thread = None

def run_flask():
    """Run Flask server in background"""
    app.run(debug=False, host='127.0.0.1', port=5000, use_reloader=False, threaded=True)

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

def cleanup():
    """Cleanup function called on exit"""
    # Ollama is now user-managed, so we don't stop it on exit
    # The user can keep it running for other purposes
    pass

def main():
    """Launch app in native window"""
    global flask_thread
    
    print("=" * 60)
    print("Beyond The Resume - Starting Up")
    print("=" * 60)
    
    # Register cleanup handlers
    atexit.register(cleanup)
    signal.signal(signal.SIGINT, lambda s, f: cleanup_and_exit())
    signal.signal(signal.SIGTERM, lambda s, f: cleanup_and_exit())
    
    try:
        # Start Flask in background thread
        print("\n[1/2] Starting Flask server...")
        flask_thread = threading.Thread(target=run_flask, daemon=True)
        flask_thread.start()

        # Wait for server to be ready
        if not wait_for_server():
            print("Failed to start server")
            cleanup()
            return

        print("\n[2/2] Opening application window...")

        # Create native window with web content
        window = webview.create_window(
            title='Beyond The Resume',
            url='http://localhost:5000',
            width=1200,
            height=800,
            min_size=(900, 600),
            background_color='#0D0D0B'
        )

        print("Application ready! Opening window...\n")
        webview.start(debug=False)
        
        # This code runs when window is closed
        print("\nApplication window closed.")
        
    except KeyboardInterrupt:
        print("\n\nApplication interrupted by user.")
    except Exception as e:
        print(f"\nError: {e}")
    finally:
        # Ensure cleanup happens
        cleanup()
        print("Goodbye!")

def cleanup_and_exit():
    """Cleanup and exit immediately"""
    cleanup()
    sys.exit(0)


if __name__ == '__main__':
    main()

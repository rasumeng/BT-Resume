"""
PyWebView wrapper for Resume AI
Launches Flask backend and opens in a native window (no browser chrome)
"""

import webview
import threading
import time
import requests
from web_app import app
from core.llm_client import start_ollama, stop_ollama, is_ollama_running

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
    print("=" * 60)
    print("Beyond The Resume - Starting Up")
    print("=" * 60)
    
    # Start Ollama first
    print("\n[1/3] Starting LLM (Ollama)...")
    if not start_ollama():
        print("WARNING: Ollama failed to start. Some features may not work.")
        print("You can manually start Ollama or check that it's installed.")
    
    time.sleep(2)  # Give Ollama time to fully initialize
    
    # Start Flask in background thread
    print("\n[2/3] Starting Flask server...")
    flask_thread = threading.Thread(target=run_flask, daemon=True)
    flask_thread.start()

    # Wait for server to be ready
    if not wait_for_server():
        print("Failed to start server")
        stop_ollama()
        return

    print("\n[3/3] Opening application window...")

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
    webview.start()
    
    # Cleanup when window closes
    print("\nApplication closing...")
    print("Shutting down LLM (Ollama)...")
    stop_ollama()
    print("Goodbye!")


if __name__ == '__main__':
    main()

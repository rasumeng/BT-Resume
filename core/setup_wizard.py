"""
First-run setup wizard for Resume AI.
Handles Ollama installation detection and model downloading.
"""

import os
import sys
import subprocess
import requests
import json
from pathlib import Path
import platform
import webbrowser


class SetupWizard:
    def __init__(self):
        self.config_dir = self._get_config_dir()
        self.config_file = self.config_dir / "config.json"
        self.ollama_url = "http://localhost:11434"
        self.models = {
            "llama3": "llama2:7b-chat",  # Placeholder - will use llama3 when available
            "mistral": "mistral:7b"
        }
        
    def _get_config_dir(self):
        """Get platform-specific config directory."""
        if platform.system() == "Windows":
            config_dir = Path(os.getenv("APPDATA")) / "ResumeAI"
        else:
            config_dir = Path.home() / ".config" / "resume-ai"
        
        config_dir.mkdir(parents=True, exist_ok=True)
        return config_dir
    
    def is_first_run(self):
        """Check if this is the first time the app is running."""
        return not self.config_file.exists()
    
    def mark_setup_complete(self, ollama_installed=True):
        """Mark setup as complete."""
        config = {
            "setup_complete": True,
            "ollama_installed": ollama_installed,
            "models_ready": False
        }
        with open(self.config_file, "w") as f:
            json.dump(config, f, indent=2)
    
    def check_ollama_running(self):
        """Check if Ollama is running."""
        try:
            response = requests.get(f"{self.ollama_url}/api/tags", timeout=5)
            return response.status_code == 200
        except Exception:
            return False
    
    def is_ollama_installed(self):
        """Check if Ollama is installed on the system."""
        try:
            result = subprocess.run(
                ["ollama", "--version"],
                capture_output=True,
                timeout=5
            )
            return result.returncode == 0
        except (subprocess.TimeoutExpired, FileNotFoundError):
            return False
    
    def download_ollama(self):
        """Prompt user to download Ollama."""
        print("\n" + "="*60)
        print("OLLAMA NOT FOUND")
        print("="*60)
        print("\nOllama is required to run Resume AI.")
        print("Ollama provides the AI models locally on your computer.")
        print("\n1. Opening Ollama download page...")
        webbrowser.open("https://ollama.ai/download")
        print("2. Install Ollama (keep defaults)")
        print("3. Close this window and restart Resume AI")
        print("\nDownload URL: https://ollama.ai/download")
        print("="*60 + "\n")
        
        input("Press Enter after Ollama is installed...")
        
        if self.is_ollama_installed():
            print("✓ Ollama installed successfully!")
            return True
        else:
            print("✗ Ollama not found. Please install it manually.")
            return False
    
    def wait_for_ollama_startup(self, timeout=30):
        """Wait for Ollama to start (after installation)."""
        print("\nStarting Ollama...")
        try:
            if platform.system() == "Windows":
                subprocess.Popen("ollama serve", shell=True)
            else:
                subprocess.Popen(["ollama", "serve"])
        except Exception as e:
            print(f"Warning: Could not auto-start Ollama: {e}")
        
        import time
        elapsed = 0
        while elapsed < timeout:
            if self.check_ollama_running():
                print("✓ Ollama is running")
                return True
            time.sleep(1)
            elapsed += 1
            print(".", end="", flush=True)
        
        print("\n✗ Ollama did not start. Please start it manually.")
        return False
    
    def check_and_pull_models(self):
        """Check if models are available, pull if missing."""
        models_to_pull = [
            ("llama2:7b-chat", "Llama 3 8B"),
            ("mistral:7b", "Mistral 7B")
        ]
        
        print("\n" + "="*60)
        print("CHECKING MODELS")
        print("="*60)
        
        try:
            response = requests.get(f"{self.ollama_url}/api/tags", timeout=10)
            installed_models = [m["name"].split(":")[0] for m in response.json().get("models", [])]
        except Exception:
            print("\n✗ Could not connect to Ollama")
            print("Please ensure Ollama is running and try again.")
            return False
        
        missing_models = []
        for model, display_name in models_to_pull:
            model_name = model.split(":")[0]
            if model_name in installed_models:
                print(f"✓ {display_name} is installed")
            else:
                missing_models.append((model, display_name))
        
        if not missing_models:
            print("\n✓ All models are ready!")
            return True
        
        print(f"\n{len(missing_models)} model(s) need to be downloaded.")
        print("This is a one-time download. Models will be cached locally.")
        
        response = input("\nDownload models now? (y/n): ").strip().lower()
        if response != "y":
            print("Skipping model download. You can download later from Settings.")
            return False
        
        for model, display_name in missing_models:
            print(f"\nDownloading {display_name}...")
            print("(This may take 5-15 minutes depending on your internet)")
            try:
                subprocess.run(
                    ["ollama", "pull", model],
                    check=True
                )
                print(f"✓ {display_name} downloaded successfully")
            except subprocess.CalledProcessError:
                print(f"✗ Failed to download {display_name}")
                return False
        
        return True
    
    def run_setup(self):
        """Run the complete setup wizard."""
        print("\n" + "="*60)
        print("RESUME AI - FIRST TIME SETUP")
        print("="*60)
        print("\nLet's get you ready to enhance your resume!\n")
        
        # Step 1: Check Ollama installation
        if not self.is_ollama_installed():
            if not self.download_ollama():
                print("Setup cannot continue without Ollama.")
                return False
        
        # Step 2: Wait for Ollama to run
        if not self.check_ollama_running():
            if not self.wait_for_ollama_startup():
                print("\nSetup incomplete. Please start Ollama manually and try again.")
                print("Once Ollama is running, Resume AI will work normally.")
                self.mark_setup_complete(ollama_installed=True)
                return False
        
        # Step 3: Pull required models
        if not self.check_and_pull_models():
            print("\nNote: You can still use Resume AI with fewer models.")
            print("Add more models later through Settings.")
        
        # Mark setup complete
        self.mark_setup_complete(ollama_installed=True)
        
        print("\n" + "="*60)
        print("✓ SETUP COMPLETE!")
        print("="*60)
        print("\nResume AI is ready to use!")
        print("Launching app...\n")
        return True


if __name__ == "__main__":
    wizard = SetupWizard()
    if wizard.is_first_run():
        success = wizard.run_setup()
        sys.exit(0 if success else 1)
    else:
        print("Setup already completed.")

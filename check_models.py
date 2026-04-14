#!/usr/bin/env python3
"""
Diagnostic tool to check Ollama model status and load missing models.
Run this if PDF grading fails but TXT grading works.
"""

import sys
from core.llm_client import (
    is_ollama_running, 
    get_available_models, 
    ensure_models_loaded,
    pull_model
)

def main():
    print("=" * 70)
    print("RESUME-AI MODEL DIAGNOSTIC TOOL")
    print("=" * 70)
    
    # Check if Ollama is running
    print("\n1. Checking if Ollama is running...")
    if not is_ollama_running():
        print("   ❌ Ollama is NOT running!")
        print("   💡 Start Ollama with: ollama serve")
        return False
    print("   ✅ Ollama is running")
    
    # Check available models
    print("\n2. Checking available models...")
    models = get_available_models()
    if not models:
        print("   ❌ No models are loaded!")
    else:
        print(f"   ✅ Found {len(models)} model(s):")
        for model in models:
            print(f"      • {model}")
    
    # Check required models
    print("\n3. Checking required models...")
    required_status = ensure_models_loaded()
    
    if required_status["loaded"]:
        print("   ✅ All required models are loaded!")
        print(f"   Status: {required_status['status']}")
    else:
        print("   ❌ Missing required models:")
        for model in required_status["missing_models"]:
            print(f"      • {model}")
        
        # Try to pull missing models
        print("\n4. Attempting to load missing models...")
        for model in required_status["missing_models"]:
            print(f"\n   Loading {model}...")
            print("   (This may take several minutes...)")
            if pull_model(model):
                print(f"   ✅ Successfully loaded {model}")
            else:
                print(f"   ❌ Failed to load {model}")
                print(f"   💡 Try manually: ollama pull {model}")
    
    # Final check
    print("\n5. Final check...")
    final_status = ensure_models_loaded()
    if final_status["loaded"]:
        print("   ✅ All required models are now loaded!")
        print("\n" + "=" * 70)
        print("SUCCESS! You can now grade PDFs without issues.")
        print("=" * 70)
        return True
    else:
        print("   ❌ Some models are still missing. Please load them manually:")
        for model in final_status["missing_models"]:
            print(f"      ollama pull {model}")
        print("\n" + "=" * 70)
        print("Please load the models and try again.")
        print("=" * 70)
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

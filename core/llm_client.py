import requests
import os
import json
import subprocess
import time
import sys
import platform


# Global process handle for Ollama
_ollama_process = None


def start_ollama():
    """
    Start Ollama server subprocess.
    Returns True if successfully started or already running, False otherwise.
    """
    global _ollama_process
    
    # Check if already running
    if is_ollama_running():
        print("✓ Ollama is already running")
        return True
    
    try:
        print("Starting Ollama...")
        
        # Determine the command based on OS
        if platform.system() == "Windows":
            # On Windows, Ollama is typically installed as a service or standalone
            # Try to start the Ollama service or executable
            try:
                # Try starting as a service first
                subprocess.run(["net", "start", "Ollama"], check=False, capture_output=True)
                time.sleep(2)
                if is_ollama_running():
                    print("✓ Ollama service started successfully")
                    return True
            except:
                pass
            
            # Try running the executable directly
            ollama_path = os.environ.get("OLLAMA_PATH", "ollama")
            _ollama_process = subprocess.Popen(
                [ollama_path, "serve"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                creationflags=subprocess.CREATE_NEW_CONSOLE if platform.system() == "Windows" else 0
            )
        else:
            # On macOS/Linux
            _ollama_process = subprocess.Popen(
                ["ollama", "serve"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
        
        # Wait for Ollama to be ready
        print("Waiting for Ollama to be ready...")
        max_attempts = 30
        for attempt in range(max_attempts):
            if is_ollama_running():
                print("✓ Ollama started successfully")
                return True
            time.sleep(1)
        
        print("✗ Ollama failed to start (timeout)")
        return False
        
    except FileNotFoundError:
        print("✗ Ollama executable not found. Please ensure Ollama is installed and in PATH")
        return False
    except Exception as e:
        print(f"✗ Error starting Ollama: {e}")
        return False


def stop_ollama():
    """
    Stop Ollama server subprocess gracefully.
    """
    global _ollama_process
    
    try:
        if platform.system() == "Windows":
            # Try stopping the Ollama service
            subprocess.run(["net", "stop", "Ollama"], check=False, capture_output=True)
        
        if _ollama_process:
            _ollama_process.terminate()
            try:
                _ollama_process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                _ollama_process.kill()
            _ollama_process = None
        
        print("✓ Ollama stopped")
        return True
    except Exception as e:
        print(f"Error stopping Ollama: {e}")
        return False


def is_ollama_running():
    """
    Check if Ollama server is running and responding.
    Returns True if reachable, False otherwise.
    """
    try:
        response = requests.get("http://localhost:11434/api/tags", timeout=2)
        return response.status_code == 200
    except requests.exceptions.RequestException:
        return False


# Model routing for hybrid approach
MODEL_ROUTING = {
    # Mistral 7B - For JSON-critical tasks (must be consistent/valid)
    "parse": "mistral:7b",           # Resume parsing - JSON critical
    "grade": "mistral:7b",           # Resume grading - JSON scores must be consistent
    "changes_summary": "mistral:7b", # Changes summary - JSON array
    
    # Llama3 8B - For quality/creative tasks (paraphrasing, rewriting)
    "polish": "llama3:8b",           # Bullet polishing - needs creativity
    "tailor": "llama3:8b",           # Job tailoring - semantic understanding
    "update": "llama3:8b",           # Experience updater - creative bullet generation
}

def get_model_for_task(task_type: str, explicit_model: str = None) -> str:
    """
    Get the appropriate model for a task.
    
    Args:
        task_type: Type of task (e.g., "parse", "polish", "tailor", "grade")
        explicit_model: If provided, use this model instead of routing
    
    Returns:
        Model name to use
    """
    if explicit_model:
        return explicit_model
    
    return MODEL_ROUTING.get(task_type, os.getenv("OLLAMA_MODEL", "mistral:7b"))


def ask_llm(prompt, model=None, max_tokens=2048, temperature=0.4, task_type=None):
    """
    Query an LLM via Ollama.
    
    Args:
        prompt: The prompt to send
        model: Specific model to use (overrides task_type routing)
        max_tokens: Max tokens to generate
        temperature: Sampling temperature
        task_type: Task classification for intelligent model routing
                  Options: "parse", "grade", "polish", "tailor", "update", "changes_summary"
    
    Returns:
        LLM response text, or None if error
    """
    url = "http://localhost:11434/api/generate"
    
    # Select model: explicit > task_type routing > env var > default
    if model is None:
        model = get_model_for_task(task_type)

    payload = {
        "model": model,
        "prompt": prompt,
        "stream": False,
        "options": {
            "num_predict": max_tokens,
            "temperature": temperature
        },
    }

    try:
        response = requests.post(url, json=payload, timeout=120)
        response.raise_for_status()
        data = response.json()
        return data.get("response", "")
    except requests.exceptions.HTTPError:
        detail = ""
        try:
            detail = response.json().get("error", "")
        except Exception:
            pass
        print(f"Error from Ollama ({response.status_code}): {detail or response.text}")
        return None
    except requests.exceptions.RequestException as e:
        print("Error connecting to Ollama:", e)
        return None

if __name__ == "__main__": 
    from prompts import bullet_polish_prompt, job_tailor_prompt
    from prompts import experience_updater_prompt
    bullet = "Responsible for helping customers"
    prompt = bullet_polish_prompt(bullet)
    result = ask_llm(prompt, task_type="polish")
    print("Bullet Polish (Llama3 8B):")
    print(result)
    print()

    # Test 2 - Job tailor
    resume_section = """
    - Helped customers with their orders and complaints
    - Workedf on improving customer satisfaction
    - Assisted team members with daily tasks
    """

    job_description = """
    We are looking for a Customer Success Manager to drive customer engagement,
    resolve escalated issues, and improve retention rates across our client base.
    Strong communication and data-driven decision making required.
    """
    prompt2 = job_tailor_prompt(resume_section, job_description)
    result2 = ask_llm(prompt2, task_type="tailor")
    print("Job Tailor (Llama3 8B):")
    print(result2)
    print()

    user_input = "I built a Python script that scraped job listings and emailed me daily summaries, saved me like an hour a day"
    prompt3 = experience_updater_prompt(user_input)
    result3 = ask_llm(prompt3, task_type="update")
    print("Experience Updater (Llama3 8B):")
    print(result3)

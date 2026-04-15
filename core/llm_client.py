import requests
import os
import json
import subprocess
import time
import sys
import platform
from collections import defaultdict
from .utils import format_error_message, extract_json_from_response


# Global process handle for Ollama
_ollama_process = None

# Performance tracking
LLM_STATS = defaultdict(list)


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
        
        if platform.system() == "Windows":
            # Windows: Try multiple methods to start Ollama
            
            # Method 1: Try starting as a Windows service
            print("  → Attempting via Windows service...")
            result = subprocess.run(
                ["net", "start", "Ollama"], 
                check=False, 
                capture_output=True,
                timeout=5
            )
            time.sleep(2)
            if is_ollama_running():
                print("✓ Ollama service started successfully")
                return True
            
            # Method 2: Try common Ollama installation paths
            common_paths = [
                os.path.expanduser(r"~\AppData\Local\Programs\Ollama\ollama.exe"),
                os.path.expanduser(r"~\AppData\Local\Programs\Ollama\ollama app.exe"),
                "ollama.exe",  # If in PATH
                "ollama",      # If in PATH
            ]
            
            print("  → Attempting via executable...")
            for ollama_path in common_paths:
                if os.path.exists(ollama_path) or ollama_path in ["ollama.exe", "ollama"]:
                    try:
                        print(f"    Trying: {ollama_path}")
                        _ollama_process = subprocess.Popen(
                            [ollama_path, "serve"],
                            stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE,
                            creationflags=subprocess.CREATE_NEW_CONSOLE
                        )
                        time.sleep(3)
                        
                        # Check if it actually started
                        if is_ollama_running():
                            print(f"✓ Ollama started successfully via: {ollama_path}")
                            return True
                    except Exception as e:
                        print(f"    Failed: {e}")
                        continue
            
            print("✗ Could not start Ollama via any method")
            print("\n⚠️  IMPORTANT: Ollama needs to be running!")
            print("  Open one of these options:")
            print("  1. Run: ollama serve (in a terminal)")
            print("  2. Click the Ollama app icon in Windows")
            print("  3. Run: net start Ollama (if installed as service)")
            return False
            
        else:
            # macOS/Linux
            print("  → Starting via 'ollama serve'...")
            _ollama_process = subprocess.Popen(
                ["ollama", "serve"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
        
        # Wait for Ollama to be ready
        print("Waiting for Ollama to respond...")
        max_attempts = 60  # 60 seconds
        for attempt in range(max_attempts):
            if is_ollama_running():
                print("✓ Ollama started successfully and responding")
                return True
            sys.stdout.write(f"\r  Attempt {attempt + 1}/{max_attempts}...")
            sys.stdout.flush()
            time.sleep(1)
        
        print("\n✗ Ollama failed to start (timeout after 60 seconds)")
        return False
        
    except FileNotFoundError as e:
        print(f"✗ Ollama executable not found: {e}")
        print("\n⚠️  Please install Ollama from https://ollama.ai")
        return False
    except Exception as e:
        print(f"✗ Error starting Ollama: {e}")
        return False


def stop_ollama():
    """
    Stop Ollama server subprocess gracefully.
    Handles both service and process termination.
    """
    global _ollama_process
    
    try:
        stopped = False
        
        # On Windows, try stopping the service first
        if platform.system() == "Windows":
            try:
                result = subprocess.run(
                    ["net", "stop", "Ollama"], 
                    check=False, 
                    capture_output=True,
                    timeout=10
                )
                if result.returncode == 0:
                    print("✓ Ollama service stopped")
                    stopped = True
            except Exception as e:
                print(f"Note: Could not stop Ollama service: {e}")
        
        # Also try to terminate the subprocess we started
        if _ollama_process and _ollama_process.poll() is None:
            try:
                _ollama_process.terminate()
                try:
                    _ollama_process.wait(timeout=5)
                    print("✓ Ollama process terminated gracefully")
                except subprocess.TimeoutExpired:
                    print("⚠ Ollama process not responding, forcing kill...")
                    _ollama_process.kill()
                    _ollama_process.wait(timeout=2)
                    print("✓ Ollama process force-killed")
                stopped = True
            except Exception as e:
                print(f"Error stopping Ollama process: {e}")
            finally:
                _ollama_process = None
        
        # Final check - if still running via taskkill (Windows)
        if platform.system() == "Windows" and is_ollama_running():
            try:
                subprocess.run(
                    ["taskkill", "/IM", "ollama.exe", "/F"],
                    check=False,
                    capture_output=True,
                    timeout=5
                )
                print("✓ Ollama cleaned up via taskkill")
                stopped = True
            except Exception as e:
                print(f"Note: taskkill encountered: {e}")
        
        if stopped:
            print("✓ Ollama shutdown complete")
        else:
            print("✓ Ollama cleanup finished")
        
        return True
        
    except Exception as e:
        print(f"⚠ Error during Ollama shutdown: {e}")
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


def get_available_models():
    """
    Get list of models currently available in Ollama.
    Returns list of model names, or empty list if Ollama is not running.
    """
    try:
        response = requests.get("http://localhost:11434/api/tags", timeout=5)
        if response.status_code == 200:
            data = response.json()
            models = [model.get("name", "") for model in data.get("models", [])]
            return models
        return []
    except Exception as e:
        print(f"Error getting available models: {e}")
        return []


def pull_model(model_name: str) -> bool:
    """
    Pull (download and load) a model from Ollama hub.
    This can take a while for large models.
    
    Args:
        model_name: Model name (e.g., "mistral:7b", "llama3:8b")
    
    Returns:
        True if successful, False otherwise
    """
    try:
        print(f"Pulling model {model_name}...")
        url = "http://localhost:11434/api/pull"
        payload = {"name": model_name, "stream": False}
        
        # This might take a while
        response = requests.post(url, json=payload, timeout=300)
        if response.status_code == 200:
            print(f"✓ Successfully pulled {model_name}")
            return True
        else:
            print(f"✗ Failed to pull {model_name}: {response.text}")
            return False
    except Exception as e:
        print(f"Error pulling model {model_name}: {e}")
        return False


def ensure_models_loaded(required_models: list = None) -> dict:
    """
    Check if required models are loaded, and attempt to pull them if not.
    
    Args:
        required_models: List of model names to check. If None, checks default models.
    
    Returns:
        dict with keys: "running", "available_models", "missing_models", "loaded"
    """
    if required_models is None:
        required_models = ["mistral:7b", "llama3:8b"]
    
    running = is_ollama_running()
    available = get_available_models()
    
    if not running:
        return {
            "running": False,
            "available_models": [],
            "missing_models": required_models,
            "loaded": False,
            "error": "Ollama is not running"
        }
    
    # Extract base model names for comparison (ignore tags like :latest)
    available_base = set(m.split(":")[0] for m in available)
    required_base = set(m.split(":")[0] for m in required_models)
    
    missing = required_base - available_base
    
    return {
        "running": True,
        "available_models": available,
        "missing_models": list(missing),
        "loaded": len(missing) == 0,
        "status": f"Ollama running with {len(available)} model(s): {', '.join(available)}"
    }


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


def ask_llm(prompt, model=None, max_tokens=None, temperature=None, task_type=None):
    """
    Query an LLM via Ollama with task-optimized parameters.
    
    Args:
        prompt: The prompt to send
        model: Specific model to use (overrides task_type)
        max_tokens: Max tokens to generate (overrides task config)
        temperature: Sampling temperature (overrides task config)
        task_type: Task classification for intelligent routing
                  Options: "parse", "grade", "polish", "tailor", "update", "changes_summary"
    
    Returns:
        LLM response text, or None if error
    """
    from .llm_config import get_task_config
    from .llm_cache import get_cached, set_cached
    
    start_time = time.time()
    url = "http://localhost:11434/api/generate"
    
    # Get task-optimized config
    config = get_task_config(task_type)
    
    # Allow explicit overrides
    model = model or config["model"]
    temperature = temperature if temperature is not None else config["temperature"]
    max_tokens = max_tokens or config["max_tokens"]
    request_timeout = config["timeout"]
    
    # Check cache first (before adding system context, so cache key is based on original prompt)
    cache_key = (prompt, task_type or "unknown", model)
    cached_response = get_cached(cache_key)
    if cached_response is not None:
        # Record cache hit timing
        duration = time.time() - start_time
        LLM_STATS[task_type or "unknown"].append(duration)
        if duration > 5:
            print(f"⚠️  Slow cache lookup ({task_type}): {duration:.1f}s")
        return cached_response
    
    # Add system context for specific tasks
    final_prompt = prompt
    if task_type == "polish":
        final_prompt = f"""SYSTEM: You are a professional resume editor. Your task is to ENHANCE an existing, real resume. You are NOT creating fake experience. The resume below is written by a real person based on their actual work experience. Your job is to improve the writing quality, clarity, and impact of their real accomplishments.

{prompt}"""

    payload = {
        "model": model,
        "prompt": final_prompt,
        "stream": False,
        "options": {
            "num_predict": max_tokens,
            "temperature": temperature
        },
    }

    try:
        response = requests.post(url, json=payload, timeout=request_timeout)
        response.raise_for_status()
        data = response.json()
        result = data.get("response", "")
        
        # Cache the response
        set_cached(cache_key, result)
        
        # Record performance metrics
        duration = time.time() - start_time
        LLM_STATS[task_type or "unknown"].append(duration)
        
        # Alert on slow requests
        if duration > 5:
            print(f"⚠️  Slow LLM ({task_type}): {duration:.1f}s")
        
        return result
        
    except requests.exceptions.HTTPError as e:
        if response.status_code == 404:
            print(format_error_message("not_found", model=model))
        else:
            try:
                detail = response.json().get("error", "")
            except Exception:
                detail = response.text
            print(f"Error from Ollama ({response.status_code}): {detail or response.text}")
        return None
    except requests.exceptions.ConnectionError:
        print(format_error_message("connection_failed"))
        return None
    except requests.exceptions.Timeout:
        print(format_error_message("timeout", model=model, timeout=request_timeout))
        return None
    except requests.exceptions.RequestException as e:
        print(f"Error connecting to Ollama: {e}")
        return None


def parse_resume_to_pdf_format(resume_text: str) -> dict:
    """
    Parse a resume text and extract structured data in the exact format needed by generate_resume.py.
    
    This function:
    1. Sends the resume to the LLM with a specialized parsing prompt
    2. Extracts structured JSON data
    3. Validates the JSON structure
    4. Returns the data ready for PDF generation
    
    Args:
        resume_text: The resume content as plain text or formatted text
    
    Returns:
        dict: Resume data in the format:
        {
            "name": str,
            "contact": str (HTML formatted),
            "education": [{"school": str, "dates": str, "detail": str}, ...],
            "technical_skills": [(label, value), ...],
            "work_experience": [{"title": str, "company": str, "dates": str, "bullets": [...]}, ...],
            "projects": [{"name": str, "tech": str, "bullets": [...]}, ...],
            "leadership": [{"title": str, "org": str, "dates": str, "bullets": [...]}, ...]
        }
        
        Returns empty dict on parsing failure.
    """
    from .prompts import parse_resume_to_pdf_format_prompt
    
    print("🔄 Parsing resume with LLM...")
    prompt = parse_resume_to_pdf_format_prompt(resume_text)
    
    # Use Mistral 7B for JSON parsing - it's more reliable with structured output
    response = ask_llm(
        prompt,
        model="mistral:7b",
        max_tokens=4096,
        temperature=0.1  # Lower temperature for more consistent JSON
    )
    
    if not response:
        print("❌ LLM parsing failed - no response")
        return {}
    
    # Extract JSON from response (LLM might include explanation text)
    try:
        try:
            parsed_data = extract_json_from_response(response)
            print("✅ Resume parsed successfully")
            return parsed_data
        except ValueError:
            print("❌ Could not find valid JSON in LLM response")
            print(f"Response preview: {response[:200]}...")
            return {}
    except Exception as e:
        print(f"❌ Error parsing resume: {e}")
        return {}


def parse_resume_and_generate_pdf(resume_text: str, output_path: str = "generated_resume.pdf") -> bool:
    """
    Complete pipeline: Parse resume → Extract structured data → Generate PDF.
    
    Args:
        resume_text: The resume content as text
        output_path: Where to save the generated PDF
    
    Returns:
        bool: True if successful, False otherwise
    """
    from .generate_resume import build_resume
    
    # Step 1: Parse resume
    resume_data = parse_resume_to_pdf_format(resume_text)
    
    if not resume_data:
        print("❌ Resume parsing failed - cannot generate PDF")
        return False
    
    # Step 2: Validate required fields
    required_fields = ["name", "contact"]
    missing = [f for f in required_fields if not resume_data.get(f)]
    
    if missing:
        print(f"⚠️  Warning: Missing required fields: {', '.join(missing)}")
        # This is a warning, not a blocker - continue with partial data
    
    # Step 3: Generate PDF
    try:
        build_resume(resume_data, output_path)
        print(f"✅ PDF generated successfully: {output_path}")
        return True
    except Exception as e:
        print(f"❌ PDF generation failed: {e}")
        return False



def get_llm_stats() -> dict:
    """Get LLM performance statistics."""
    stats = {}
    for task_type, times in LLM_STATS.items():
        if times:
            avg = sum(times) / len(times)
            stats[task_type] = {
                "calls": len(times),
                "avg_time": f"{avg:.2f}s",
                "min_time": f"{min(times):.2f}s",
                "max_time": f"{max(times):.2f}s",
            }
    return stats


def get_cache_stats() -> dict:
    """
    Get cache performance statistics.
    Returns cache hit rate, items cached, and TTL info.
    """
    try:
        from .llm_cache import get_cache_stats as get_cache_stats_from_cache
        return get_cache_stats_from_cache()
    except Exception as e:
        return {"error": f"Could not retrieve cache stats: {e}"}


def get_queue_stats() -> dict:
    """
    Get request queue performance statistics.
    Returns active/queued/processed request counts.
    """
    try:
        from .llm_queue import get_queue_stats as get_queue_stats_from_queue
        return get_queue_stats_from_queue()
    except Exception as e:
        return {"error": f"Could not retrieve queue stats: {e}"}


def get_all_stats() -> dict:
    """Get comprehensive statistics for LLM, cache, and queue."""
    return {
        "llm": get_llm_stats(),
        "cache": get_cache_stats(),
        "queue": get_queue_stats(),
    }


def warmup_models(models: list = None, max_retries: int = 3) -> dict:
    """
    Preload models into Ollama memory for faster first requests.
    
    Args:
        models: List of model names (default: required models)
        max_retries: Times to retry if model fails to warm
    
    Returns:
        dict with warmup status for each model
    """
    if models is None:
        models = ["mistral:7b", "llama3:8b"]
    
    warmup_status = {}
    
    print("\n🔥 Warming up models...")
    print("-" * 50)
    
    for model in models:
        print(f"Warming {model}...", end=" ", flush=True)
        
        for attempt in range(max_retries):
            try:
                # Send minimal request to trigger model loading
                response = ask_llm(
                    ".",  # Minimal prompt
                    model=model,
                    max_tokens=1,
                    temperature=0.0
                )
                
                if response:
                    print("✓")
                    warmup_status[model] = "ready"
                    break
                else:
                    print(".", end="", flush=True)
            except Exception as e:
                print(".", end="", flush=True)
                if attempt < max_retries - 1:
                    time.sleep(1)
        else:
            print("✗")
            warmup_status[model] = "failed"
    
    print("-" * 50)
    
    ready = sum(1 for v in warmup_status.values() if v == "ready")
    print(f"✓ {ready}/{len(models)} models ready\n")
    
    return warmup_status

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

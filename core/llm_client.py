import requests
import os
import json


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

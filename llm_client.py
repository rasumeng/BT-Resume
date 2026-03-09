import requests
import os
from prompts import bullet_polish_prompt, job_tailor_prompt
from prompts import experience_updater_prompt

def ask_llm(prompt):
    url = "http://localhost:11434/api/generate"
    model = os.getenv("OLLAMA_MODEL", "mistral:7b")

    payload = {
    "model": model,
    "prompt": prompt,
    "stream": False,
    "options": {"num_predict": 1024,
                "temperature": 0.4
                },
    }

    try:
        response = requests.post(url, json=payload, timeout=120)
        response.raise_for_status() # raise error if request faield
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
    bullet = "Responsible for helping customers"
    prompt = bullet_polish_prompt(bullet)
    result = ask_llm(prompt)
    print("Bullet Polish:")
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
    result2 = ask_llm(prompt2)
    print("Job Tailor:")
    print(result2)
    print()

    user_input = "I built a Python script that scraped job listings and emailed me daily summaries, saved me like an hour a day"
    prompt3 = experience_updater_prompt(user_input)
    result3 = ask_llm(prompt3)
    print("Experience Updater:")
    print(result3)

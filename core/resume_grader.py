import json
from core.prompts import get_grader_prompt
from core.llm_client import ask_llm

class ResumeGrader:
    def grade(self, resume_text):
        prompt = get_grader_prompt(resume_text)
        print("Grading resume using mistral:7b model...")
        response = ask_llm(prompt, task_type="grade")

        if not response:
            print("ERROR: Failed to get grading response from Mistral (model may not be loaded)")
            print("❌ TIP: Check that mistral:7b is loaded in Ollama by visiting http://localhost:11434/api/tags")
            print("❌ To load mistral:7b, run: ollama pull mistral:7b")
            raise Exception("Grading model (mistral:7b) did not respond. Check Ollama status and make sure mistral:7b is loaded (run 'ollama pull mistral:7b')")
        
        try:
            start = response.find("{")
            end = response.rfind("}") + 1
            if start == -1 or end <= start:
                raise ValueError("No JSON found in response")
            scores = json.loads(response[start:end])
            scores["overall"] = round(
                sum([
                    scores["ats_score"],
                    scores["sections_score"],
                    scores["bullets_score"],
                    scores["keywords_score"]
                ]) / 4, 1
            )
            return scores
        except (json.JSONDecodeError, ValueError) as e:
            print(f"ERROR: Failed to parse grading response as JSON: {e}")
            print(f"Response was: {response[:200]}...")
            raise Exception(f"Failed to parse grading response: {str(e)}")
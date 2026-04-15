import json
from core.prompts import get_grader_prompt
from core.llm_client import ask_llm
from core.utils import format_error_message, extract_json_from_response


class ResumeGrader:
    def grade(self, resume_text):
        prompt = get_grader_prompt(resume_text)
        print("Grading resume using mistral:7b model...")
        response = ask_llm(prompt, task_type="grade")

        if not response:
            model = "mistral:7b"
            print(format_error_message("model_not_loaded", model=model))
            raise Exception(f"Grading model ({model}) did not respond. Check Ollama status and make sure {model} is loaded (run 'ollama pull {model}')")
        
        try:
            parsed = extract_json_from_response(response)
            scores = parsed
            scores["overall"] = round(
                sum([
                    scores["ats_score"],
                    scores["sections_score"],
                    scores["bullets_score"],
                    scores["keywords_score"]
                ]) / 4, 1
            )
            return scores
        except ValueError as e:
            print(f"ERROR: Failed to parse grading response as JSON: {e}")
            print(f"Response was: {response[:200]}...")
            raise Exception(f"Failed to parse grading response: {str(e)}")
import json
from core.prompts import get_grader_prompt
from core.llm_client import ask_llm

class ResumeGrader:
    def grade(self, resume_text):
        prompt = get_grader_prompt(resume_text)
        response = ask_llm(prompt, model="mistral:7b")

        if not response:
            return None
        
        try:
            start = response.find("{")
            end = response.rfind("}") + 1
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
        except json.JSONDecodeError:
            return None
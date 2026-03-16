import os

class AppState:
    def __init__(self):
        self.selected_resume = None
        self.resumes_dir = os.path.join(
            os.path.expanduser("~"), "Documents", "BT-Resume", "resumes"
        )
        os.makedirs(self.resumes_dir, exist_ok=True)
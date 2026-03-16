import customtkinter as ctk
from core.state import AppState
from gui.resumes_panel import ResumesPanel
from gui.bullet_polish_panel import BulletPolishPanel
from gui.job_tailor_panel import JobTailorPanel
from gui.experience_panel import ExperiencePanel

# System theme detection - one line
ctk.set_appearance_mode("system")
ctk.set_default_color_theme("blue")

class App(ctk.CTk):
    
    def __init__(self):
        super().__init__()

        self.title("Beyond The Resume")
        self.geometry("900x600")
        self.minsize(900, 600)
        
        self.app_state = AppState()

        self.sidebar_expanded = True
        self.sidebar_width_expanded = 200
        self.sidebar_width_collapsed = 96

        # allow column 1 to expand
        self.grid_columnconfigure(1, weight=1)

        # allow row 0 to expand
        self.grid_rowconfigure(0, weight=1)

    #Sidebar
        self.sidebar = ctk.CTkFrame(self, width=self.sidebar_width_expanded)
        self.sidebar.grid_propagate(False)
        self.sidebar.grid(row=0, column=0, sticky="ns")
        self.sidebar.grid_rowconfigure(6, weight=1)
        self.sidebar.grid_columnconfigure(0, weight=1)

        header = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        header.grid(row=0, column=0, padx=10, pady=(15, 10), sticky="ew")
        header.grid_columnconfigure(0, weight=1)

        # App Title
        self.sidebar_title = ctk.CTkLabel(header, text="BT Resume", font=("Arial", 20, "bold"))
        self.sidebar_title.grid(row=0, column=0, padx=(10, 0), sticky="w")

        self.toggle_btn = ctk.CTkButton(
            header,
            text="☰",
            width=28,
            height=28,
            command=self.toggle_sidebar,
        )
        self.toggle_btn.grid(row=0, column=1, padx=(6, 0), sticky="e")

        #Buttons
        self.btn_one = ctk.CTkButton(self.sidebar, text="My Resumes", anchor="w", command=lambda: self.show_panel(self.panel_one))
        self.btn_one.grid(row=1, column=0, padx=20, pady=5, sticky="ew")
        
        self.btn_two = ctk.CTkButton(self.sidebar, text="Bullet Polish", anchor="w", command=lambda: self.show_panel(self.panel_two))
        self.btn_two.grid(row=2, column=0, padx=20, pady=5, sticky="ew")

        self.btn_three = ctk.CTkButton(self.sidebar, text="Job Tailor", anchor="w", command=lambda: self.show_panel(self.panel_three))
        self.btn_three.grid(row=3, column=0, padx=20, pady=5, sticky="ew")

        self.btn_four = ctk.CTkButton(self.sidebar, text="Experience", anchor="w", command=lambda: self.show_panel(self.panel_four))
        self.btn_four.grid(row=4, column=0, padx=20, pady=5, sticky="ew")
       
    # main page
        self.content = ctk.CTkFrame(self)
        self.content.grid(row=0, column=1, sticky="nsew")
        self.content.grid_columnconfigure(0, weight=1)
        self.content.grid_rowconfigure(0, weight=1)

    # Panels
        self.panel_one = ResumesPanel(self.content, self.app_state)
        self.panel_two = BulletPolishPanel(self.content, self.app_state)
        self.panel_three = JobTailorPanel(self.content, self.app_state)
        self.panel_four = ExperiencePanel(self.content, self.app_state)

        self.panels = [self.panel_one, self.panel_two, self.panel_three, self.panel_four]

        self.show_panel(self.panel_one)


    def show_panel(self, panel):
        for p in self.panels:
            p.grid_remove()

        panel.grid(sticky="nsew")
        refresh = getattr(panel, "refresh", None)
        if callable(refresh):
            refresh()

    def toggle_sidebar(self):
        self.sidebar_expanded = not self.sidebar_expanded

        if self.sidebar_expanded:
            self.sidebar.configure(width=self.sidebar_width_expanded)
            self.sidebar_title.configure(text="BT Resume", font=("Arial", 20, "bold"))
            self.toggle_btn.configure(text="☰")

            self.btn_one.configure(text="My Resumes", anchor="w")
            self.btn_two.configure(text="Bullet Polish", anchor="w")
            self.btn_three.configure(text="Job Tailor", anchor="w")
            self.btn_four.configure(text="Experience", anchor="w")

            self.btn_one.grid_configure(padx=20)
            self.btn_two.grid_configure(padx=20)
            self.btn_three.grid_configure(padx=20)
            self.btn_four.grid_configure(padx=20)
        else:
            self.sidebar.configure(width=self.sidebar_width_collapsed)
            self.sidebar_title.configure(text="BTR", font=("Arial", 16, "bold"))
            self.toggle_btn.configure(text="☰")

            # Compact labels for collapsed mode.
            self.btn_one.configure(text="R", anchor="center")
            self.btn_two.configure(text="BP", anchor="center")
            self.btn_three.configure(text="JT", anchor="center")
            self.btn_four.configure(text="EX", anchor="center")

            self.btn_one.grid_configure(padx=8)
            self.btn_two.grid_configure(padx=8)
            self.btn_three.grid_configure(padx=8)
            self.btn_four.grid_configure(padx=8)
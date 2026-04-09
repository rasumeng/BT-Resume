import threading
import os
import customtkinter as ctk
from PIL import Image
from core.state import AppState
from gui.design_system import COLORS, FONTS, SPACING, BUTTON_PRIMARY, BUTTON_OUTLINE
from gui.resumes_panel import ResumesPanel
from gui.bullet_polish_panel import BulletPolishPanel
from gui.job_tailor_panel import JobTailorPanel
from gui.experience_panel import ExperiencePanel

# ═════════════════════════════════════════════════════════════════
# APPLY DESIGN SYSTEM TO CUSTOMTKINTER
# ═════════════════════════════════════════════════════════════════
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class App(ctk.CTk):
    
    def __init__(self):
        super().__init__()

        self.title("Beyond The Resume")
        self.geometry("900x600")
        self.minsize(900, 600)
        
        self.app_state = AppState()

        # Grid layout: row 0 = header, row 1 = separator, row 2 = content
        self.grid_columnconfigure(0, weight=0)  # Sidebar column
        self.grid_columnconfigure(1, weight=1)  # Content column (expands)
        self.grid_rowconfigure(2, weight=1)     # Content row (expands)

        # ═══════════════════════════════════════════════════════════════
        # HEADER ROW (spans full width)
        # ═══════════════════════════════════════════════════════════════
        header = ctk.CTkFrame(self, fg_color=COLORS["dark_3"], height=80)
        header.grid(row=0, column=0, columnspan=2, sticky="ew")
        header.grid_propagate(False)
        header.grid_columnconfigure(0, weight=0)  # Logo
        header.grid_columnconfigure(1, weight=0)  # =
        header.grid_columnconfigure(2, weight=0)  # |
        header.grid_columnconfigure(3, weight=1)  # Title (expands)

        # Load and display logo
        try:
            logo_path = os.path.join(os.path.dirname(__file__), "..", "images", "BTR-Logo Transparent.png")
            logo_image = Image.open(logo_path)
            logo_width = 60
            ratio = logo_width / logo_image.width
            logo_height = int(logo_image.height * ratio)
            logo_image = logo_image.resize((logo_width, logo_height), Image.Resampling.LANCZOS)
            self.logo_tk = ctk.CTkImage(light_image=logo_image, dark_image=logo_image, size=(logo_width, logo_height))
            logo_label = ctk.CTkLabel(header, image=self.logo_tk, text="")
            logo_label.grid(row=0, column=0, padx=SPACING["lg"], pady=SPACING["md"], sticky="w")
        except Exception as e:
            print(f"Warning: Could not load logo: {e}")
            logo_label = ctk.CTkLabel(header, text="BTR", font=FONTS["display_md"], text_color=COLORS["cream"])
            logo_label.grid(row=0, column=0, padx=SPACING["lg"], pady=SPACING["md"], sticky="w")

        # Separator "="
        sep_equals = ctk.CTkLabel(header, text="=", font=FONTS["display_md"], text_color=COLORS["gold"])
        sep_equals.grid(row=0, column=1, padx=SPACING["md"], sticky="w")

        # Divider "|"
        sep_pipe = ctk.CTkLabel(header, text="|", font=FONTS["display_md"], text_color=COLORS["gold"])
        sep_pipe.grid(row=0, column=2, padx=SPACING["md"], sticky="w")

        # Dynamic section title
        self.section_title = ctk.CTkLabel(
            header, text="MY RESUMES",
            font=FONTS["display_lg"],
            text_color=COLORS["cream"]
        )
        self.section_title.grid(row=0, column=3, padx=SPACING["lg"], pady=SPACING["md"], sticky="w")

        # ═══════════════════════════════════════════════════════════════
        # HORIZONTAL DIVIDER LINE
        # ═══════════════════════════════════════════════════════════════
        divider = ctk.CTkFrame(self, fg_color=COLORS["gold"], height=1)
        divider.grid(row=1, column=0, columnspan=2, sticky="ew")
        divider.grid_propagate(False)

        # ═══════════════════════════════════════════════════════════════
        # SIDEBAR (left column)
        # ═══════════════════════════════════════════════════════════════
        self.sidebar = ctk.CTkFrame(self, width=160, fg_color=COLORS["dark_3"], border_width=1, border_color=COLORS["gold"])
        self.sidebar.grid(row=2, column=0, sticky="ns")
        self.sidebar.grid_propagate(False)
        self.sidebar.grid_rowconfigure(4, weight=1)
        self.sidebar.grid_columnconfigure(0, weight=1)

        # Navigation buttons
        self.btn_one = ctk.CTkButton(
            self.sidebar, text="My Resumes", anchor="w",
            fg_color="transparent", text_color=COLORS["text_muted"],
            hover_color=COLORS["dark_4"],
            border_color=COLORS["gold"],
            border_width=1,
            command=lambda: self.show_panel(self.panel_one)
        )
        self.btn_one.grid(row=0, column=0, padx=SPACING["lg"], pady=SPACING["sm"], sticky="ew")

        self.btn_two = ctk.CTkButton(
            self.sidebar, text="Bullet Polish", anchor="w",
            fg_color="transparent", text_color=COLORS["text_muted"],
            hover_color=COLORS["dark_4"],
            border_color=COLORS["gold"],
            border_width=1,
            command=lambda: self.show_panel(self.panel_two)
        )
        self.btn_two.grid(row=1, column=0, padx=SPACING["lg"], pady=SPACING["sm"], sticky="ew")

        self.btn_three = ctk.CTkButton(
            self.sidebar, text="Job Tailor", anchor="w",
            fg_color="transparent", text_color=COLORS["text_muted"],
            hover_color=COLORS["dark_4"],
            border_color=COLORS["gold"],
            border_width=1,
            command=lambda: self.show_panel(self.panel_three)
        )
        self.btn_three.grid(row=2, column=0, padx=SPACING["lg"], pady=SPACING["sm"], sticky="ew")

        self.btn_four = ctk.CTkButton(
            self.sidebar, text="Experience", anchor="w",
            fg_color="transparent", text_color=COLORS["text_muted"],
            hover_color=COLORS["dark_4"],
            border_color=COLORS["gold"],
            border_width=1,
            command=lambda: self.show_panel(self.panel_four)
        )
        self.btn_four.grid(row=3, column=0, padx=SPACING["lg"], pady=SPACING["sm"], sticky="ew")

        # ═══════════════════════════════════════════════════════════════
        # MAIN CONTENT AREA (right column)
        # ═══════════════════════════════════════════════════════════════
        self.content = ctk.CTkFrame(self, fg_color=COLORS["dark"])
        self.content.grid(row=2, column=1, sticky="nsew")
        self.content.grid_columnconfigure(0, weight=1)
        self.content.grid_rowconfigure(0, weight=1)

        # Initialize panels
        self.panel_one = ResumesPanel(self.content, self.app_state)
        self.panel_two = BulletPolishPanel(self.content, self.app_state)
        self.panel_three = JobTailorPanel(self.content, self.app_state)
        self.panel_four = ExperiencePanel(self.content, self.app_state)

        self.panels = [self.panel_one, self.panel_two, self.panel_three, self.panel_four]

        self.show_panel(self.panel_one)


    def show_panel(self, panel):
        for p in self.panels:
            p.grid_remove()

        panel.grid(row=0, column=0, sticky="nsew")
        
        # Update section title based on which panel is shown
        if panel == self.panel_one:
            self.section_title.configure(text="MY RESUMES")
        elif panel == self.panel_two:
            self.section_title.configure(text="BULLET POLISH")
        elif panel == self.panel_three:
            self.section_title.configure(text="JOB TAILOR")
        elif panel == self.panel_four:
            self.section_title.configure(text="EXPERIENCE UPDATER")
        
        # Thread the refresh to prevent UI freezing
        refresh = getattr(panel, "refresh", None)
        if callable(refresh):
            thread = threading.Thread(target=refresh, daemon=True)
            thread.start()
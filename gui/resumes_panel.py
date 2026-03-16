import os
import io
import fitz
import shutil
import threading
import tkinter as tk
from PIL import Image, ImageTk
import customtkinter as ctk
from tkinter import filedialog

class ResumesPanel(ctk.CTkFrame):
    def __init__(self, parent, state):
        super().__init__(parent)
        self.state = state

        # Outer grid: col 0 = sidebar, col 1 = preview; row 1 expands
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=4)
        self.grid_rowconfigure(1, weight=1)

        title = ctk.CTkLabel(self, text="My Resumes")
        title.grid(row=0, column=0, padx=20, pady=10, sticky="w")

        # --- Sidebar: all left-side controls in one frame, anchored to top ---
        self.sidebar = ctk.CTkFrame(self, fg_color="transparent")
        self.sidebar.grid(row=1, column=0, sticky="new", padx=10, pady=5)
        self.sidebar.grid_columnconfigure(0, weight=1)

        self.resume_list = ctk.CTkScrollableFrame(self.sidebar, height=100)
        self.resume_list.grid(row=0, column=0, sticky="ew", pady=5)

        add_btn = ctk.CTkButton(self.sidebar, text="+ Add Resume", command=self.add_resume)
        add_btn.grid(row=1, column=0, pady=10, sticky="ew")

        grade_label = ctk.CTkLabel(self.sidebar, text="Resume Grade")
        grade_label.grid(row=2, column=0, pady=(10, 0), sticky="w")

        self.grade_frame = ctk.CTkFrame(self.sidebar)
        self.grade_frame.grid(row=3, column=0, pady=5, sticky="ew")
        self.grade_frame.grid_columnconfigure(0, weight=0)
        self.grade_frame.grid_columnconfigure(1, weight=1)
        self.grade_frame.grid_columnconfigure(2, weight=0)

        grade_btn = ctk.CTkButton(self.sidebar, text="+ Grade Resume", command=self.grade_resume)
        grade_btn.grid(row=4, column=0, pady=10, sticky="ew")

        # Score bars
        self.bar_ats, self.lbl_ats = self.add_score_row(self.grade_frame, "ATS", 0)
        self.bar_sections, self.lbl_sections = self.add_score_row(self.grade_frame, "Sections", 1)
        self.bar_bullets, self.lbl_bullets = self.add_score_row(self.grade_frame, "Bullets", 2)
        self.bar_keywords, self.lbl_keywords = self.add_score_row(self.grade_frame, "Keywords", 3)

        self.lbl_overall = ctk.CTkLabel(self.grade_frame, text="Overall: --")
        self.lbl_overall.grid(row=4, column=0, columnspan=3, pady=(5, 10))

        # --- Preview panel ---
        self.preview = ctk.CTkFrame(self)
        self.preview.grid(row=1, column=1, padx=20, pady=10, sticky="nsew")

        self._pages = []
        self._page_tk_imgs = []
        self._zoom = 1.0
        self._zoom_debounce = None
        self._pan_x = 0
        self._pan_y = 0
        self._pan_start = (0, 0)
        self._content_w = 0
        self._content_h = 0

        self._canvas = tk.Canvas(self.preview, bg="#1a1a1a", highlightthickness=0)
        self._canvas.pack(fill="both", expand=True)
        self._canvas.bind("<MouseWheel>", self._on_zoom)
        self._canvas.bind("<ButtonPress-1>", self._on_pan_start)
        self._canvas.bind("<B1-Motion>", self._on_pan_move)
        self.preview.bind("<Configure>", self._on_preview_resize)

        self.load_resume_list()

    def refresh(self):
        self.load_resume_list()

    def load_resume_list(self): 
        for widget in self.resume_list.winfo_children():
            widget.destroy()
        # scans self.state.resumes_dir
        for file in os.listdir(self.state.resumes_dir):
            if file.endswith(".pdf"):
                display_name = file[:-4]
                display_name = display_name if len(display_name) <= 30 else display_name[:27] + "..."
                filepath = os.path.join(self.state.resumes_dir, file)
                btn = ctk.CTkButton(self.resume_list, text=display_name, anchor="w", command=lambda p=filepath: self.select_resume(p))
                btn.pack(fill="x", pady=2)
        # creates a button per PDF in self.resume_list


    def add_resume(self):
        # File dialog
        file_path = filedialog.askopenfilename(filetypes=[("PDF files", "*.pdf")])

        if not file_path:
            return
        
        filename = os.path.basename(file_path)

        destination = os.path.join(self.state.resumes_dir, filename)
        # copy file
        shutil.copy(file_path, destination)

        # call load_resume_list()
        self.load_resume_list()
        

    def select_resume(self, filepath):
        self.state.selected_resume = filepath

        doc = fitz.open(filepath)
        self._pages = []
        for page in doc:
            mat = fitz.Matrix(2.0, 2.0)
            pix = page.get_pixmap(matrix=mat)
            image_data = pix.tobytes("png")
            img = Image.open(io.BytesIO(image_data))
            img.load()
            self._pages.append(img)
        doc.close()

        self._zoom = 1.0
        self._pan_x = 0
        self._pan_y = 0
        self._redraw_preview()

    def _on_preview_resize(self, event):
        self._redraw_preview()

    def _redraw_preview(self, resample=Image.LANCZOS):
        if not self._pages:
            return

        w = self._canvas.winfo_width()
        h = self._canvas.winfo_height()
        if w <= 1 or h <= 1:
            return

        PADDING = 12
        page_w = self._pages[0].size[0]
        fit_ratio = (w - PADDING * 2) / page_w
        scale = fit_ratio * self._zoom

        # Compute full rendered content bounds for pan clamping.
        self._content_w = max(1, int(page_w * scale))
        self._content_h = PADDING
        for img in self._pages:
            page_h = max(1, int(img.size[1] * scale))
            self._content_h += page_h + PADDING

        self._pan_x, self._pan_y = self._clamp_pan(self._pan_x, self._pan_y)

        self._canvas.delete("all")
        self._page_tk_imgs = []

        cx = w // 2 + self._pan_x
        y = PADDING + self._pan_y
        for img in self._pages:
            pw, ph = img.size
            new_w = max(1, int(pw * scale))
            new_h = max(1, int(ph * scale))
            resized = img.resize((new_w, new_h), resample)
            tk_img = ImageTk.PhotoImage(resized)
            self._page_tk_imgs.append(tk_img)
            self._canvas.create_image(cx, y, anchor="n", image=tk_img)
            y += new_h + PADDING

        self._canvas.configure(scrollregion=self._canvas.bbox("all"))

    def _on_zoom(self, event):
        if not self._pages:
            return
        factor = 1.1 if event.delta > 0 else 0.9
        self._zoom = max(0.3, min(5.0, self._zoom * factor))
        self._redraw_preview(resample=Image.BILINEAR)
        if self._zoom_debounce:
            self.after_cancel(self._zoom_debounce)
        self._zoom_debounce = self.after(150, lambda: self._redraw_preview(resample=Image.LANCZOS))

    def _on_pan_start(self, event):
        self._pan_start = (event.x - self._pan_x, event.y - self._pan_y)

    def _on_pan_move(self, event):
        if not self._pages:
            return
        old_pan_x, old_pan_y = self._pan_x, self._pan_y
        target_pan_x = event.x - self._pan_start[0]
        target_pan_y = event.y - self._pan_start[1]
        self._pan_x, self._pan_y = self._clamp_pan(target_pan_x, target_pan_y)
        dx = self._pan_x - old_pan_x
        dy = self._pan_y - old_pan_y
        # Shift all items by the delta — no re-render needed
        for item_id in self._canvas.find_all():
            x, y = self._canvas.coords(item_id)
            self._canvas.coords(item_id, x + dx, y + dy)

    def _clamp_pan(self, pan_x, pan_y):
        w = self._canvas.winfo_width()
        h = self._canvas.winfo_height()
        if w <= 1 or h <= 1:
            return pan_x, pan_y

        padding = 12

        # Keep horizontal edges attached when content is wider than viewport.
        if self._content_w <= (w - 2 * padding):
            pan_x = 0
        else:
            x_limit = (self._content_w - (w - 2 * padding)) / 2
            pan_x = max(-x_limit, min(x_limit, pan_x))

        # Keep top/bottom within viewport when content is taller than viewport.
        if self._content_h <= (h - 2 * padding):
            pan_y = 0
        else:
            min_pan_y = h - 2 * padding - self._content_h
            pan_y = max(min_pan_y, min(0, pan_y))

        return pan_x, pan_y

    def add_score_row(self, parent, label_text, row):
        label = ctk.CTkLabel(parent, text=label_text, width=20, anchor="w")
        label.grid(row=row, column=0, padx=(5,5), pady=1, sticky="w")

        bar = ctk.CTkProgressBar(parent, height=8)
        bar.set(0)
        bar.grid(row=row, column=1, padx=5, pady=1, sticky="ew")

        score_label = ctk.CTkLabel(parent, text="--/10", width=20)
        score_label.grid(row=row, column=2, padx=(5,5), pady=1)

        return bar, score_label

    def grade_resume(self):
        if not self.state.selected_resume:
            return # Do nun if no resume selected
        
        thread = threading.Thread(target=self._run_grader)
        thread.daemon = True
        thread.start()

    def _run_grader(self):
        # this runs off the main thread
        from core.resume_grader import ResumeGrader
        from core.input_parser import load_pdf

        text = load_pdf(self.state.selected_resume)
        grader = ResumeGrader()
        scores = grader.grade(text)

        if scores:
            self.after(0, lambda: self._update_scores(scores))

    def _update_scores(self, scores):
        # This runs back on the main thread via after()
        self.bar_ats.set(scores["ats_score"] / 10)
        self.lbl_ats.configure(text=f"{scores['ats_score']}/10")

        self.bar_sections.set(scores["sections_score"]/10)
        self.lbl_sections.configure(text=f"{scores['sections_score']}/10")

        self.bar_bullets.set(scores["bullets_score"] / 10)
        self.lbl_bullets.configure(text=f"{scores['bullets_score']}/10")

        self.bar_keywords.set(scores["keywords_score"] / 10)
        self.lbl_keywords.configure(text=f"{scores['keywords_score']}/10")

    
        # repeat for others...
        self.lbl_overall.configure(text=f"Overall: {scores['overall']}")


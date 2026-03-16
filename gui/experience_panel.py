import json
import os
import re
import threading
import customtkinter as ctk
from tkinter import filedialog

from core.llm_client import ask_llm
from core.output_builder import append_experience_entry
from core.prompts import experience_updater_prompt


SECTIONS = ["WORK EXPERIENCE", "PROJECTS", "LEADERSHIP", "CERTIFICATIONS", "VOLUNTEERING"]


class ExperiencePanel(ctk.CTkFrame):
	def __init__(self, parent, state):
		super().__init__(parent)
		self.state = state
		self._is_generating = False
		self._bullet_vars = []
		self._bullet_texts = []

		self.grid_columnconfigure(0, weight=1)
		self.grid_rowconfigure(2, weight=1)

		title = ctk.CTkLabel(self, text="Experience Updater", font=("Arial", 22, "bold"))
		title.grid(row=0, column=0, padx=20, pady=(12, 8), sticky="w")

		input_frame = ctk.CTkFrame(self)
		input_frame.grid(row=1, column=0, padx=20, pady=(0, 10), sticky="ew")
		input_frame.grid_columnconfigure(0, weight=1)

		desc_label = ctk.CTkLabel(input_frame, text="Describe your experience:")
		desc_label.grid(row=0, column=0, padx=10, pady=(10, 6), sticky="w")

		self.experience_text = ctk.CTkTextbox(input_frame, height=120, wrap="word")
		self.experience_text.grid(row=1, column=0, padx=10, pady=(0, 10), sticky="ew")

		action_row = ctk.CTkFrame(input_frame, fg_color="transparent")
		action_row.grid(row=2, column=0, padx=10, pady=(0, 10), sticky="ew")
		action_row.grid_columnconfigure(1, weight=1)

		section_label = ctk.CTkLabel(action_row, text="Section:")
		section_label.grid(row=0, column=0, padx=(0, 8), sticky="w")

		self.section_dropdown = ctk.CTkOptionMenu(action_row, values=SECTIONS, width=190)
		self.section_dropdown.set(SECTIONS[0])
		self.section_dropdown.grid(row=0, column=1, padx=(0, 8), sticky="w")

		self.generate_btn = ctk.CTkButton(action_row, text="Generate Bullets", command=self.generate_bullets)
		self.generate_btn.grid(row=0, column=2, sticky="e")

		bullets_frame = ctk.CTkFrame(self)
		bullets_frame.grid(row=2, column=0, padx=20, pady=(0, 10), sticky="nsew")
		bullets_frame.grid_rowconfigure(1, weight=1)
		bullets_frame.grid_columnconfigure(0, weight=1)
		bullets_frame.grid_columnconfigure(1, weight=0)

		bullets_label = ctk.CTkLabel(bullets_frame, text="Generated Bullets - select the ones to keep")
		bullets_label.grid(row=0, column=0, padx=10, pady=(10, 6), sticky="w")

		bulk_actions = ctk.CTkFrame(bullets_frame, fg_color="transparent")
		bulk_actions.grid(row=0, column=1, padx=(0, 10), pady=(10, 6), sticky="e")

		self.select_all_btn = ctk.CTkButton(bulk_actions, text="Select All", width=90, command=self.select_all_bullets)
		self.select_all_btn.grid(row=0, column=0, padx=(0, 6))

		self.clear_all_btn = ctk.CTkButton(bulk_actions, text="Clear All", width=90, command=self.clear_all_bullets)
		self.clear_all_btn.grid(row=0, column=1)

		self.bullets_list = ctk.CTkScrollableFrame(bullets_frame, height=170)
		self.bullets_list.grid(row=1, column=0, padx=10, pady=(0, 10), sticky="nsew")
		self._set_generated_bullets([])

		bottom = ctk.CTkFrame(self)
		bottom.grid(row=3, column=0, padx=20, pady=(0, 12), sticky="ew")
		bottom.grid_columnconfigure(1, weight=1)
		bottom.grid_columnconfigure(3, weight=1)

		title_label = ctk.CTkLabel(bottom, text="Experience Title:")
		title_label.grid(row=0, column=0, padx=(10, 8), pady=(10, 6), sticky="w")

		self.entry_title = ctk.CTkEntry(bottom, placeholder_text="Company, project, or role")
		self.entry_title.grid(row=0, column=1, padx=(0, 10), pady=(10, 6), sticky="ew")

		resume_label = ctk.CTkLabel(bottom, text="Add to Resume:")
		resume_label.grid(row=1, column=0, padx=(10, 8), pady=(0, 10), sticky="w")

		self.resume_dropdown = ctk.CTkOptionMenu(bottom, values=["No resumes found"], width=220)
		self.resume_dropdown.grid(row=1, column=1, padx=(0, 10), pady=(0, 10), sticky="w")

		self.add_btn = ctk.CTkButton(bottom, text="Add to Resume", command=self.add_to_resume)
		self.add_btn.grid(row=1, column=2, padx=(0, 8), pady=(0, 10), sticky="e")

		self.create_new_btn = ctk.CTkButton(bottom, text="Create New from Entry", command=self.create_new_from_entry)
		self.create_new_btn.grid(row=1, column=3, padx=(0, 10), pady=(0, 10), sticky="e")

		self.status_label = ctk.CTkLabel(bottom, text="Describe an experience, then generate bullets.")
		self.status_label.grid(row=2, column=0, columnspan=4, padx=10, pady=(0, 10), sticky="w")

		self.load_resume_options()

	def refresh(self):
		self.load_resume_options()

	def load_resume_options(self):
		files = sorted([f[:-4] for f in os.listdir(self.state.resumes_dir) if f.lower().endswith(".pdf")])
		values = files or ["No resumes found"]
		self.resume_dropdown.configure(values=values)
		self.resume_dropdown.set(values[0])

	def generate_bullets(self):
		if self._is_generating:
			return

		experience = self.experience_text.get("1.0", "end").strip()
		if not experience:
			self.status_label.configure(text="Describe your experience first.")
			return

		self._is_generating = True
		self.generate_btn.configure(state="disabled", text="Generating...")
		self.status_label.configure(text="Generating bullet variations...")

		thread = threading.Thread(target=self._run_generate, args=(experience,), daemon=True)
		thread.start()

	def _run_generate(self, experience):
		try:
			prompt = experience_updater_prompt(experience)
			raw = ask_llm(prompt)
			bullets = self._parse_generated_bullets(raw)
			if not bullets:
				raise ValueError("No bullets were returned. Try adding more detail.")
			self.after(0, lambda b=bullets: self._on_generate_success(b))
		except Exception as exc:
			msg = str(exc)
			self.after(0, lambda m=msg: self._on_generate_error(m))

	def _on_generate_success(self, bullets):
		self._is_generating = False
		self.generate_btn.configure(state="normal", text="Generate Bullets")
		self._set_generated_bullets(bullets)
		self.status_label.configure(text="Generated bullets. Select the ones you want to keep.")

	def _on_generate_error(self, error_msg):
		self._is_generating = False
		self.generate_btn.configure(state="normal", text="Generate Bullets")
		self._set_generated_bullets([])
		self.status_label.configure(text=f"Generate failed: {error_msg}")

	def _set_generated_bullets(self, bullets):
		for widget in self.bullets_list.winfo_children():
			widget.destroy()

		self._bullet_vars = []
		self._bullet_texts = bullets

		if not bullets:
			placeholder = ctk.CTkLabel(self.bullets_list, text="No bullets yet.", anchor="w")
			placeholder.pack(fill="x", padx=4, pady=4)
			return

		for bullet in bullets:
			var = ctk.BooleanVar(value=True)
			check = ctk.CTkCheckBox(self.bullets_list, text=bullet, variable=var)
			check.pack(fill="x", padx=4, pady=4, anchor="w")
			self._bullet_vars.append(var)

	def select_all_bullets(self):
		for var in self._bullet_vars:
			var.set(True)

	def clear_all_bullets(self):
		for var in self._bullet_vars:
			var.set(False)

	def _parse_generated_bullets(self, raw):
		if not raw:
			return []

		text = raw.strip()

		try:
			data = json.loads(text)
			if isinstance(data, list):
				cleaned = [self._normalize_bullet(str(item)) for item in data if str(item).strip()]
				return cleaned[:6]
		except Exception:
			pass

		lines = []
		for line in text.splitlines():
			stripped = line.strip()
			if not stripped:
				continue
			if stripped[0].isdigit() and len(stripped) > 2 and stripped[1] in ".)":
				stripped = stripped[2:].strip()
			lines.append(self._normalize_bullet(stripped))

		deduped = []
		seen = set()
		for line in lines:
			key = line.lower()
			if key not in seen:
				seen.add(key)
				deduped.append(line)
		return deduped[:6]

	def _normalize_bullet(self, text):
		bullet = re.sub(r"^[-*●\s]+", "", text).strip()
		return f"- {bullet}" if bullet else ""

	def _selected_bullets(self):
		selected = []
		for idx, var in enumerate(self._bullet_vars):
			if var.get() and idx < len(self._bullet_texts):
				selected.append(self._bullet_texts[idx])
		return selected

	def _selected_resume_path(self):
		resume_name = self.resume_dropdown.get()
		if not resume_name or resume_name == "No resumes found":
			return None
		return os.path.join(self.state.resumes_dir, f"{resume_name}.pdf")

	def add_to_resume(self):
		resume_path = self._selected_resume_path()
		if not resume_path or not os.path.exists(resume_path):
			self.status_label.configure(text="Select a valid resume first.")
			return

		title = self.entry_title.get().strip()
		if not title:
			self.status_label.configure(text="Enter an experience title first.")
			return

		bullets = self._selected_bullets()
		if not bullets:
			self.status_label.configure(text="Select at least one generated bullet.")
			return

		section = self.section_dropdown.get().strip().upper()
		try:
			append_experience_entry(resume_path, section, title, bullets)
			self.status_label.configure(text=f"Added entry to {os.path.basename(resume_path)}")
			self.load_resume_options()
		except Exception as exc:
			self.status_label.configure(text=f"Add failed: {exc}")

	def create_new_from_entry(self):
		resume_path = self._selected_resume_path()
		if not resume_path or not os.path.exists(resume_path):
			self.status_label.configure(text="Select a valid resume first.")
			return

		title = self.entry_title.get().strip()
		if not title:
			self.status_label.configure(text="Enter an experience title first.")
			return

		bullets = self._selected_bullets()
		if not bullets:
			self.status_label.configure(text="Select at least one generated bullet.")
			return

		current_name = os.path.splitext(os.path.basename(resume_path))[0]
		save_path = filedialog.asksaveasfilename(
			title="Create New Resume from Entry",
			defaultextension=".pdf",
			initialdir=self.state.resumes_dir,
			initialfile=f"{current_name}_updated.pdf",
			filetypes=[("PDF files", "*.pdf")],
		)
		if not save_path:
			return

		section = self.section_dropdown.get().strip().upper()
		try:
			append_experience_entry(resume_path, section, title, bullets, output_path=save_path)
			self.status_label.configure(text=f"Created: {os.path.basename(save_path)}")
			self.load_resume_options()
		except Exception as exc:
			self.status_label.configure(text=f"Create failed: {exc}")

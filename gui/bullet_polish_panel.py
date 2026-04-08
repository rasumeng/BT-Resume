import os
import json
import re
import threading
import customtkinter as ctk
from tkinter import filedialog, messagebox

from core.input_parser import load_pdf, parse_section, parse_subsections
from core.output_builder import build_resume
from core.pdf_generator import generate_pdf
from core.llm_client import ask_llm
from core.prompts import get_changes_summary_prompt


class BulletPolishPanel(ctk.CTkFrame):
	def __init__(self, parent, state):
		super().__init__(parent)
		self.state = state
		self._is_polishing = False
		self._original_formatted_text = ""

		self.grid_columnconfigure(0, weight=1)
		self.grid_columnconfigure(1, weight=1)
		self.grid_columnconfigure(0, uniform="pane")
		self.grid_columnconfigure(1, uniform="pane")
		self.grid_rowconfigure(1, weight=1)

		title = ctk.CTkLabel(self, text="Bullet Polish", font=("Arial", 22, "bold"))
		title.grid(row=0, column=0, padx=(20, 10), pady=12, sticky="w")

		controls = ctk.CTkFrame(self, fg_color="transparent")
		controls.grid(row=0, column=1, padx=(10, 20), pady=12, sticky="e")
		controls.grid_columnconfigure(1, weight=1)

		resume_label = ctk.CTkLabel(controls, text="Resume:")
		resume_label.grid(row=0, column=0, padx=(0, 8), sticky="e")

		self.resume_dropdown = ctk.CTkOptionMenu(
			controls,
			values=["No resumes found"],
			command=self.on_resume_selected,
			width=220,
		)
		self.resume_dropdown.grid(row=0, column=1, padx=(0, 8), sticky="ew")

		self.polish_btn = ctk.CTkButton(
			controls,
			text="Polish Resume",
			command=self.polish_resume,
		)
		self.polish_btn.grid(row=0, column=2, sticky="e")

		original_frame = ctk.CTkFrame(self)
		original_frame.grid(row=1, column=0, padx=(20, 10), pady=(0, 10), sticky="nsew")
		original_frame.grid_rowconfigure(1, weight=1)
		original_frame.grid_columnconfigure(0, weight=1)

		original_label = ctk.CTkLabel(original_frame, text="Original")
		original_label.grid(row=0, column=0, padx=10, pady=(10, 6), sticky="w")

		self.original_text = ctk.CTkTextbox(original_frame, wrap="word")
		self.original_text.grid(row=1, column=0, padx=10, pady=(0, 10), sticky="nsew")
		self.original_text.configure(state="disabled")

		polished_frame = ctk.CTkFrame(self)
		polished_frame.grid(row=1, column=1, padx=(10, 20), pady=(0, 10), sticky="nsew")
		polished_frame.grid_rowconfigure(1, weight=1)
		polished_frame.grid_columnconfigure(0, weight=1)

		polished_label = ctk.CTkLabel(polished_frame, text="Polished")
		polished_label.grid(row=0, column=0, padx=10, pady=(10, 6), sticky="w")

		self.polished_text = ctk.CTkTextbox(polished_frame, wrap="word")
		self.polished_text.grid(row=1, column=0, padx=10, pady=(0, 10), sticky="nsew")

		summary_frame = ctk.CTkFrame(self)
		summary_frame.grid(row=3, column=0, columnspan=2, padx=20, pady=(0, 10), sticky="ew")
		summary_frame.grid_columnconfigure(0, weight=1)

		summary_label = ctk.CTkLabel(summary_frame, text="Changes Summary")
		summary_label.grid(row=0, column=0, padx=10, pady=(8, 4), sticky="w")

		self.summary_box = ctk.CTkTextbox(summary_frame, height=100, wrap="word")
		self.summary_box.grid(row=1, column=0, padx=10, pady=(0, 10), sticky="ew")
		self.summary_box.configure(state="disabled")

		footer = ctk.CTkFrame(self, fg_color="transparent")
		footer.grid(row=4, column=0, columnspan=2, padx=20, pady=(0, 12), sticky="ew")
		footer.grid_columnconfigure(0, weight=1)

		self.status_label = ctk.CTkLabel(footer, text="Select a resume, then click Polish Resume.")
		self.status_label.grid(row=0, column=0, sticky="w")

		btn_row = ctk.CTkFrame(footer, fg_color="transparent")
		btn_row.grid(row=0, column=1, sticky="e")

		self.save_new_btn = ctk.CTkButton(btn_row, text="Save as New", command=self.save_as_new)
		self.save_new_btn.grid(row=0, column=0, padx=(0, 8))

		self.replace_btn = ctk.CTkButton(btn_row, text="Replace Original", command=self.replace_original)
		self.replace_btn.grid(row=0, column=1)

		self._set_save_buttons_enabled(False)
		self.load_resume_options()

	def refresh(self):
		# Keep dropdown synced with files added or overwritten in other panels.
		self.load_resume_options()

	def load_resume_options(self):
		files = sorted([f[:-4] for f in os.listdir(self.state.resumes_dir) if f.lower().endswith(".pdf")])
		values = files or ["No resumes found"]
		self.resume_dropdown.configure(values=values)
		self.resume_dropdown.set(values[0])
		self.on_resume_selected(values[0])

	def on_resume_selected(self, resume_name):
		if resume_name == "No resumes found":
			self._set_original_text("")
			self._set_polished_text("")
			self._update_summary([])
			self._set_save_buttons_enabled(False)
			self.status_label.configure(text="Add a PDF resume first in My Resumes.")
			return

		path = self._selected_resume_path()
		if not path or not os.path.exists(path):
			self._set_original_text("")
			self._set_polished_text("")
			self._update_summary([])
			self._set_save_buttons_enabled(False)
			self.status_label.configure(text="Selected resume was not found.")
			return

		try:
			text = load_pdf(path)
		except Exception as exc:
			self._set_original_text("")
			self._set_polished_text("")
			self._update_summary([])
			self._set_save_buttons_enabled(False)
			self.status_label.configure(text=f"Failed to load resume: {exc}")
			return

		sections = parse_section(text)
		formatted_original = self._format_original_sections(sections) if sections else text.strip()
		self._original_formatted_text = formatted_original
		self._set_original_text(formatted_original)
		self._set_polished_text("")
		self._update_summary([])
		self._set_save_buttons_enabled(False)
		self.status_label.configure(text="Ready to polish.")

	def polish_resume(self):
		if self._is_polishing:
			return

		path = self._selected_resume_path()
		if not path or not os.path.exists(path):
			self.status_label.configure(text="Pick a valid resume first.")
			return

		self._is_polishing = True
		self.polish_btn.configure(state="disabled", text="Polishing...")
		self._set_save_buttons_enabled(False)
		self.status_label.configure(text="Polishing bullets... this can take up to a minute.")

		thread = threading.Thread(target=self._run_polish, args=(path,), daemon=True)
		thread.start()

	def _run_polish(self, path):
		try:
			original_text = load_pdf(path)
			sections = parse_section(original_text)
			if not sections:
				raise ValueError("Could not detect resume sections. Try a resume with clear section headers like Experience, Projects, or Skills.")
			formatted_original = self._format_original_sections(sections).strip()
			polished_sections = build_resume(sections, None)
			polished_text = self._sections_to_text(polished_sections)
			if not polished_text.strip():
				raise ValueError("Polish returned empty output. Check Ollama/model availability and try again.")
			changes_prompt = get_changes_summary_prompt(formatted_original, polished_text)
			changes_raw = ask_llm(changes_prompt)
			changes = self._parse_changes_summary(changes_raw)
			self.after(0, lambda p=polished_text, o=formatted_original, c=changes: self._on_polish_success(p, o, c))
		except Exception as exc:
			error_msg = str(exc)
			self.after(0, lambda msg=error_msg: self._on_polish_error(msg))

	def _on_polish_success(self, polished_text, formatted_original, changes):
		self._is_polishing = False
		self.polish_btn.configure(state="normal", text="Polish Resume")
		self._set_polished_text(polished_text)
		self._update_summary(changes)
		self._set_save_buttons_enabled(bool(polished_text.strip()))
		if polished_text.strip() == formatted_original.strip():
			self.status_label.configure(text="Polish finished, but output is mostly unchanged. We can tune the prompt/model together.")
		else:
			self.status_label.configure(text="Polish complete. Review and save.")

	def _on_polish_error(self, error_msg):
		self._is_polishing = False
		self.polish_btn.configure(state="normal", text="Polish Resume")
		self._update_summary([])
		self._set_save_buttons_enabled(False)
		self.status_label.configure(text=f"Polish failed: {error_msg}")

	def _parse_changes_summary(self, raw):
		if not raw:
			return []

		text = raw.strip()
		try:
			data = json.loads(text)
			if isinstance(data, list):
				return [str(item).strip() for item in data if str(item).strip()][:8]
		except Exception:
			pass

		match = re.search(r"\[[\s\S]*\]", text)
		if match:
			try:
				data = json.loads(match.group(0))
				if isinstance(data, list):
					return [str(item).strip() for item in data if str(item).strip()][:8]
			except Exception:
				pass

		return []

	def _update_summary(self, changes):
		self.summary_box.configure(state="normal")
		self.summary_box.delete("1.0", "end")
		if changes:
			lines = [f"- {change}" for change in changes]
			self.summary_box.insert("1.0", "\n".join(lines))
		else:
			self.summary_box.insert("1.0", "No summary yet.")
		self.summary_box.configure(state="disabled")

	def save_as_new(self):
		polished = self.polished_text.get("1.0", "end").strip()
		if not polished:
			self.status_label.configure(text="No polished resume content to save.")
			return

		current_name = self.resume_dropdown.get()
		default_name = f"{current_name}_polished.pdf" if current_name and current_name != "No resumes found" else "resume_polished.pdf"
		save_path = filedialog.asksaveasfilename(
			title="Save Polished Resume As",
			defaultextension=".pdf",
			initialdir=self.state.resumes_dir,
			initialfile=default_name,
			filetypes=[("PDF files", "*.pdf")],
		)
		if not save_path:
			return

		self._save_polished_to_path(save_path)

	def replace_original(self):
		polished = self.polished_text.get("1.0", "end").strip()
		if not polished:
			self.status_label.configure(text="No polished resume content to save.")
			return

		path = self._selected_resume_path()
		if not path:
			self.status_label.configure(text="Select a resume first.")
			return

		confirmed = messagebox.askyesno(
			"Replace Original Resume",
			"This will overwrite the selected PDF. Continue?",
		)
		if not confirmed:
			return

		self._save_polished_to_path(path)

	def _save_polished_to_path(self, path):
		try:
			polished_text = self.polished_text.get("1.0", "end").strip()
			polished_sections = parse_section(polished_text)
			if not polished_sections:
				self.status_label.configure(text="Could not parse polished content into sections.")
				return
			generate_pdf(polished_sections, path)
			self.status_label.configure(text=f"Saved: {os.path.basename(path)}")
			self.load_resume_options()
		except Exception as exc:
			self.status_label.configure(text=f"Save failed: {exc}")

	def _selected_resume_path(self):
		resume_name = self.resume_dropdown.get()
		if not resume_name or resume_name == "No resumes found":
			return None
		return os.path.join(self.state.resumes_dir, f"{resume_name}.pdf")

	def _sections_to_text(self, sections):
		chunks = []
		for header, content in sections.items():
			chunks.append(header)
			# Skip dict values (like _CONTACT) - only process strings
			if isinstance(content, str):
				chunks.append(content.strip())
			chunks.append("")
		return "\n".join(chunks).strip()

	def _format_original_sections(self, sections):
		chunks = []
		for header, content in sections.items():
			chunks.append(header)

			# Skip dict values (like _CONTACT) - only process strings
			if not isinstance(content, str):
				continue

			subsections = parse_subsections(content, header)
			if subsections:
				for sub in subsections:
					title = sub.get("title", "").strip()
					bullets = sub.get("bullets", [])
					if title:
						chunks.append(title)
					if bullets:
						for bullet in bullets:
							chunks.append(f"- {bullet.strip()}")
					chunks.append("")
			else:
				for line in content.split("\n"):
					line = line.strip()
					if line:
						chunks.append(line)
				chunks.append("")

		# Collapse repeated blank lines and trim edges.
		cleaned = []
		last_blank = False
		for line in chunks:
			is_blank = not line.strip()
			if is_blank and last_blank:
				continue
			cleaned.append(line)
			last_blank = is_blank

		return "\n".join(cleaned).strip()

	def _set_original_text(self, text):
		self.original_text.configure(state="normal")
		self.original_text.delete("1.0", "end")
		self.original_text.insert("1.0", text)
		self.original_text.configure(state="disabled")

	def _set_polished_text(self, text):
		self.polished_text.delete("1.0", "end")
		self.polished_text.insert("1.0", text)

	def _set_save_buttons_enabled(self, enabled):
		state = "normal" if enabled else "disabled"
		self.save_new_btn.configure(state=state)
		self.replace_btn.configure(state=state)

import os
import json
import re
import threading
import customtkinter as ctk
from tkinter import filedialog, messagebox

from core.input_parser import load_pdf, parse_section
from core.output_builder import build_resume
from core.pdf_generator import generate_pdf
from core.llm_client import ask_llm
from core.prompts import get_changes_summary_prompt


class JobTailorPanel(ctk.CTkFrame):
	def __init__(self, parent, state):
		super().__init__(parent)
		self.state = state
		self._is_tailoring = False

		self.grid_columnconfigure(0, weight=1)
		self.grid_columnconfigure(1, weight=1)
		self.grid_columnconfigure(0, uniform="pane")
		self.grid_columnconfigure(1, uniform="pane")
		self.grid_rowconfigure(1, weight=1)

		title = ctk.CTkLabel(self, text="Job Tailor", font=("Arial", 22, "bold"))
		title.grid(row=0, column=0, padx=(20, 10), pady=12, sticky="w")

		controls = ctk.CTkFrame(self, fg_color="transparent")
		controls.grid(row=0, column=1, padx=(10, 20), pady=12, sticky="e")
		controls.grid_columnconfigure(1, weight=1)

		resume_label = ctk.CTkLabel(controls, text="Resume:")
		resume_label.grid(row=0, column=0, padx=(0, 8), sticky="e")

		self.resume_dropdown = ctk.CTkOptionMenu(
			controls,
			values=["No resumes found"],
			width=220,
		)
		self.resume_dropdown.grid(row=0, column=1, padx=(0, 8), sticky="ew")

		self.tailor_btn = ctk.CTkButton(
			controls,
			text="Tailor Resume",
			command=self.tailor_resume,
		)
		self.tailor_btn.grid(row=0, column=2, sticky="e")

		job_desc_frame = ctk.CTkFrame(self)
		job_desc_frame.grid(row=1, column=0, padx=(20, 10), pady=(0, 10), sticky="nsew")
		job_desc_frame.grid_rowconfigure(1, weight=1)
		job_desc_frame.grid_columnconfigure(0, weight=1)

		job_desc_label = ctk.CTkLabel(job_desc_frame, text="Job Description")
		job_desc_label.grid(row=0, column=0, padx=10, pady=(10, 6), sticky="w")

		self.job_desc_text = ctk.CTkTextbox(job_desc_frame, wrap="word")
		self.job_desc_text.grid(row=1, column=0, padx=10, pady=(0, 10), sticky="nsew")

		output_frame = ctk.CTkFrame(self)
		output_frame.grid(row=1, column=1, padx=(10, 20), pady=(0, 10), sticky="nsew")
		output_frame.grid_rowconfigure(1, weight=1)
		output_frame.grid_columnconfigure(0, weight=1)

		output_label = ctk.CTkLabel(output_frame, text="Tailored Output")
		output_label.grid(row=0, column=0, padx=10, pady=(10, 6), sticky="w")

		self.tailored_text = ctk.CTkTextbox(output_frame, wrap="word")
		self.tailored_text.grid(row=1, column=0, padx=10, pady=(0, 10), sticky="nsew")

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

		self.status_label = ctk.CTkLabel(footer, text="Select a resume, paste a job description, then click Tailor Resume.")
		self.status_label.grid(row=0, column=0, sticky="w")

		btn_row = ctk.CTkFrame(footer, fg_color="transparent")
		btn_row.grid(row=0, column=1, sticky="e")

		self.save_new_btn = ctk.CTkButton(btn_row, text="Save as New", command=self.save_as_new)
		self.save_new_btn.grid(row=0, column=0, padx=(0, 8))

		self.replace_btn = ctk.CTkButton(btn_row, text="Replace Original", command=self.replace_original)
		self.replace_btn.grid(row=0, column=1)

		self._set_save_buttons_enabled(False)
		self.load_resume_options()
		self._update_summary([])

	def refresh(self):
		self.load_resume_options()

	def load_resume_options(self):
		files = sorted([f[:-4] for f in os.listdir(self.state.resumes_dir) if f.lower().endswith(".pdf")])
		values = files or ["No resumes found"]
		self.resume_dropdown.configure(values=values)
		self.resume_dropdown.set(values[0])

	def tailor_resume(self):
		if self._is_tailoring:
			return

		path = self._selected_resume_path()
		if not path or not os.path.exists(path):
			self.status_label.configure(text="Pick a valid resume first.")
			return

		job_description = self.job_desc_text.get("1.0", "end").strip()
		if not job_description:
			self.status_label.configure(text="Paste a job description first.")
			return

		self._is_tailoring = True
		self.tailor_btn.configure(state="disabled", text="Tailoring...")
		self._set_save_buttons_enabled(False)
		self.status_label.configure(text="Tailoring resume... this can take up to a minute.")

		thread = threading.Thread(target=self._run_tailor, args=(path, job_description), daemon=True)
		thread.start()

	def _run_tailor(self, path, job_description):
		try:
			original_text = load_pdf(path)
			sections = parse_section(original_text)
			if not sections:
				raise ValueError("Could not detect resume sections. Try a resume with clear section headers.")

			tailored_sections = build_resume(sections, job_description)
			tailored_text = self._sections_to_text(tailored_sections)
			if not tailored_text.strip():
				raise ValueError("Tailor returned empty output. Check Ollama/model availability and try again.")

			original_formatted = self._sections_to_text(sections)
			changes_prompt = get_changes_summary_prompt(original_formatted, tailored_text)
			changes_raw = ask_llm(changes_prompt)
			changes = self._parse_changes_summary(changes_raw)

			self.after(0, lambda text=tailored_text, c=changes: self._on_tailor_success(text, c))
		except Exception as exc:
			error_msg = str(exc)
			self.after(0, lambda msg=error_msg: self._on_tailor_error(msg))

	def _on_tailor_success(self, tailored_text, changes):
		self._is_tailoring = False
		self.tailor_btn.configure(state="normal", text="Tailor Resume")
		self._set_tailored_text(tailored_text)
		self._update_summary(changes)
		self._set_save_buttons_enabled(bool(tailored_text.strip()))
		self.status_label.configure(text="Tailor complete. Review and save.")

	def _on_tailor_error(self, error_msg):
		self._is_tailoring = False
		self.tailor_btn.configure(state="normal", text="Tailor Resume")
		self._update_summary([])
		self._set_save_buttons_enabled(False)
		self.status_label.configure(text=f"Tailor failed: {error_msg}")

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
		tailored = self.tailored_text.get("1.0", "end").strip()
		if not tailored:
			self.status_label.configure(text="No tailored resume content to save.")
			return

		current_name = self.resume_dropdown.get()
		default_name = f"{current_name}_tailored.pdf" if current_name and current_name != "No resumes found" else "resume_tailored.pdf"
		save_path = filedialog.asksaveasfilename(
			title="Save Tailored Resume As",
			defaultextension=".pdf",
			initialdir=self.state.resumes_dir,
			initialfile=default_name,
			filetypes=[("PDF files", "*.pdf")],
		)
		if not save_path:
			return

		self._save_tailored_to_path(save_path)

	def replace_original(self):
		tailored = self.tailored_text.get("1.0", "end").strip()
		if not tailored:
			self.status_label.configure(text="No tailored resume content to save.")
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

		self._save_tailored_to_path(path)

	def _save_tailored_to_path(self, path):
		try:
			tailored_text = self.tailored_text.get("1.0", "end").strip()
			tailored_sections = parse_section(tailored_text)
			if not tailored_sections:
				self.status_label.configure(text="Could not parse tailored content into sections.")
				return
			generate_pdf(tailored_sections, path)
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
			# Skip non-string values like dicts (e.g., _CONTACT)
			if not isinstance(content, str):
				continue
			chunks.append(header)
			chunks.append(content.strip())
			chunks.append("")
		return "\n".join(chunks).strip()

	def _set_tailored_text(self, text):
		self.tailored_text.delete("1.0", "end")
		self.tailored_text.insert("1.0", text)

	def _set_save_buttons_enabled(self, enabled):
		state = "normal" if enabled else "disabled"
		self.save_new_btn.configure(state=state)
		self.replace_btn.configure(state=state)

def bullet_polish_prompt(bullet: str, mode: str = "medium") -> str:
    mode_instructions = {
        "light": (
            "Make minimal changes. Only fix weak or vague verbs and tighten wording. "
            "Preserve the original structure and content as closely as possible."
        ),
        "medium": (
            "Improve clarity, verb precision, and impact. You may restructure the bullet "
            "if it improves readability, but do not change the substance of what was done."
        ),
        "aggressive": (
            "Fully rewrite for maximum impact. Restructure freely, sharpen the verb, "
            "and make the accomplishment as compelling as possible without inventing experience."
        ),
    }

    return f"""You are a professional resume editor. Rewrite the following resume bullet point.

BULLET:
{bullet}

REWRITE RULES:
1. Begin with a precise action verb that reflects the specific nature of the work in this bullet.
   - Choose the verb based on what was actually done, not from a fixed list.
   - If the original verb is already specific and accurate, keep it.
   - Only replace verbs that are weak, vague, or generic (e.g. "helped", "worked on", "assisted", "did", "was responsible for").
2. Follow the structure: [Action Verb] + [What was done] + [Tools/Technologies used] + [Outcome or impact].
3. Preserve every technology, tool, and language mentioned in the original — do not drop any.
4. If a measurable result is present, keep it. If one is strongly implied and you can represent it with a natural placeholder like [X%] or [N users], you may add it. If no metric fits naturally, omit it entirely. NEVER write [N/A], [none], or any explanatory bracket text.
5. Do NOT add skills, tools, or experience that are not in the original bullet.
6. Maximum 180 characters.
7. Do NOT include a leading "- " prefix.
8. Return only the rewritten bullet. No explanation, no commentary, no alternatives.

INTENSITY: {mode_instructions[mode]}

REWRITTEN BULLET:"""


def get_changes_summary_prompt(original, polished):
  return f"""
You are a resume editor reviewing changes made to a resume.
Compare the original and polished versions and summarize what changed.

Rules:
- Return a JSON array of change strings, nothing else
- Maximum 8 changes
- Each change should be concise (under 80 characters)
- Focus on meaningful changes: verb upgrades, added keywords, structural improvements
- Ignore whitespace or formatting differences

Return exactly this format:
["change 1", "change 2", "change 3"]

Original:
{original}

Polished:
{polished}

Changes:
""".strip()

def job_tailor_prompt(resume_section: str, job_description: str) -> str:
    return f"""You are a professional resume editor. Rewrite the following resume bullets to better align with the job description.

RESUME BULLETS:
{resume_section}

JOB DESCRIPTION:
{job_description}

RULES:
1. Return exactly the same number of bullets as provided — no more, no fewer.
2. Each bullet must begin with a precise action verb that reflects what was actually done in that bullet.
   - If the original verb is already accurate and strong, keep it.
   - Only replace verbs that are weak or generic.
   - Do not reuse the same verb across multiple bullets.
3. Incorporate relevant keywords and terminology from the job description naturally — do not force them in awkwardly.
4. Preserve the original accomplishments exactly. Do not swap in responsibilities copied from the job posting.
5. Do NOT add any skills, tools, or technologies that are not present in the original bullets.
6. Maximum 180 characters per bullet.
7. Do NOT include a leading "- " prefix.
8. Return only the rewritten bullets, one per line. No explanation or commentary.

REWRITTEN BULLETS:"""

def experience_updater_prompt(user_input: str) -> str:
    return f"""You are a professional resume writer. Convert the following experience description into 2-4 resume bullet points.

EXPERIENCE DESCRIPTION:
{user_input}

RULES:
1. Extract 2-4 distinct accomplishments or responsibilities from the description.
2. Each bullet must begin with a precise action verb that matches what was actually done in that specific task.
   - Derive the verb from the nature of the work — do not default to the same verb across bullets.
   - Avoid weak or overused openers like "Developed", "Worked on", "Helped", or "Was responsible for".
3. Follow the structure: [Action Verb] + [What was done] + [Tools/Technologies] + [Result or impact].
4. If a metric is stated, include it. If one is implied, use a placeholder like [X%] or [N users].
5. Maximum 180 characters per bullet.
6. Each bullet must start with "- ".
7. Return only the bullets. No explanation, no preamble.

BULLETS:"""
def get_grader_prompt(resume_text: str) -> str:
    return f"""You are a professional resume reviewer. Grade the following resume across 4 dimensions.

RESUME:
{resume_text}

Score each dimension from 1 to 10 using these criteria:
- ats_score: How well the resume would pass Applicant Tracking Systems (keywords, formatting, standard sections)
- sections_score: Whether the resume has the right sections (Education, Experience, Projects, Skills) and organizes them clearly
- bullets_score: Quality of bullet points — action verbs, measurable results, specificity, conciseness
- keywords_score: Presence of relevant technical and industry keywords for the apparent target role

Return ONLY a valid JSON object in exactly this format, with no explanation, no preamble, no markdown:
{{"ats_score": 0, "sections_score": 0, "bullets_score": 0, "keywords_score": 0}}

SCORES:"""


def parse_resume_structure_prompt(resume_text: str) -> str:
    return f"""You are a resume parsing expert. Your task is to recognize common resume formatting patterns and extract structured data.

RESUME:
{resume_text}

COMMON RESUME PATTERNS TO RECOGNIZE:

1. WORK EXPERIENCE / PROFESSIONAL EXPERIENCE / EMPLOYMENT:
   - Typical format: "Title/Position – Company/Organization [Location] [Date Range]"
   - Can also appear as separate lines or multiple formats
   - Each entry has: a job title, a company/organization name, optional location, optional dates, and bullet points describing accomplishments
   - Locations can be cities, states, or "Remote"
   - Dates are typically in format: "Month Year – Month Year" or "Month Year – Present"

2. PROJECTS / ACADEMIC PROJECTS / PERSONAL PROJECTS:
   - Typical format: "Project Name [| Technology Stack]"
   - Location: Projects rarely have locations unless specified
   - Dates: May not have dates
   - Technologies: Often listed inline with project name (after | or parentheses)
   - Each project has bullet points describing what was built/accomplished

3. LEADERSHIP / ACTIVITIES / INVOLVEMENT / EXTRACURRICULARS:
   - Typical format: "Title – Organization [Location] [Date Range]"
   - Similar to work experience but for clubs, organizations, volunteering
   - Has: a title, organization name, optional location, optional dates, bullet points

4. EDUCATION:
   - Typical format: "School/University [Location] [Date]" with degree info on same or next line
   - Has: degree name, school name, optional location, optional date/graduation date, optional details (GPA, honors, etc.)

5. SKILLS / TECHNICAL SKILLS / COMPETENCIES:
   - Usually listed as categories with items underneath
   - May be comma-separated or bullet-pointed
   - Extract category names and skill items

EXTRACTION RULES - DO NOT HARDCODE:
- Look for PATTERNS not specific keywords. For example:
  - "Title/Position – Company" format indicates work experience entry
  - "Name [| Technology]" on its own line often indicates a project
  - "Title – Organization" in a leadership/activity section
  
- For locations: Extract only if explicitly shown in the HEADER line of an entry (not from bullet content)
  - Locations appear after a dash, comma, or in parentheses near the title/company
  - Do NOT infer locations from bullet points

- For dates: Extract only if explicitly shown in the HEADER line (not from bullet content)
  - Typically at the end of an entry header
  - Format: "Month Year – Month Year" or "Month Year – Present"

- For bullets: Extract EVERY bullet point exactly as written
  - has_location in bullet: true ONLY if the bullet text itself contains a location mention (city, state, address)
  - has_date in bullet: true ONLY if the bullet text itself contains a date or time period

- For company/organization names: Extract exactly as they appear in the resume, do NOT set to null if present
- For technologies in projects: Extract inline technologies if listed (e.g., "Python", "React", "JavaScript")

Return ONLY valid JSON with no explanation, markdown formatting, or code blocks - just pure JSON:

{{
  "work_experience": [
    {{
      "position": "string",
      "company": "string",
      "location": "string or null",
      "start_date": "string or null",
      "end_date": "string or null",
      "bullets": [
        {{"text": "string", "has_location": false or true, "has_date": false or true}}
      ]
    }}
  ],
  "projects": [
    {{
      "name": "string",
      "location": "string or null",
      "date": "string or null",
      "technologies": "string or null",
      "bullets": [
        {{"text": "string", "has_location": false or true, "has_date": false or true}}
      ]
    }}
  ],
  "leadership": [
    {{
      "title": "string",
      "organization": "string or null",
      "location": "string or null",
      "date": "string or null",
      "bullets": [
        {{"text": "string", "has_location": false or true, "has_date": false or true}}
      ]
    }}
  ],
  "education": [
    {{
      "degree": "string",
      "school": "string",
      "location": "string or null",
      "date": "string or null",
      "details": [
        {{"text": "string"}}
      ]
    }}
  ],
  "skills": [
    {{
      "category": "string",
      "items": ["string"]
    }}
  ]
}}

PARSED RESUME:"""
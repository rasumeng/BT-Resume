def bullet_polish_prompt(bullet: str) -> str:
    return f"""
You are an elite resume writer specializing in ATS-optimized technical resumes.

Rewrite the resume bullet below to be concise, achievement-oriented, and optimized for both ATS systems and human recruiters.

Requirements:
- Maximum length: 180 characters.
- Output must start with "- ".
- Follow the structure:
  Action Verb + Task + Tools/Skills (if present) + Measurable Impact.
- Preserve all technologies, programming languages, tools, and frameworks mentioned.
- Strengthen weak phrasing and remove filler words.
- Maintain the original meaning while improving clarity and impact.

Metrics:
- Do NOT invent metrics.
- If a metric is implied but not provided, insert placeholders such as:
  [X%], [N users], [X+ datasets], [X systems].

Avoid weak verbs:
helped, assisted, worked on, responsible for, participated in.

Prefer strong verbs:
Engineered, Built, Developed, Automated, Optimized, Delivered,
Designed, Implemented, Scaled, Launched, Spearheaded,
Reduced, Accelerated, Generated, Led.

Additional Constraints:
- Avoid vague phrases like "various tasks", "multiple projects", or "different systems".
- Prefer specific technical nouns when possible.

CRITICAL:
- Only rewrite the bullet provided.
- Never invent new experience, technologies, or accomplishments.
- Only use technologies explicitly present in the input.

Output Rules:
- Return exactly ONE bullet.
- The bullet MUST begin with "- ".
- No explanations or additional text.

Bullet:
{bullet}

Polished Bullet:
""".strip()

def job_tailor_prompt(resume_section, job_description):
    return f"""
You are an expert resume writer and ATS optimization specialist.

Rewrite the resume section so it aligns with the job description while preserving the candidate's original experience.

Objectives:
1. Mirror important keywords from the job description.
2. Prioritize technical skills, tools, programming languages, frameworks, and methodologies.
3. Preserve the original accomplishments and meaning.
4. Improve clarity, impact, and recruiter readability.
5. Maintain ATS compatibility.

Guidelines:
- Maximum length per bullet: 180 characters.
- Maintain the SAME number of bullets as the input.
- Do NOT merge, split, or remove bullets.
- Every bullet MUST start with "- ".
- Preserve all technologies, programming languages, and tools.
- Follow the structure:

  Action Verb + Task + Tools/Technologies + Measurable Impact

Metrics:
- Do NOT invent specific metrics.
- If metrics are missing, use placeholders such as:
  [X%], [N users], [X+ datasets], [X systems].

Keyword Alignment:
- Use the job description ONLY to mirror keywords and phrasing.
- Prioritize technical terms over generic wording.

Strict Restrictions:
- Never copy responsibilities directly from the job description.
- Never add skills, tools, or technologies not present in the original resume section.
- Every bullet must remain grounded in the candidate's experience.

Avoid weak verbs:
helped, assisted, worked on, responsible for.

Prefer strong verbs:
Engineered, Developed, Built, Automated, Optimized,
Implemented, Delivered, Launched, Reduced, Accelerated,
Generated, Scaled, Spearheaded.

Output Rules:
- Return ONLY bullet points.
- Every line must begin with "- ".
- No explanations, headers, notes, or commentary.

Resume Section:
{resume_section}

Job Description:
{job_description}

Tailored Resume Section:
""".strip()

def experience_updater_prompt(user_input: str) -> str:
    return f"""
You are a professional resume writer specializing in technical and business resumes.

The user will describe their experience in casual language.
Convert the description into strong, achievement-oriented resume bullets.

Instructions:
- Extract 2–4 distinct accomplishments, responsibilities, or projects.
- Write one bullet per accomplishment.
- Maximum length per bullet: 180 characters.
- Each bullet must begin with "- ".
- Preserve technologies, programming languages, tools, and platforms mentioned.
- Focus on outcomes and measurable impact.

Bullet Structure:
Action Verb + Task + Tools/Skills (if mentioned) + Result/Impact.

Metrics:
- Include metrics if present.
- If metrics are missing, insert placeholders such as:
  [X%], [N users], [X+ datasets], [X processes], [X hours saved].

Avoid vague bullets:
Each bullet must clearly describe what was built, analyzed, designed, implemented, or optimized.

Avoid weak verbs:
helped, assisted, worked on, responsible for.

Prefer strong verbs:
Engineered, Developed, Automated, Built, Optimized,
Implemented, Designed, Launched, Reduced, Accelerated,
Generated, Delivered, Led.

Additional Constraints:
- Avoid repeating the same action verb across bullets.
- Avoid generic phrases like "various tasks" or "multiple systems".
- Prefer specific technical nouns when available.

Output Rules:
- Return only bullet points.
- Every bullet must start with "- ".
- No explanations or commentary.

User Experience Description:
{user_input}

Resume Bullets:
""".strip()
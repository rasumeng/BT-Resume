"""
Resume Data Model

Defines the structured schema for resume data with validation.
This ensures consistent data storage across parsing and generation.
"""

from typing import Optional, List, Dict, Any
from dataclasses import dataclass, asdict, field


@dataclass
class ContactInfo:
    """Contact information at the top of resume"""
    name: str
    email: Optional[str] = None
    phone: Optional[str] = None
    location: Optional[str] = None
    linkedin: Optional[str] = None
    github: Optional[str] = None
    portfolio: Optional[str] = None
    websites: Dict[str, str] = field(default_factory=dict)  # {name: url}
    
    def to_dict(self) -> dict:
        """Convert to dict, excluding None values"""
        data = asdict(self)
        return {k: v for k, v in data.items() if v}
    
    @classmethod
    def from_dict(cls, data: dict) -> "ContactInfo":
        """Create from dict, handling extra fields"""
        valid_fields = {f.name for f in cls.__dataclass_fields__.values()}
        filtered = {k: v for k, v in data.items() if k in valid_fields and v}
        
        # Ensure name is present
        if "name" not in filtered or not filtered["name"]:
            filtered["name"] = "Resume"
        
        return cls(**filtered)
    
    def get_contact_line(self) -> str:
        """Generate formatted contact line for resume header"""
        parts = []
        if self.phone:
            parts.append(self.phone)
        if self.email:
            parts.append(self.email)
        if self.location:
            parts.append(self.location)
        if self.linkedin:
            # Extract just the URL or username
            parts.append(self.linkedin)
        if self.github:
            parts.append(self.github)
        
        # Add other websites
        for key, url in (self.websites or {}).items():
            parts.append(url)
        
        return " | ".join(parts)


@dataclass
class BulletPoint:
    """A single resume bullet point"""
    text: str
    has_location: bool = False
    has_date: bool = False


@dataclass
class WorkExperience:
    """Work experience entry"""
    position: str
    company: str
    location: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    bullets: List[BulletPoint] = field(default_factory=list)
    
    def to_dict(self) -> dict:
        return {
            "position": self.position,
            "company": self.company,
            "location": self.location,
            "start_date": self.start_date,
            "end_date": self.end_date,
            "bullets": [asdict(b) for b in self.bullets] if self.bullets else [],
        }


@dataclass
class Project:
    """Project entry"""
    name: str
    location: Optional[str] = None
    date: Optional[str] = None
    technologies: Optional[str] = None
    bullets: List[BulletPoint] = field(default_factory=list)
    
    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "location": self.location,
            "date": self.date,
            "technologies": self.technologies,
            "bullets": [asdict(b) for b in self.bullets] if self.bullets else [],
        }


@dataclass
class Education:
    """Education entry"""
    degree: str
    school: str
    location: Optional[str] = None
    date: Optional[str] = None
    details: List[Dict] = field(default_factory=list)  # [{text: str}]
    
    def to_dict(self) -> dict:
        return {
            "degree": self.degree,
            "school": self.school,
            "location": self.location,
            "date": self.date,
            "details": self.details if self.details else [],
        }


@dataclass
class Leadership:
    """Leadership/Activities entry"""
    title: str
    organization: Optional[str] = None
    location: Optional[str] = None
    date: Optional[str] = None
    bullets: List[BulletPoint] = field(default_factory=list)
    
    def to_dict(self) -> dict:
        return {
            "title": self.title,
            "organization": self.organization,
            "location": self.location,
            "date": self.date,
            "bullets": [asdict(b) for b in self.bullets] if self.bullets else [],
        }


@dataclass
class Skill:
    """Skill category"""
    category: str
    items: List[str] = field(default_factory=list)
    
    def to_dict(self) -> dict:
        return {
            "category": self.category,
            "items": self.items if self.items else [],
        }


@dataclass
class ResumData:
    """Complete resume structure"""
    contact: ContactInfo
    work_experience: List[WorkExperience] = field(default_factory=list)
    projects: List[Project] = field(default_factory=list)
    education: List[Education] = field(default_factory=list)
    leadership: List[Leadership] = field(default_factory=list)
    skills: List[Skill] = field(default_factory=list)
    certifications: Optional[List[Dict]] = None
    summary: Optional[str] = None
    
    def to_dict(self) -> dict:
        """Convert to dict for JSON serialization"""
        data = {
            "contact": self.contact.to_dict(),
            "work_experience": [e.to_dict() for e in self.work_experience],
            "projects": [p.to_dict() for p in self.projects],
            "education": [e.to_dict() for e in self.education],
            "leadership": [l.to_dict() for l in self.leadership],
            "skills": [s.to_dict() for s in self.skills],
        }
        if self.certifications:
            data["certifications"] = self.certifications
        if self.summary:
            data["summary"] = self.summary
        return data
    
    @classmethod
    def from_llm_json(cls, llm_json: dict) -> "ResumData":
        """Create ResumData from LLM-generated JSON
        
        Handles the raw JSON output from the LLM parser and converts it
        to structured ResumData objects with validation.
        """
        # Extract contact info
        contact_raw = llm_json.get("contact", {})
        if isinstance(contact_raw, str):
            # Fallback: parse string contact info (shouldn't happen with good LLM)
            contact_raw = {"name": contact_raw}
        
        contact = ContactInfo.from_dict(contact_raw)
        if not contact.name:
            contact.name = "Resume"  # Fallback name
        
        # Extract sections
        work_exp = []
        for item in llm_json.get("work_experience", []):
            if isinstance(item, dict):
                bullets = [
                    BulletPoint(
                        text=b["text"],
                        has_location=b.get("has_location", False),
                        has_date=b.get("has_date", False),
                    )
                    for b in item.get("bullets", [])
                ]
                work_exp.append(
                    WorkExperience(
                        position=item.get("position", ""),
                        company=item.get("company", ""),
                        location=item.get("location"),
                        start_date=item.get("start_date"),
                        end_date=item.get("end_date"),
                        bullets=bullets,
                    )
                )
        
        projects = []
        for item in llm_json.get("projects", []):
            if isinstance(item, dict):
                bullets = [
                    BulletPoint(
                        text=b["text"],
                        has_location=b.get("has_location", False),
                        has_date=b.get("has_date", False),
                    )
                    for b in item.get("bullets", [])
                ]
                projects.append(
                    Project(
                        name=item.get("name", ""),
                        location=item.get("location"),
                        date=item.get("date"),
                        technologies=item.get("technologies"),
                        bullets=bullets,
                    )
                )
        
        education = []
        for item in llm_json.get("education", []):
            if isinstance(item, dict):
                education.append(
                    Education(
                        degree=item.get("degree", ""),
                        school=item.get("school", ""),
                        location=item.get("location"),
                        date=item.get("date"),
                        details=item.get("details", []),
                    )
                )
        
        leadership = []
        for item in llm_json.get("leadership", []):
            if isinstance(item, dict):
                bullets = [
                    BulletPoint(
                        text=b["text"],
                        has_location=b.get("has_location", False),
                        has_date=b.get("has_date", False),
                    )
                    for b in item.get("bullets", [])
                ]
                leadership.append(
                    Leadership(
                        title=item.get("title", ""),
                        organization=item.get("organization"),
                        location=item.get("location"),
                        date=item.get("date"),
                        bullets=bullets,
                    )
                )
        
        skills = []
        for item in llm_json.get("skills", []):
            if isinstance(item, dict):
                skills.append(
                    Skill(
                        category=item.get("category", ""),
                        items=item.get("items", []),
                    )
                )
        
        return cls(
            contact=contact,
            work_experience=work_exp,
            projects=projects,
            education=education,
            leadership=leadership,
            skills=skills,
            certifications=llm_json.get("certifications"),
            summary=llm_json.get("summary"),
        )
    
    def validate(self) -> tuple[bool, List[str]]:
        """Validate resume data. Returns (is_valid, list_of_errors)"""
        errors = []
        
        # Contact validation
        if not self.contact or not self.contact.name:
            errors.append("Contact name is required")
        if not self.contact.email and not self.contact.phone:
            errors.append("At least email or phone is required")
        
        # Section validation (at least one section should exist)
        has_sections = (
            self.work_experience or
            self.projects or
            self.education or
            self.leadership or
            self.skills
        )
        if not has_sections:
            errors.append("Resume must have at least one section (work, projects, education, etc.)")
        
        return len(errors) == 0, errors

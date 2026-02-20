"""Resume Parser Service.

Extracts structured data from resume/CV documents.
"""
from __future__ import annotations

import base64
import re
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from backend.app.schemas.docai import (
    Education,
    ResumeParseRequest,
    ResumeParseResponse,
    WorkExperience,
)


class ResumeParser:
    """Parser for extracting data from resume documents."""

    # Common section headers
    SECTION_HEADERS = {
        "experience": [
            r"(?:work\s+)?experience",
            r"employment\s+history",
            r"professional\s+experience",
            r"work\s+history",
        ],
        "education": [
            r"education",
            r"academic\s+background",
            r"qualifications",
        ],
        "skills": [
            r"skills",
            r"technical\s+skills",
            r"core\s+competencies",
            r"expertise",
        ],
        "certifications": [
            r"certifications?",
            r"licenses?",
            r"credentials",
        ],
        "summary": [
            r"(?:professional\s+)?summary",
            r"(?:career\s+)?objective",
            r"profile",
            r"about\s+me",
        ],
    }

    # Common skills keywords
    TECHNICAL_SKILLS = [
        "python", "javascript", "java", "c++", "c#", "ruby", "go", "rust",
        "sql", "nosql", "mongodb", "postgresql", "mysql", "redis",
        "aws", "azure", "gcp", "docker", "kubernetes", "terraform",
        "react", "angular", "vue", "node.js", "django", "flask",
        "machine learning", "deep learning", "ai", "data science",
        "git", "ci/cd", "agile", "scrum", "jira",
    ]

    def __init__(self) -> None:
        """Initialize the resume parser."""
        self._nlp_available = self._check_nlp()

    def _check_nlp(self) -> bool:
        """Check if NLP libraries are available."""
        try:
            import spacy  # noqa: F401
            return True
        except Exception:
            return False

    async def parse(self, request: ResumeParseRequest) -> ResumeParseResponse:
        """Parse a resume document.

        Args:
            request: The parse request with file path or content

        Returns:
            Parsed resume data
        """
        start_time = time.time()
        text = await self._extract_text(request)

        # Extract contact information
        name = self._extract_name(text)
        email = self._extract_email(text)
        phone = self._extract_phone(text)
        location = self._extract_location(text)
        linkedin_url = self._extract_linkedin(text)
        github_url = self._extract_github(text)
        portfolio_url = self._extract_portfolio(text)

        # Extract summary
        summary = self._extract_summary(text)

        # Extract sections
        education = self._extract_education(text)
        experience = self._extract_experience(text)

        # Extract skills
        skills = (
            self._extract_skills(text)
            if request.extract_skills
            else []
        )

        # Extract certifications and languages
        certifications = self._extract_certifications(text)
        languages = self._extract_languages(text)

        # Calculate total experience
        total_years = self._calculate_total_experience(experience)

        # Job matching if requested
        job_match_score = None
        job_match_details = None
        if request.match_job_description:
            job_match_score, job_match_details = self._match_job(
                text, skills, experience, request.match_job_description
            )

        # Calculate confidence
        confidence = self._calculate_confidence(
            name, email, education, experience
        )

        processing_time_ms = int((time.time() - start_time) * 1000)

        return ResumeParseResponse(
            name=name,
            email=email,
            phone=phone,
            location=location,
            linkedin_url=linkedin_url,
            github_url=github_url,
            portfolio_url=portfolio_url,
            summary=summary,
            education=education,
            experience=experience,
            skills=skills,
            certifications=certifications,
            languages=languages,
            total_years_experience=total_years,
            job_match_score=job_match_score,
            job_match_details=job_match_details,
            raw_text=text[:5000] if text else None,
            confidence_score=confidence,
            processing_time_ms=processing_time_ms,
        )

    async def _extract_text(self, request: ResumeParseRequest) -> str:
        """Extract text from the resume document."""
        if request.content:
            content = base64.b64decode(request.content)
            return await self._extract_from_bytes(content)
        elif request.file_path:
            path = Path(request.file_path)
            if not path.exists():
                raise FileNotFoundError(f"File not found: {request.file_path}")

            suffix = path.suffix.lower()
            if suffix == ".pdf":
                return await self._extract_from_pdf(path)
            elif suffix == ".docx":
                return await self._extract_from_docx(path)
            else:
                return path.read_text(encoding="utf-8")
        return ""

    async def _extract_from_bytes(self, content: bytes) -> str:
        """Extract text from raw bytes."""
        try:
            import fitz
            doc = fitz.open(stream=content, filetype="pdf")
            text = ""
            for page in doc:
                text += page.get_text()
            doc.close()
            return text
        except Exception:
            return content.decode("utf-8", errors="ignore")

    async def _extract_from_pdf(self, path: Path) -> str:
        """Extract text from a PDF file."""
        try:
            import fitz
            doc = fitz.open(str(path))
            text = ""
            for page in doc:
                text += page.get_text()
            doc.close()
            return text
        except ImportError:
            return ""

    async def _extract_from_docx(self, path: Path) -> str:
        """Extract text from a DOCX file."""
        try:
            from docx import Document
            doc = Document(str(path))
            return "\n".join([para.text for para in doc.paragraphs])
        except ImportError:
            return ""

    def _extract_name(self, text: str) -> Optional[str]:
        """Extract candidate name from resume."""
        # Usually the name is in the first few lines
        lines = text.strip().split("\n")[:5]

        for line in lines:
            line = line.strip()
            # Skip lines that look like headers or contact info
            if "@" in line or re.search(r"\d{3}[-.\s]?\d{3}", line):
                continue
            if len(line) < 3 or len(line) > 50:
                continue

            # Check if line looks like a name (mostly letters and spaces)
            if re.match(r"^[A-Z][a-z]+(?:\s+[A-Z][a-z]+)+$", line):
                return line

        # Fallback: first non-empty line
        for line in lines:
            line = line.strip()
            if line and len(line) < 50:
                return line

        return None

    def _extract_email(self, text: str) -> Optional[str]:
        """Extract email address from resume."""
        email_match = re.search(r"[\w.+-]+@[\w-]+\.[\w.-]+", text)
        return email_match.group(0) if email_match else None

    def _extract_phone(self, text: str) -> Optional[str]:
        """Extract phone number from resume."""
        # Various phone formats
        phone_patterns = [
            r"\+?1?[-.\s]?\(?(\d{3})\)?[-.\s]?(\d{3})[-.\s]?(\d{4})",
            r"\+?\d{1,3}[-.\s]?\d{1,4}[-.\s]?\d{1,4}[-.\s]?\d{1,4}",
        ]

        for pattern in phone_patterns:
            match = re.search(pattern, text)
            if match:
                return match.group(0)

        return None

    def _extract_location(self, text: str) -> Optional[str]:
        """Extract location from resume."""
        # Look for city, state pattern
        location_match = re.search(
            r"([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?),\s*([A-Z]{2})\b",
            text[:1000]
        )
        if location_match:
            return f"{location_match.group(1)}, {location_match.group(2)}"

        return None

    def _extract_linkedin(self, text: str) -> Optional[str]:
        """Extract LinkedIn URL from resume."""
        url_match = re.search(
            r"(https?://(?:www\.)?linkedin\.com/in/[a-zA-Z0-9-]+)",
            text, re.IGNORECASE
        )
        if url_match:
            return url_match.group(1)

        bare_match = re.search(r"linkedin\.com/in/([a-zA-Z0-9-]+)", text, re.IGNORECASE)
        if bare_match:
            return f"https://linkedin.com/in/{bare_match.group(1)}"

        label_match = re.search(r"linkedin:\s*([a-zA-Z0-9-]+)", text, re.IGNORECASE)
        if label_match:
            return f"https://linkedin.com/in/{label_match.group(1)}"
        return None

    def _extract_github(self, text: str) -> Optional[str]:
        """Extract GitHub URL from resume."""
        url_match = re.search(
            r"(https?://(?:www\.)?github\.com/[a-zA-Z0-9-]+)",
            text, re.IGNORECASE
        )
        if url_match:
            return url_match.group(1)

        bare_match = re.search(r"github\.com/([a-zA-Z0-9-]+)", text, re.IGNORECASE)
        if bare_match:
            return f"https://github.com/{bare_match.group(1)}"

        label_match = re.search(r"github:\s*([a-zA-Z0-9-]+)", text, re.IGNORECASE)
        if label_match:
            return f"https://github.com/{label_match.group(1)}"
        return None

    def _extract_portfolio(self, text: str) -> Optional[str]:
        """Extract portfolio URL from resume."""
        url_match = re.search(
            r"(?:portfolio|website|blog)[:\s]*(?:https?://)?([a-zA-Z0-9.-]+\.[a-z]{2,})",
            text, re.IGNORECASE
        )
        if url_match:
            return f"https://{url_match.group(1)}"
        return None

    def _extract_summary(self, text: str) -> Optional[str]:
        """Extract professional summary from resume."""
        # Find summary section
        for pattern in self.SECTION_HEADERS["summary"]:
            match = re.search(
                rf"{pattern}\s*:?\s*\n(.+?)(?=\n\s*\n|\n\s*(?:experience|education|skills|certif|certifications)\b|$)",
                text, re.IGNORECASE | re.DOTALL
            )
            if match:
                summary = match.group(1).strip()
                if len(summary) > 20:
                    return summary[:1000]

        return None

    def _extract_education(self, text: str) -> List[Education]:
        """Extract education entries from resume."""
        education_list: List[Education] = []

        # Find education section
        education_section = ""
        for pattern in self.SECTION_HEADERS["education"]:
            match = re.search(
                rf"{pattern}\s*:?\s*\n(.+?)(?:\n\n|experience|skills|certif|$)",
                text, re.IGNORECASE | re.DOTALL
            )
            if match:
                education_section = match.group(1)
                break

        if not education_section:
            return education_list

        # Look for degree patterns
        degree_patterns = [
            r"(Bachelor|Master|PhD|Doctor|Associate|MBA|B\.?S\.?|M\.?S\.?|B\.?A\.?|M\.?A\.?)[^,\n]*",
        ]

        # Split into entries by double newline or bullet
        entries = re.split(r"\n\n|\n•|\n-", education_section)

        for entry in entries:
            if len(entry) < 10:
                continue

            # Extract institution
            institution = None
            lines = entry.strip().split("\n")
            if lines:
                institution = lines[0].strip()

            # Extract degree
            degree = None
            for pattern in degree_patterns:
                degree_match = re.search(pattern, entry, re.IGNORECASE)
                if degree_match:
                    degree = degree_match.group(0)
                    break

            # Extract dates
            date_match = re.search(r"(\d{4})\s*[-–]\s*(\d{4}|present)", entry, re.IGNORECASE)
            start_date = date_match.group(1) if date_match else None
            end_date = date_match.group(2) if date_match else None

            if institution:
                education_list.append(Education(
                    institution=institution,
                    degree=degree,
                    start_date=start_date,
                    end_date=end_date,
                ))

        return education_list[:5]  # Limit to 5 entries

    def _extract_experience(self, text: str) -> List[WorkExperience]:
        """Extract work experience entries from resume."""
        experience_list: List[WorkExperience] = []

        # Find experience section
        experience_section = ""
        for pattern in self.SECTION_HEADERS["experience"]:
            match = re.search(
                rf"{pattern}\s*:?\s*\n(.+?)(?:education|skills|certif|$)",
                text, re.IGNORECASE | re.DOTALL
            )
            if match:
                experience_section = match.group(1)
                break

        if not experience_section:
            return experience_list

        # Split into entries
        entries = re.split(r"\n\n\n|\n\n(?=[A-Z])", experience_section)

        for entry in entries:
            if len(entry) < 20:
                continue

            lines = entry.strip().split("\n")
            if not lines:
                continue

            # Extract company and title
            company = None
            title = None

            # First line usually has company or title
            first_line = lines[0].strip()
            if first_line:
                company = first_line

            # Second line might have the other
            if len(lines) > 1:
                second_line = lines[1].strip()
                if re.search(r"(?:manager|engineer|developer|analyst|director|specialist|coordinator)", second_line, re.IGNORECASE):
                    title = second_line
                elif not company:
                    company = second_line

            # Try to find title in entry
            if not title:
                title_match = re.search(
                    r"((?:Senior\s+)?(?:Software|Data|Product|Project|Marketing|Sales|HR|UX|UI|Full\s*Stack|Front\s*End|Back\s*End)\s+"
                    r"(?:Engineer|Developer|Designer|Manager|Analyst|Specialist|Director|Coordinator|Consultant))",
                    entry, re.IGNORECASE
                )
                if title_match:
                    title = title_match.group(1)

            # Extract dates
            date_match = re.search(
                r"(\w+\s+\d{4}|\d{4})\s*[-–]\s*(\w+\s+\d{4}|\d{4}|present|current)",
                entry, re.IGNORECASE
            )
            start_date = date_match.group(1) if date_match else None
            end_date = date_match.group(2) if date_match else None
            is_current = bool(end_date and re.search(r"present|current", end_date, re.IGNORECASE))

            # Extract achievements (bullet points)
            achievements: List[str] = []
            for line in lines:
                line = line.strip()
                if line.startswith(("•", "-", "*", "○")):
                    achievement = line.lstrip("•-*○").strip()
                    if len(achievement) > 10:
                        achievements.append(achievement[:200])

            if company or title:
                experience_list.append(WorkExperience(
                    company=company or "Unknown Company",
                    title=title or "Position",
                    start_date=start_date,
                    end_date=end_date,
                    is_current=is_current,
                    achievements=achievements[:5],
                ))

        return experience_list[:10]  # Limit to 10 entries

    def _extract_skills(self, text: str) -> List[str]:
        """Extract skills from resume."""
        skills: List[str] = []
        text_lower = text.lower()

        # Find skills section
        skills_section = ""
        for pattern in self.SECTION_HEADERS["skills"]:
            match = re.search(
                rf"{pattern}\s*:?\s*\n(.+?)(?:\n\n|experience|education|certif|$)",
                text, re.IGNORECASE | re.DOTALL
            )
            if match:
                skills_section = match.group(1)
                break

        # Extract from skills section
        if skills_section:
            # Split by commas, bullets, or pipes
            skill_items = re.split(r"[,•|\n]", skills_section)
            for item in skill_items:
                item = item.strip().strip("-•*")
                if 2 < len(item) < 50:
                    skills.append(item)

        # Also look for known technical skills throughout the document
        for skill in self.TECHNICAL_SKILLS:
            if skill.lower() in text_lower and skill not in [s.lower() for s in skills]:
                skills.append(skill.title() if len(skill) > 3 else skill.upper())

        return list(set(skills))[:30]  # Deduplicate and limit

    def _extract_certifications(self, text: str) -> List[str]:
        """Extract certifications from resume."""
        certifications: List[str] = []

        # Find certifications section
        for pattern in self.SECTION_HEADERS["certifications"]:
            match = re.search(
                rf"{pattern}\s*:?\s*\n(.+?)(?:\n\n|skills|experience|education|$)",
                text, re.IGNORECASE | re.DOTALL
            )
            if match:
                section = match.group(1)
                # Split by newlines or bullets
                items = re.split(r"\n|•|-", section)
                for item in items:
                    item = item.strip()
                    if 5 < len(item) < 100:
                        certifications.append(item)

        # Look for common certification patterns
        cert_patterns = [
            r"(?:AWS|Azure|Google[ \t]+Cloud|GCP)[ \t]+Certified[ \t]+[^,\n]+",
            r"(?:PMP|CISSP|CISM|CEH|CompTIA|CCNA|CCNP)[^,\n]*",
            r"Certified[ \t]+[A-Z][a-z]+(?:[ \t]+[A-Z][a-z]+)*",
        ]

        for pattern in cert_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            certifications.extend(matches)

        return list(set(certifications))[:10]

    def _extract_languages(self, text: str) -> List[str]:
        """Extract spoken languages from resume."""
        languages: List[str] = []

        # Look for languages section or mentions
        lang_match = re.search(
            r"(?:languages?|fluent\s+in|speaks?)\s*:?\s*([^\n]+)",
            text, re.IGNORECASE
        )
        if lang_match:
            lang_text = lang_match.group(1)
            # Split by commas or "and"
            items = re.split(r"[,;]|\band\b", lang_text)
            for item in items:
                item = item.strip()
                # Filter to likely language names
                if re.match(r"^[A-Z][a-z]+(?:\s+\([^)]+\))?$", item):
                    languages.append(item)

        return languages[:5]

    def _calculate_total_experience(
        self, experience: List[WorkExperience]
    ) -> Optional[float]:
        """Calculate total years of experience."""
        total_months = 0
        current_year = datetime.now(timezone.utc).year

        for exp in experience:
            start_year = None
            end_year = None

            if exp.start_date:
                year_match = re.search(r"(\d{4})", exp.start_date)
                if year_match:
                    start_year = int(year_match.group(1))

            if exp.end_date:
                if re.search(r"present|current", exp.end_date, re.IGNORECASE):
                    end_year = current_year
                else:
                    year_match = re.search(r"(\d{4})", exp.end_date)
                    if year_match:
                        end_year = int(year_match.group(1))

            if start_year and end_year:
                total_months += (end_year - start_year) * 12

        return round(total_months / 12, 1) if total_months > 0 else None

    def _match_job(
        self,
        text: str,
        skills: List[str],
        experience: List[WorkExperience],
        job_description: str,
    ) -> Tuple[float, Dict[str, Any]]:
        """Match resume against a job description."""
        job_lower = job_description.lower()
        text_lower = text.lower()

        # Skill match
        job_skills = []
        for skill in self.TECHNICAL_SKILLS:
            if skill.lower() in job_lower:
                job_skills.append(skill)

        matching_skills = [s for s in skills if s.lower() in job_lower]
        skill_score = len(matching_skills) / max(len(job_skills), 1) if job_skills else 0

        # Keyword match
        job_keywords = set(re.findall(r"\b\w{4,}\b", job_lower))
        resume_keywords = set(re.findall(r"\b\w{4,}\b", text_lower))
        keyword_overlap = len(job_keywords & resume_keywords)
        keyword_score = min(keyword_overlap / max(len(job_keywords), 1), 1.0)

        # Experience match (simplified)
        years_required = None
        years_match = re.search(r"(\d+)\+?\s*years?", job_description, re.IGNORECASE)
        if years_match:
            years_required = int(years_match.group(1))

        total_years = self._calculate_total_experience(experience)
        exp_score = 1.0
        if years_required and total_years:
            exp_score = min(total_years / years_required, 1.0)

        # Overall score
        overall_score = (skill_score * 0.4 + keyword_score * 0.3 + exp_score * 0.3)

        details = {
            "skill_score": round(skill_score, 2),
            "keyword_score": round(keyword_score, 2),
            "experience_score": round(exp_score, 2),
            "matching_skills": matching_skills,
            "required_skills": job_skills,
            "years_required": years_required,
            "years_found": total_years,
        }

        return round(overall_score, 2), details

    def _calculate_confidence(
        self,
        name: Optional[str],
        email: Optional[str],
        education: List[Education],
        experience: List[WorkExperience],
    ) -> float:
        """Calculate overall confidence score."""
        score = 0.0

        if name:
            score += 0.2
        if email:
            score += 0.2
        if education:
            score += 0.3
        if experience:
            score += 0.3

        return min(score, 1.0)


# Singleton instance
resume_parser = ResumeParser()

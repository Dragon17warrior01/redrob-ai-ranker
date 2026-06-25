"""
state.py

Defines the data schema that flows through the LangGraph pipeline.

Design principle:
    The RAW nested data (career_history, skills, etc.) is preserved as-is
    inside ParsedCandidate, because downstream nodes like the Consistency
    Detector and Honeypot Detector need full fidelity (e.g. comparing a
    career entry's `title` against its own `description`).

    On top of the raw data, the parser also computes a small set of cheap
    DERIVED fields (most_recent_title, total_distinct_employers, etc.)
    so that nodes which only need aggregates (Technical/Behavioral feature
    engines) don't have to re-walk the nested lists every time.

    Sentinel values used by the source data (-1 for "no score available",
    {} for "no assessment data") are cleaned into proper None/null values
    at parse time, so every downstream node can trust that a present
    numeric field is a real number.
"""

from __future__ import annotations

from datetime import date
from typing import Optional

from pydantic import BaseModel, Field, field_validator


# ---------------------------------------------------------------------------
# Raw sub-structures (mirror the source JSON closely, just typed + cleaned)
# ---------------------------------------------------------------------------

class Profile(BaseModel):
    anonymized_name: str
    headline: str
    summary: str
    location: str
    country: str
    years_of_experience: float
    current_title: str
    current_company: str
    current_company_size: Optional[str] = None
    current_industry: Optional[str] = None


class CareerEntry(BaseModel):
    company: str
    title: str
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    duration_months: Optional[int] = None
    is_current: bool = False
    industry: Optional[str] = None
    company_size: Optional[str] = None
    description: str = ""


class EducationEntry(BaseModel):
    institution: str
    degree: str
    field_of_study: str
    start_year: Optional[int] = None
    end_year: Optional[int] = None
    grade: Optional[str] = None
    tier: Optional[str] = None


class SkillEntry(BaseModel):
    name: str
    proficiency: Optional[str] = None
    endorsements: int = 0
    duration_months: Optional[int] = None


class CertificationEntry(BaseModel):
    name: str
    issuer: Optional[str] = None
    year: Optional[int] = None


class LanguageEntry(BaseModel):
    language: str
    proficiency: Optional[str] = None


class SalaryRange(BaseModel):
    min: Optional[float] = None
    max: Optional[float] = None
    is_inverted: bool = False  # True if min > max in source data (data-quality flag)


class RedrobSignals(BaseModel):
    """
    Behavioral / platform engagement signals.

    Sentinel cleanup applied here:
        -1                  -> None  (sentinel for "not available")
        {} (empty dict)     -> None  (sentinel for "no assessment data")
    """
    profile_completeness_score: Optional[float] = None
    signup_date: Optional[date] = None
    last_active_date: Optional[date] = None
    open_to_work_flag: bool = False
    profile_views_received_30d: Optional[int] = None
    applications_submitted_30d: Optional[int] = None
    recruiter_response_rate: Optional[float] = None
    avg_response_time_hours: Optional[float] = None
    skill_assessment_scores: Optional[dict] = None
    connection_count: Optional[int] = None
    endorsements_received: Optional[int] = None
    notice_period_days: Optional[int] = None
    expected_salary_range_inr_lpa: Optional[SalaryRange] = None
    preferred_work_mode: Optional[str] = None
    willing_to_relocate: Optional[bool] = None
    github_activity_score: Optional[float] = None
    search_appearance_30d: Optional[int] = None
    saved_by_recruiters_30d: Optional[int] = None
    interview_completion_rate: Optional[float] = None
    offer_acceptance_rate: Optional[float] = None
    verified_email: bool = False
    verified_phone: bool = False
    linkedin_connected: bool = False

    @field_validator(
        "github_activity_score",
        "offer_acceptance_rate",
        mode="before",
    )
    @classmethod
    def clean_negative_sentinel(cls, v):
        """-1 is a documented sentinel for 'no data', not a real value."""
        if v is None:
            return None
        if isinstance(v, (int, float)) and v < 0:
            return None
        return v

    @field_validator("skill_assessment_scores", mode="before")
    @classmethod
    def clean_empty_dict(cls, v):
        """An empty {} means 'no assessment data', so treat it as None."""
        if v is None or v == {}:
            return None
        return v


# ---------------------------------------------------------------------------
# Derived aggregates (computed by the parser, not present in source data)
# ---------------------------------------------------------------------------

class DerivedCareerStats(BaseModel):
    """
    Cheap aggregates over career_history, computed once so downstream
    feature nodes don't need to re-walk the raw list.
    """
    most_recent_title: Optional[str] = None
    most_recent_description: Optional[str] = None
    total_distinct_employers: int = 0
    total_career_months: int = 0  # sum of duration_months across all entries
    num_roles_held: int = 0
    largest_gap_days: int = 0
    has_employment_gap: bool = False  # convenience flag: largest_gap_days > 60
    title_description_mismatch_flagged: bool = False
    # True if ANY career entry's title and description appear to describe
    # different job functions (cheap heuristic flag; the real consistency
    # check happens in consistency_detector.py — this is just a fast,
    # parser-level pre-flag the detector can use as a hint)

# ---------------------------------------------------------------------------
# Job Description schema
# ---------------------------------------------------------------------------

class JobDescription(BaseModel):

    title: Optional[str] = None

    required_skills: list[str] = Field(default_factory=list)

    preferred_skills: list[str] = Field(default_factory=list)

    minimum_experience: Optional[float] = None

    preferred_education: list[str] = Field(default_factory=list)

    certifications: list[str] = Field(default_factory=list)

    work_mode: Optional[str] = None

    location: Optional[str] = None
# ---------------------------------------------------------------------------
# Top-level parsed candidate object — this is what flows through the graph
# ---------------------------------------------------------------------------

class ParsedCandidate(BaseModel):
    candidate_id: str
    profile: Profile

    career_history: list[CareerEntry] = Field(default_factory=list)
    education: list[EducationEntry] = Field(default_factory=list)
    skills: list[SkillEntry] = Field(default_factory=list)
    certifications: list[CertificationEntry] = Field(default_factory=list)
    languages: list[LanguageEntry] = Field(default_factory=list)

    redrob_signals: RedrobSignals

    # derived, parser-computed aggregates
    derived: DerivedCareerStats = Field(default_factory=DerivedCareerStats)


# ---------------------------------------------------------------------------
# LangGraph pipeline state (Session 2 will wire this into graph.py)
# ---------------------------------------------------------------------------

class PipelineState(BaseModel):
    """
    Placeholder for the full LangGraph state object.
    Session 2 will expand this as technical/behavioral/consistency/honeypot
    scores get added. Kept minimal for now so parser.py has something
    concrete to populate.
    """
    candidate: ParsedCandidate
    job: JobDescription
    technical_score: Optional[float] = None
    behavioral_score: Optional[float] = None
    consistency_score: Optional[float] = None
    honeypot_penalty: Optional[float] = None
    final_score: Optional[float] = None
    reason: Optional[str] = None
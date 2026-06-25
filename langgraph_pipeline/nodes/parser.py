"""
parser.py  (System 1: Candidate Parser)

Reads raw candidate records (JSONL — one JSON object per line) and converts
each one into a validated ParsedCandidate (see state.py).

Responsibilities (per the project blueprint):
    - Read candidates.jsonl
    - Extract: candidate_id, experience, titles, companies, descriptions,
      skills, behavioral signals
    - Clean known sentinel values (-1, {}) so downstream nodes always see
      either a real value or None
    - Compute cheap derived career aggregates (most recent title, employer
      count, total months, largest employment gap, a temporary keyword-based
      title/description mismatch hint for the Consistency Detector)

Explicitly NOT this file's job:
    - Deciding whether a candidate is good/bad (that's the Scoring Engine)
    - Deciding what counts as a "real" employment gap (that's System 4 —
      this file only stores the raw largest_gap_days number)
    - Deep consistency/honeypot logic (Systems 4 and 5) — this file's
      mismatch hint is a cheap placeholder, not a verdict

CHANGE LOG (review pass applied on top of the original version):
    - print() -> logging
    - Added required-field validation (candidate_id, profile) with a clear
      ValueError instead of a buried KeyError
    - Fixed most-recent-role selection: previously assumed career_history[0]
      was "most recent" if no entry had is_current=True. That's not
      guaranteed by the schema. Now picks the entry with the latest
      start_date instead.
    - Negative duration_months values are now clamped to 0 before summing.
    - Employer names are normalized (stripped + lowercased) for the
      distinct-employer COUNT only; the original casing is still what's
      stored/displayed elsewhere.
    - Employment gap is now stored as largest_gap_days (an int), with
      has_employment_gap kept as a convenience boolean derived from it.
      The 60-day threshold is still here for the boolean convenience flag,
      but System 4 can use the raw number for its own logic instead of
      trusting this file's opinion on what counts as "a gap."
    - except Exception -> specific exceptions (JSONDecodeError, ValueError,
      KeyError, TypeError) so a real bug doesn't get silently swallowed
      alongside expected bad-data cases.
    - The keyword-bucket mismatch heuristic is KEPT (not deleted) but
      clearly labeled as a temporary placeholder. It is brittle by design
      and is meant to be replaced by an embedding-based cosine-similarity
      check in consistency_detector.py once Sentence Transformers is wired
      up in System 2. Deleting it now would leave zero mismatch signal
      until that system exists.
"""

from __future__ import annotations

import json
import logging
import time
from datetime import date as _date
from pathlib import Path
from typing import Any, Iterator

from langgraph_pipeline.state import (
    CareerEntry,
    CertificationEntry,
    DerivedCareerStats,
    EducationEntry,
    LanguageEntry,
    ParsedCandidate,
    Profile,
    RedrobSignals,
    SalaryRange,
    SkillEntry,
)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# TEMPORARY keyword-bucket heuristic for title/description mismatch
# ---------------------------------------------------------------------------
# PLACEHOLDER — replace with embedding cosine similarity in
# consistency_detector.py (System 4) once Sentence Transformers is wired up
# in System 2. This keyword approach is brittle (e.g. a "Data Analyst" whose
# description happens to mention "Kafka pipelines" could be flagged
# incorrectly) and the keyword lists are not exhaustive. It exists only so
# downstream nodes have SOME mismatch signal before System 2/4 are built.

_JOB_FAMILY_KEYWORDS: dict[str, list[str]] = {
    "engineering": ["pipeline", "kafka", "spark", "airflow", "kubernetes",
                    "api", "backend", "database", "code", "deploy", "schema"],
    "marketing": ["seo", "content", "campaign", "brand", "demand-generation",
                  "social", "editorial", "copy"],
    "design": ["brand identity", "packaging", "figma", "adobe", "typography",
               "visual system", "creative direction"],
    "mechanical": ["cad", "solidworks", "creo", "fea", "ansys", "dfm",
                   "prototype", "tooling", "subsystem"],
    "support_ops": ["support agent", "ticket", "escalation", "tier-1",
                     "tier-2", "knowledge base"],
    "finance": ["gaap", "ind-as", "general ledger", "fixed-asset", "audit",
                "tax filing", "month-end close"],
    "consulting": ["stakeholder management", "business diagnostics",
                   "process re-engineering", "slide-craft"],
    "sales": ["quota", "arr", "prospecting", "discovery call", "close rate",
              "consultative selling"],
    "logistics": ["fulfillment", "warehouse", "picking", "packing",
                  "outbound", "on-time fulfillment"],
}

_TITLE_TO_FAMILY: dict[str, str] = {
    "engineer": "engineering",
    "backend": "engineering",
    "analytics": "engineering",
    "marketing": "marketing",
    "designer": "design",
    "mechanical": "mechanical",
    "support": "support_ops",
    "accountant": "finance",
    "business analyst": "consulting",
    "sales": "sales",
    "operations manager": "logistics",
}


def _job_family_for_title(title: str) -> str | None:
    title_lower = title.lower()
    for key, family in _TITLE_TO_FAMILY.items():
        if key in title_lower:
            return family
    return None


def _cheap_keyword_mismatch_hint(title: str, description: str) -> bool:
    """
    TEMPORARY placeholder hint only. Returns True if the description
    strongly matches a DIFFERENT job family than the one implied by the
    title. Not a final verdict — System 4 should do its own deeper check.
    """
    title_family = _job_family_for_title(title)
    if title_family is None:
        return False

    description_lower = description.lower()
    title_family_hits = sum(
        1 for kw in _JOB_FAMILY_KEYWORDS[title_family] if kw in description_lower
    )

    other_family_hits: dict[str, int] = {}
    for family, keywords in _JOB_FAMILY_KEYWORDS.items():
        if family == title_family:
            continue
        hits = sum(1 for kw in keywords if kw in description_lower)
        if hits > 0:
            other_family_hits[family] = hits

    if not other_family_hits:
        return False

    _, best_other_hits = max(other_family_hits.items(), key=lambda kv: kv[1])
    return best_other_hits > title_family_hits


# ---------------------------------------------------------------------------
# Derived stats computation
# ---------------------------------------------------------------------------

EMPLOYMENT_GAP_THRESHOLD_DAYS = 60  # used only for the convenience boolean flag


def _compute_derived_stats(career_history: list[CareerEntry]) -> DerivedCareerStats:
    if not career_history:
        return DerivedCareerStats()

    # FIX: previously fell back to career_history[0] if no entry had
    # is_current=True, which silently assumed the list was already sorted
    # newest-first. The schema doesn't guarantee that ordering, so instead
    # pick whichever entry has the latest start_date. Entries with no
    # start_date are treated as earliest-possible so they don't win by
    # accident.
    # Prefer the explicitly marked current role if one exists.
    current_roles = [e for e in career_history if e.is_current]
    if current_roles:
        most_recent = current_roles[0]
    else:
    # Otherwise, fall back to the role with the latest start date.
        most_recent = max(
            career_history,
            key=lambda e: e.start_date or _date.min,
        )

    # FIX: normalize (strip + lowercase) for the distinct-employer COUNT
    # only. We don't mutate e.company itself, so the original casing is
    # still what's stored and displayed elsewhere.
    distinct_employers = {
        e.company.strip().lower() for e in career_history if e.company
    }

    # FIX: clamp negative duration_months to 0 before summing, since a
    # malformed negative value shouldn't be able to reduce total experience.
    total_months = sum(max(e.duration_months or 0, 0) for e in career_history)

    # FIX: store the actual largest gap in days rather than just a boolean.
    # This lets System 4 apply its own judgment (e.g. distinguishing a
    # planned career break from a suspicious unexplained gap) instead of
    # trusting this file's opinion on what counts as "a gap."
    largest_gap_days = 0
    sorted_entries = sorted(
        (e for e in career_history if e.start_date and e.end_date),
        key=lambda e: e.start_date,
    )
    for earlier, later in zip(sorted_entries, sorted_entries[1:]):
        gap_days = max(
            (later.start_date - earlier.end_date).days,
            0,
        )
        largest_gap_days = max(largest_gap_days, gap_days)

    mismatch_flagged = any(
        _cheap_keyword_mismatch_hint(e.title, e.description) for e in career_history
    )

    return DerivedCareerStats(
        most_recent_title=most_recent.title,
        most_recent_description=most_recent.description,
        total_distinct_employers=len(distinct_employers),
        total_career_months=total_months,
        num_roles_held=len(career_history),
        largest_gap_days=largest_gap_days,
        has_employment_gap=largest_gap_days > EMPLOYMENT_GAP_THRESHOLD_DAYS,
        title_description_mismatch_flagged=mismatch_flagged,
    )


# ---------------------------------------------------------------------------
# Salary range cleanup (flags min > max as a data-quality issue, doesn't drop it)
# ---------------------------------------------------------------------------

def _parse_salary_range(raw: dict | None) -> SalaryRange | None:
    if not raw:
        return None
    salary_min = raw.get("min")
    salary_max = raw.get("max")
    is_inverted = (
        salary_min is not None and salary_max is not None and salary_min > salary_max
    )
    return SalaryRange(min=salary_min, max=salary_max, is_inverted=is_inverted)


# ---------------------------------------------------------------------------
# Required-field validation
# ---------------------------------------------------------------------------

_REQUIRED_TOP_LEVEL_FIELDS = ["candidate_id", "profile"]


def _validate_required_fields(raw: dict[str, Any]) -> None:
    """
    Raises ValueError with a clear message if a required field is missing
    or empty, instead of letting a generic KeyError/TypeError surface from
    deep inside Pydantic construction.
    """
    for field in _REQUIRED_TOP_LEVEL_FIELDS:
        if field not in raw or raw[field] in (None, "", {}):
            raise ValueError(f"Missing or empty required field: '{field}'")

    candidate_id = raw["candidate_id"]
    if not isinstance(candidate_id, str) or not candidate_id.strip():
        raise ValueError(f"Invalid candidate_id: {candidate_id!r}")


# ---------------------------------------------------------------------------
# Single-record parsing
# ---------------------------------------------------------------------------

def parse_candidate_record(raw: dict[str, Any]) -> ParsedCandidate:
    """Convert one raw JSON dict (already json.loads'd) into a ParsedCandidate."""

    _validate_required_fields(raw)

    profile = Profile(**raw["profile"])

    career_history = [CareerEntry(**entry) for entry in raw.get("career_history", [])]
    education = [EducationEntry(**entry) for entry in raw.get("education", [])]
    skills = [SkillEntry(**entry) for entry in raw.get("skills", [])]
    certifications = [
        CertificationEntry(**entry) for entry in raw.get("certifications", [])
    ]
    languages = [LanguageEntry(**entry) for entry in raw.get("languages", [])]

    signals_raw = dict(raw.get("redrob_signals", {}))
    signals_raw["expected_salary_range_inr_lpa"] = _parse_salary_range(
        signals_raw.get("expected_salary_range_inr_lpa")
    )
    redrob_signals = RedrobSignals(**signals_raw)

    derived = _compute_derived_stats(career_history)

    return ParsedCandidate(
        candidate_id=raw["candidate_id"],
        profile=profile,
        career_history=career_history,
        education=education,
        skills=skills,
        certifications=certifications,
        languages=languages,
        redrob_signals=redrob_signals,
        derived=derived,
    )


# ---------------------------------------------------------------------------
# File-level streaming parse (memory-safe for 100k+ candidates)
# ---------------------------------------------------------------------------

def parse_candidates_file(path: str | Path) -> Iterator[ParsedCandidate]:
    """
    Streams candidates one at a time rather than loading the whole file into
    memory at once — important for the 16GB RAM constraint at 100k records.

    A single malformed line is skipped with a logged warning rather than
    crashing the whole run, since one bad record out of 100k shouldn't kill
    the pipeline (but is worth knowing about). Only the specific exception
    types we actually expect from bad data are caught here — a genuine bug
    elsewhere in the code should still raise and be visible.
    """
    path = Path(path)
    with path.open("r", encoding="utf-8") as f:
        for line_number, line in enumerate(f, start=1):
            line = line.strip()
            if not line:
                continue
            try:
                raw = json.loads(line)
                yield parse_candidate_record(raw)
            except json.JSONDecodeError as exc:
                logger.warning("Skipped line %d: invalid JSON (%s)", line_number, exc)
            except ValueError as exc:
                logger.warning("Skipped line %d: validation error (%s)", line_number, exc)
            except (KeyError, TypeError) as exc:
                logger.warning("Skipped line %d: malformed record (%s)", line_number, exc)


if __name__ == "__main__":
    # Quick manual smoke test against the sample file, with basic run stats
    # and timing (useful baseline for the 5-minute / 100k-candidate
    # benchmark we still need to validate).
    sample_path = Path(__file__).resolve().parents[2] / "data" / "sample_candidates.jsonl"

    start_time = time.time()
    total_lines = sum(1 for _ in sample_path.open("r", encoding="utf-8") if _.strip())

    success_count = 0
    for candidate in parse_candidates_file(sample_path):
        success_count += 1
        logger.info(
            "%s: most_recent_title=%r, employers=%d, mismatch_flag=%s, "
            "largest_gap_days=%d, github_score=%s, salary_inverted=%s",
            candidate.candidate_id,
            candidate.derived.most_recent_title,
            candidate.derived.total_distinct_employers,
            candidate.derived.title_description_mismatch_flagged,
            candidate.derived.largest_gap_days,
            candidate.redrob_signals.github_activity_score,
            candidate.redrob_signals.expected_salary_range_inr_lpa.is_inverted
            if candidate.redrob_signals.expected_salary_range_inr_lpa
            else None,
        )

    elapsed = time.time() - start_time
    failed_count = total_lines - success_count
    logger.info(
        "Done. total=%d success=%d failed=%d runtime=%.3fs",
        total_lines, success_count, failed_count, elapsed,
    )
from docx import Document

from langgraph_pipeline.nodes.job_parser import JobParser

from langgraph_pipeline.nodes.parser import (
    parse_candidates_file,
)

from langgraph_pipeline.nodes.technical_scorer import (
    TechnicalScorer,
)


# --------------------
# Load Job Description
# --------------------

doc = Document(
    "data/raw/job_description.docx"
)

job_text = "\n".join(

    paragraph.text

    for paragraph in doc.paragraphs

)

job_parser = JobParser()

job = job_parser.parse(
    job_text
)


# --------------------
# Load First Candidate
# --------------------

candidate = next(

    parse_candidates_file(
        "data/raw/candidates.jsonl"
    )

)


# --------------------
# Create Scorer
# --------------------

scorer = TechnicalScorer()


# --------------------
# Display Candidate
# --------------------

print("\n===== CANDIDATE =====\n")

print("ID:", candidate.candidate_id)

print(

    "Title:",

    candidate.profile.current_title

)

print(

    "Experience:",

    candidate.profile.years_of_experience

)


# --------------------
# Display Job
# --------------------

print("\n===== JOB =====\n")

print(

    "Title:",

    job.title

)


# --------------------
# Technical Breakdown
# --------------------

print("\n===== TECHNICAL BREAKDOWN =====\n")

print(

    "Skills:",

    scorer.score_skills(

        candidate,

        job,

    )

)

print(

    "Experience:",

    scorer.score_experience(

        candidate,

        job,

    )

)
# Temporary baseline score.
# Will later compare against
# JD education requirements.

print(

    "Education:",

    scorer.score_education(

        candidate,

        job,

    )

)

print(

    "Certifications:",

    scorer.score_certifications(

        candidate,

        job,

    )

)


# --------------------
# Final Score
# --------------------

print("\n===== FINAL SCORE =====\n")

print(

    scorer.calculate_total_score(

        candidate,

        job,

    )

)
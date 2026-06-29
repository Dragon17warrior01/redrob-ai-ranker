"""
rank.py

Generates the final ranked Top-100 candidate list from the completed
LangGraph pipeline.

Output CSV Columns:
    candidate_id
    rank
    score
    reasoning

Sorting:
    1. Highest final_score
    2. candidate_id ascending (tie-break)

No LLM is used.
Reasoning is generated entirely from existing pipeline outputs.
"""

from pathlib import Path
import csv

from pipeline_runner import run_pipeline


OUTPUT_DIR = Path("output")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

OUTPUT_FILE = OUTPUT_DIR / "top_100_candidates.csv"


def _safe_number(value):
    """Convert values safely to float."""
    try:
        return float(value)
    except Exception:
        return 0.0


def _candidate_id(state):
    """
    Extract candidate id from PipelineState.

    Supports:
        state["candidate"]["candidate_id"]
        state.candidate["candidate_id"]
        state.candidate.candidate_id
    """

    candidate = None

    if isinstance(state, dict):
        candidate = state.get("candidate")
    else:
        candidate = getattr(state, "candidate", None)

    if candidate is None:
        return ""

    if isinstance(candidate, dict):
        return (
            candidate.get("candidate_id")
            or candidate.get("id")
            or ""
        )

    return (
        getattr(candidate, "candidate_id", None)
        or getattr(candidate, "id", "")
    )


def _get_field(state, field):
    """
    Read PipelineState fields whether it is
    dict-like or attribute based.
    """

    if isinstance(state, dict):
        return state.get(field)

    return getattr(state, field, None)


def generate_reasoning(state):
    """
    Rule-based reasoning.

    Uses ONLY existing pipeline outputs.

    Pipeline fields:
        technical_score
        behavioral_score
        consistency_score
        honeypot_penalty
        final_score
    """

    technical = _safe_number(_get_field(state, "technical_score"))
    behavioral = _safe_number(_get_field(state, "behavioral_score"))
    consistency = _safe_number(_get_field(state, "consistency_score"))
    penalty = _safe_number(_get_field(state, "honeypot_penalty"))
    final_score = _safe_number(_get_field(state, "final_score"))

    reasons = []

    # Technical
    if technical >= 80:
        reasons.append("excellent technical match")
    elif technical >= 65:
        reasons.append("strong technical match")
    elif technical >= 50:
        reasons.append("moderate technical match")
    else:
        reasons.append("limited technical match")

    # Behavioral
    if behavioral >= 80:
        reasons.append("excellent behavioral profile")
    elif behavioral >= 65:
        reasons.append("strong behavioral profile")
    elif behavioral >= 50:
        reasons.append("acceptable behavioral profile")

    # Consistency
    if consistency >= 90:
        reasons.append("high profile consistency")
    elif consistency >= 75:
        reasons.append("good profile consistency")
    elif consistency >= 60:
        reasons.append("reasonable profile consistency")
    else:
        reasons.append("low profile consistency")

    # Honeypot penalty
    if penalty <= 0:
        reasons.append("no honeypot penalty")
    elif penalty <= 5:
        reasons.append("minor penalty applied")
    elif penalty <= 15:
        reasons.append("moderate penalty applied")
    else:
        reasons.append("significant penalty applied")

    # Final score summary
    if final_score >= 85:
        reasons.append("overall outstanding candidate")
    elif final_score >= 70:
        reasons.append("overall strong candidate")
    elif final_score >= 55:
        reasons.append("overall suitable candidate")
    else:
        reasons.append("overall limited fit")

    return "; ".join(reasons)


def rank_candidates(results):
    """
    Sort candidates.

    Primary:
        final_score descending

    Secondary:
        candidate_id ascending
    """

    ranked = sorted(
        results,
        key=lambda state: (
            -_safe_number(_get_field(state, "final_score")),
            str(_candidate_id(state)),
        ),
    )

    return ranked[:100]


def export_csv(top_candidates, output_file=OUTPUT_FILE):
    """
    Export Top-100 CSV.
    """

    with open(
        output_file,
        "w",
        newline="",
        encoding="utf-8",
    ) as csvfile:

        writer = csv.writer(csvfile)

        writer.writerow(
            [
                "candidate_id",
                "rank",
                "score",
                "reasoning",
            ]
        )

        for rank, state in enumerate(top_candidates, start=1):

            writer.writerow(
                [
                    _candidate_id(state),
                    rank,
                    round(
                        _safe_number(
                            _get_field(state, "final_score")
                        ),
                        2,
                    ),
                    generate_reasoning(state),
                ]
            )


def main():

    print("=" * 60)
    print("Running LangGraph Candidate Ranking Pipeline")
    print("=" * 60)

    results = run_pipeline()

    print()
    print(f"Pipeline returned {len(results)} candidates.")

    top_candidates = rank_candidates(results)

    print(f"Selected Top {len(top_candidates)} candidates.")

    export_csv(top_candidates)

    print()
    print(f"CSV exported to: {OUTPUT_FILE.resolve()}")
    print("Done.")


if __name__ == "__main__":
    main()
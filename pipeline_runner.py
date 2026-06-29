"""
pipeline_runner.py
"""

from pathlib import Path

from langgraph_pipeline.graph import graph
from langgraph_pipeline.state import PipelineState
from langgraph_pipeline.nodes.parser import parse_candidates_file
from langgraph_pipeline.nodes.job_parser import JobParser

CANDIDATE_FILE = Path("data/raw/candidates.jsonl")
JOB_DESCRIPTION_FILE = Path("data/raw/job_description.txt")


def run_pipeline(
    candidate_file=CANDIDATE_FILE,
    job_description_file=JOB_DESCRIPTION_FILE,
):
    print("1. Reading job description...")

    with open(job_description_file, "r", encoding="utf-8") as f:
        job_text = f.read()

    print("2. Parsing job description...")

    job = JobParser().parse(job_text)

    print("3. Job parsed successfully.")

    results = []

    print("4. Starting candidate evaluation...")

    for idx, candidate in enumerate(
        parse_candidates_file(candidate_file),
        start=1,
    ):

        state = PipelineState(
            candidate=candidate,
            job=job,
        )

        final_state = graph.invoke(state)

        results.append(final_state)

        if idx % 1000 == 0:
            print(f"Processed {idx} candidates...")

    print(f"Finished processing {len(results)} candidates.")

    return results


if __name__ == "__main__":
    run_pipeline()
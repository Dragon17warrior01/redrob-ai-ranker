"""
pipeline_runner.py
"""

from pathlib import Path

print("1. Imports started...")

from langgraph_pipeline.graph import graph
from langgraph_pipeline.state import PipelineState
from langgraph_pipeline.nodes.parser import parse_candidates_file
from langgraph_pipeline.nodes.job_parser import JobParser

print("2. Imports completed.")

CANDIDATE_FILE = Path("data/raw/candidates.jsonl")
JOB_DESCRIPTION_FILE = Path("data/raw/job_description.txt")

print("3. Reading job description...")

with open(JOB_DESCRIPTION_FILE, "r", encoding="utf-8") as f:
    job_text = f.read()

print("4. Parsing job description...")

job = JobParser().parse(job_text)

print("5. Job parsed successfully.")

results = []

print("6. Starting candidate loop...")

for candidate in parse_candidates_file(CANDIDATE_FILE):

    print(f"Processing {candidate.candidate_id}")

    state = PipelineState(
        candidate=candidate,
        job=job,
    )

    print("Calling graph...")

    final_state = graph.invoke(state)

    print("Graph returned.")

    results.append(final_state)

print("Done.")
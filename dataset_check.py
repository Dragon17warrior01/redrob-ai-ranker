import json

candidate_path = "data/raw/candidates.jsonl"

count = 0

with open(candidate_path, "r", encoding="utf-8") as f:

    for line in f:

        count += 1

        if count == 1:

            first_candidate = json.loads(line)

print("\n========== DATASET SUMMARY ==========\n")

print("Total candidates:", count)

print("\nCandidate fields:")

for field in first_candidate.keys():

    print("-", field)

print("\nCareer history entries:")

print(len(first_candidate["career_history"]))

print("\nSkills count:")

print(len(first_candidate["skills"]))

print("\nEducation entries:")

print(len(first_candidate["education"]))

print("\nRedrob signal count:")

print(len(first_candidate["redrob_signals"]))
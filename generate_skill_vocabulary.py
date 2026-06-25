import json

input_file = "data/raw/candidates.jsonl"

unique_skills = set()

with open(input_file, "r", encoding="utf-8") as f:

    for line in f:

        candidate = json.loads(line)

        skills = candidate.get("skills", [])

        for skill in skills:

            skill_name = skill.get("name")

            if skill_name:

                unique_skills.add(skill_name.strip())

skill_list = sorted(unique_skills)

output_file = "data/skill_vocabulary.json"

with open(output_file, "w", encoding="utf-8") as f:

    json.dump(skill_list, f, indent=4)

print(f"Total unique skills: {len(skill_list)}")

print(f"Saved to: {output_file}")
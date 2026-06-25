"""
job_parser.py

Converts raw job description text
into a structured JobDescription object.
"""

import json
import re

from pathlib import Path

from langgraph_pipeline.state import JobDescription


class JobParser:

    def __init__(self):

        vocabulary_path = Path(
            "feature_store/skill_vocabulary.json"
        )

        with open(
            vocabulary_path,
            "r",
            encoding="utf-8"
        ) as f:

            self.skill_vocabulary = json.load(f)

    def extract_skills(
        self,
        job_text: str
    ):

        found_skills = []

        text = job_text.lower()

        for skill in self.skill_vocabulary:

            if skill.lower() in text:

                found_skills.append(skill)

        return sorted(found_skills)

    def extract_experience(
        self,
        job_text: str
    ):

        pattern = r"(\d+)\+?\s*years"

        match = re.search(
            pattern,
            job_text.lower()
        )

        if match:

            return float(
                match.group(1)
            )

        return None

    def extract_work_mode(
        self,
        job_text: str
    ):

        text = job_text.lower()

        if "hybrid" in text:

            return "hybrid"

        if "remote" in text:

            return "remote"

        if "onsite" in text:

            return "onsite"

        return None

    def extract_location(
        self,
        job_text: str
    ):

        locations = [

            "Pune",

            "Noida",

            "Mumbai",

            "Hyderabad",

            "Delhi NCR",

            "Delhi",

            "Bangalore",

            "Chennai",

            "Gurgaon"

        ]

        found_locations = []

        text = job_text.lower()

        for city in locations:

            if city.lower() in text:

                found_locations.append(
                    city
                )

        if found_locations:

            return ", ".join(
                found_locations
            )

        return None

    def extract_title(
        self,
        job_text: str
    ):

        titles = [

            "Senior AI Engineer",

            "AI Engineer",

            "Machine Learning Engineer",

            "Data Scientist",

            "Data Engineer",

            "Software Engineer",

            "Backend Engineer",

            "Frontend Engineer"

        ]

        text = job_text.lower()

        for title in titles:

            if title.lower() in text:

                return title

        return None

    def parse(
        self,
        job_text: str
    ):

        job = JobDescription()

        job.title = self.extract_title(
            job_text
        )

        job.required_skills = self.extract_skills(
            job_text
        )

        job.minimum_experience = self.extract_experience(
            job_text
        )

        job.work_mode = self.extract_work_mode(
            job_text
        )

        job.location = self.extract_location(
            job_text
        )

        return job
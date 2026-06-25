"""
consistency_detector.py

Detects inconsistencies inside a candidate profile.

Returns a score between 0 and 100.

100 = highly consistent

0 = highly suspicious
"""

from langgraph_pipeline.state import ParsedCandidate


class ConsistencyDetector:

    def score_title_description_consistency(

        self,

        candidate: ParsedCandidate,

    ) -> float:

        suspicious = 0

        total = 0

        keywords = [

            "python",

            "machine learning",

            "data",

            "ai",

            "llm",

            "backend",

            "software",

            "cloud",

        ]

        for entry in candidate.career_history:

            total += 1

            title = entry.title.lower()

            description = entry.description.lower()

            if any(

                keyword in title

                for keyword in keywords

            ):

                if not any(

                    keyword in description

                    for keyword in keywords

                ):

                    suspicious += 1

        if total == 0:

            return 100.0

        score = (

            1

            - suspicious / total

        ) * 100

        return round(

            score,

            2,

        )

    def score_skill_usage_consistency(

        self,

        candidate: ParsedCandidate,

    ) -> float:

        descriptions = " ".join(

            entry.description.lower()

            for entry in candidate.career_history

        )

        total_skills = len(

            candidate.skills

        )

        if total_skills == 0:

            return 100.0

        matched = 0

        for skill in candidate.skills:

            skill_name = skill.name.lower()

            if skill_name in descriptions:

                matched += 1

        ratio = matched / total_skills

        if ratio >= 0.60:

            return 100.0

        if ratio >= 0.40:

            return 85.0

        if ratio >= 0.20:

            return 70.0

        return 60.0

    def score_job_hopping(

        self,

        candidate: ParsedCandidate,

    ) -> float:

        short_jobs = 0

        total_jobs = 0

        for entry in candidate.career_history:

            total_jobs += 1

            duration = entry.duration_months

            if duration:

                if duration < 6:

                    short_jobs += 1

        if total_jobs == 0:

            return 100.0

        score = (

            1

            - short_jobs / total_jobs

        ) * 100

        return round(

            score,

            2,

        )

    def calculate_final_score(

        self,

        candidate: ParsedCandidate,

    ) -> float:

        title_score = (

            self.score_title_description_consistency(

                candidate

            )

        )

        skill_score = (

            self.score_skill_usage_consistency(

                candidate

            )

        )

        hopping_score = (

            self.score_job_hopping(

                candidate

            )

        )

        total = (

            title_score * 0.40

            + skill_score * 0.40

            + hopping_score * 0.20

        )

        return round(

            total,

            2,

        )
"""
technical_scorer.py

Calculates a candidate's technical suitability
against a JobDescription.
"""

from typing import Optional

from langgraph_pipeline.state import (
    ParsedCandidate,
    JobDescription,
)


class TechnicalScorer:

    def __init__(
        self,

        skill_weight: float = 0.50,

        experience_weight: float = 0.25,

        education_weight: float = 0.15,

        certification_weight: float = 0.10,

        ignore_skills: Optional[set] = None,

    ):

        self.skill_weight = skill_weight

        self.experience_weight = experience_weight

        self.education_weight = education_weight

        self.certification_weight = certification_weight

        self.ignore_skills = ignore_skills or {

            "Marketing",

            "Go",

        }

        # Validate weights

        weights_sum = (

            self.skill_weight

            + self.experience_weight

            + self.education_weight

            + self.certification_weight

        )

        if abs(weights_sum - 1.0) > 0.001:

            raise ValueError(

                f"Weights must sum to 1.0, got {weights_sum}"

            )

    def score_skills(

        self,

        candidate: ParsedCandidate,

        job: JobDescription,

    ) -> float:

        try:

            candidate_skills = {

                skill.name.lower()

                for skill in (

                    candidate.skills or []

                )

            }

            job_skills = {

                skill.lower()

                for skill in (

                    job.required_skills or []

                )

                if skill not in self.ignore_skills

            }

            if not job_skills:

                return 100.0

            overlap = candidate_skills.intersection(

                job_skills

            )

            score = (

                len(overlap)

                /

                len(job_skills)

            ) * 100

            return min(

                score,

                100.0,

            )

        except Exception:

            return 0.0

    def score_experience(

        self,

        candidate: ParsedCandidate,

        job: JobDescription,

    ) -> float:

        try:

            candidate_exp = (

                candidate.profile.years_of_experience

            )

            required_exp = (

                job.minimum_experience

            )

            if required_exp is None:

                return 100.0

            ratio = (

                candidate_exp

                /

                required_exp

            )

            return min(

                ratio * 100,

                100.0,

            )

        except Exception:

            return 0.0

    def score_education(

        self,

        candidate: ParsedCandidate,

        job: JobDescription,

    ) -> float:

        try:

            if not candidate.education:

                return 0.0

            return 80.0

        except Exception:

            return 0.0

    def score_certifications(

        self,

        candidate: ParsedCandidate,

        job: JobDescription,

    ) -> float:

        try:

            if not candidate.certifications:

                return 0.0

            return 80.0

        except Exception:

            return 0.0

    def calculate_total_score(

        self,

        candidate: ParsedCandidate,

        job: JobDescription,

    ) -> float:

        skill_score = self.score_skills(

            candidate,

            job,

        )

        experience_score = self.score_experience(

            candidate,

            job,

        )

        education_score = self.score_education(

            candidate,

            job,

        )

        certification_score = self.score_certifications(

            candidate,

            job,

        )

        total = (

            skill_score

            * self.skill_weight

            +

            experience_score

            * self.experience_weight

            +

            education_score

            * self.education_weight

            +

            certification_score

            * self.certification_weight

        )

        return round(

            total,

            2,

        )
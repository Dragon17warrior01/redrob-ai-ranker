"""
behavioral_scorer.py

Calculates a candidate's behavioral score
using Redrob platform signals.
"""

from datetime import date

from langgraph_pipeline.state import ParsedCandidate


class BehavioralScorer:

    def score_profile_completeness(

        self,

        candidate: ParsedCandidate,

    ) -> float:

        score = (

            candidate.redrob_signals.profile_completeness_score

            or 0

        )

        return min(

            score,

            100,

        )

    def score_response_rate(

        self,

        candidate: ParsedCandidate,

    ) -> float:

        rate = (

            candidate.redrob_signals.recruiter_response_rate

            or 0

        )

        return round(
            rate * 100,
            2,
        )

    def score_interview_completion(

        self,

        candidate: ParsedCandidate,

    ) -> float:

        rate = (

            candidate.redrob_signals.interview_completion_rate

            or 0

        )

        return round(
            rate * 100,
            2,
        )

    def score_offer_acceptance(

        self,

        candidate: ParsedCandidate,

    ) -> float:

        rate = (

            candidate.redrob_signals.offer_acceptance_rate

            or 0

        )

        return round(
            rate * 100,
            2,
)

    def score_recency(

        self,

        candidate: ParsedCandidate,

    ) -> float:

        last_active = (

            candidate.redrob_signals.last_active_date

        )

        if last_active is None:

            return 0.0

        days_away = (

            date.today()

            -

            last_active

        ).days

        if days_away <= 7:

            return 100.0

        if days_away <= 30:

            return 80.0

        if days_away <= 90:

            return 50.0

        return 20.0

    def calculate_total_score(

        self,

        candidate: ParsedCandidate,

    ) -> float:

        profile = (

            self.score_profile_completeness(

                candidate

            )

        )

        response = (

            self.score_response_rate(

                candidate

            )

        )

        interview = (

            self.score_interview_completion(

                candidate

            )

        )

        offer = (

            self.score_offer_acceptance(

                candidate

            )

        )

        recency = (

            self.score_recency(

                candidate

            )

        )

        total = (

            profile * 0.25

            +

            response * 0.20

            +

            interview * 0.20

            +

            offer * 0.15

            +

            recency * 0.20

        )

        return round(

            total,

            2,

        )
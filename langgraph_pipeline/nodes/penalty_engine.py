"""
penalty_engine.py

Converts consistency scores
into penalty points.

Higher consistency

↓

Lower penalty
"""


class PenaltyEngine:

    def calculate_penalty(

        self,

        consistency_score: float,

    ) -> float:

        if consistency_score >= 95:

            return 0.0

        if consistency_score >= 85:

            return 1.0

        if consistency_score >= 75:

            return 3.0

        if consistency_score >= 60:

            return 5.0

        if consistency_score >= 40:

            return 8.0

        return 12.0
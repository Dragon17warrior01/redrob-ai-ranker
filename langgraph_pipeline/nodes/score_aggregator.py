"""
score_aggregator.py

Combines technical and behavioral scores
into one overall score.

Penalty points are deducted from the
weighted score to produce the final score.
"""


class ScoreAggregator:

    def __init__(

        self,

        technical_weight: float = 0.70,

        behavioral_weight: float = 0.30,

    ):

        self.technical_weight = technical_weight

        self.behavioral_weight = behavioral_weight

        # Validate weights
        weights_sum = (

            self.technical_weight

            +

            self.behavioral_weight

        )

        if abs(weights_sum - 1.0) > 0.001:

            raise ValueError(

                f"Weights must sum to 1.0, got {weights_sum}"

            )

    def calculate_final_score(

        self,

        technical_score: float,

        behavioral_score: float,

        penalty: float,

    ) -> float:

        total = (

            technical_score

            * self.technical_weight

            +

            behavioral_score

            * self.behavioral_weight

            -

            penalty

        )

        # Final score should never be negative.
        return round(

            max(total, 0.0),

            2,

        )
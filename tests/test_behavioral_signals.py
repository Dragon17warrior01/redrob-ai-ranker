from langgraph_pipeline.nodes.parser import (
    parse_candidates_file,
)

from langgraph_pipeline.nodes.behavioral_scorer import (
    BehavioralScorer,
)


candidate = next(

    parse_candidates_file(

        "data/raw/candidates.jsonl"

    )

)

scorer = BehavioralScorer()


print("\n===== BEHAVIORAL BREAKDOWN =====\n")


print(

    "Profile:",

    scorer.score_profile_completeness(

        candidate

    )

)

print(

    "Response:",

    scorer.score_response_rate(

        candidate

    )

)

print(

    "Interview:",

    scorer.score_interview_completion(

        candidate

    )

)

print(

    "Offer:",

    scorer.score_offer_acceptance(

        candidate

    )

)

print(

    "Recency:",

    scorer.score_recency(

        candidate

    )

)


print("\n===== FINAL SCORE =====\n")


print(

    scorer.calculate_total_score(

        candidate

    )

)
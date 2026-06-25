from langgraph_pipeline.nodes.parser import (

    parse_candidates_file,

)

from langgraph_pipeline.nodes.consistency_detector import (

    ConsistencyDetector,

)


candidate = next(

    parse_candidates_file(

        "data/raw/candidates.jsonl"

    )

)


detector = ConsistencyDetector()


print(

    "\n===== CONSISTENCY BREAKDOWN =====\n"

)


print(

    "Title:",

    detector.score_title_description_consistency(

        candidate,

    )

)


print(

    "Skill Usage:",

    detector.score_skill_usage_consistency(

        candidate,

    )

)


print(

    "Job Hopping:",

    detector.score_job_hopping(

        candidate,

    )

)


print(

    "\n===== FINAL SCORE =====\n"

)


print(

    detector.calculate_final_score(

        candidate,

    )

)
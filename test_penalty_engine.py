from langgraph_pipeline.nodes.penalty_engine import (

    PenaltyEngine,

)


consistency_score = 84.0


engine = PenaltyEngine()


penalty = engine.calculate_penalty(

    consistency_score

)


print(

    "\n===== PENALTY =====\n"

)


print(

    penalty

)
from langgraph_pipeline.nodes.score_aggregator import (
    ScoreAggregator,
)


technical_score = 38.31

behavioral_score = 61.42


aggregator = ScoreAggregator()


final_score = aggregator.calculate_final_score(

    technical_score,

    behavioral_score,

)


print("\n===== FINAL RANKING SCORE =====\n")

print(

    final_score

)
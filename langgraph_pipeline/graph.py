"""
graph.py

Defines the LangGraph workflow for candidate evaluation.
"""

from langgraph.graph import StateGraph, START, END

from langgraph_pipeline.state import PipelineState

from langgraph_pipeline.nodes.technical_scorer import TechnicalScorer
from langgraph_pipeline.nodes.behavioral_scorer import BehavioralScorer
from langgraph_pipeline.nodes.consistency_detector import ConsistencyDetector
from langgraph_pipeline.nodes.penalty_engine import PenaltyEngine
from langgraph_pipeline.nodes.score_aggregator import ScoreAggregator


technical_scorer = TechnicalScorer()
behavioral_scorer = BehavioralScorer()
consistency_detector = ConsistencyDetector()
penalty_engine = PenaltyEngine()
score_aggregator = ScoreAggregator()


def technical_node(state: PipelineState) -> PipelineState:
    state.technical_score = technical_scorer.calculate_total_score(
        state.candidate,
        state.job,
    )
    return state


def behavioral_node(state: PipelineState) -> PipelineState:
    state.behavioral_score = behavioral_scorer.calculate_total_score(
        state.candidate,
    )
    return state


def consistency_node(state: PipelineState) -> PipelineState:
    # Change to calculate_total_score() if you rename it later.
    state.consistency_score = consistency_detector.calculate_final_score(
        state.candidate,
    )
    return state


def penalty_node(state: PipelineState) -> PipelineState:
    state.honeypot_penalty = penalty_engine.calculate_penalty(
        state.consistency_score,
    )
    return state


def aggregation_node(state: PipelineState) -> PipelineState:
    state.final_score = score_aggregator.calculate_final_score(
        technical_score=state.technical_score,
        behavioral_score=state.behavioral_score,
        penalty=state.honeypot_penalty,
    )
    return state


def build_graph():

    workflow = StateGraph(PipelineState)

    workflow.add_node("technical", technical_node)
    workflow.add_node("behavioral", behavioral_node)
    workflow.add_node("consistency", consistency_node)
    workflow.add_node("penalty", penalty_node)
    workflow.add_node("aggregate", aggregation_node)

    workflow.add_edge(START, "technical")
    workflow.add_edge("technical", "behavioral")
    workflow.add_edge("behavioral", "consistency")
    workflow.add_edge("consistency", "penalty")
    workflow.add_edge("penalty", "aggregate")
    workflow.add_edge("aggregate", END)

    return workflow.compile()


graph = build_graph()
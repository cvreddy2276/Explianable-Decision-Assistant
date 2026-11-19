"""LangGraph workflow orchestration for the agent pipeline."""

import logging
from typing import Any, Dict, List, TypedDict

from langgraph.graph import END, START, StateGraph

from backend.agents.explanation_agent import explanation_agent
from backend.agents.fairness_agent import fairness_agent
from backend.agents.summary_agent import summary_agent
from backend.agents.transparency_agent import transparency_agent

logger = logging.getLogger(__name__)


class DecisionState(TypedDict, total=False):
    """State passed through the four-agent LangGraph workflow."""

    decision: Dict[str, Any]
    decision_explanation: str
    fairness_assessment: str
    influencing_factors: List[str]
    final_summary: str


def build_explanation_graph():
    """Build the sequential explanation, fairness, transparency, and summary graph."""
    graph = StateGraph(DecisionState)
    graph.add_node("ExplanationAgent", explanation_agent)
    graph.add_node("FairnessAgent", fairness_agent)
    graph.add_node("TransparencyAgent", transparency_agent)
    graph.add_node("SummaryAgent", summary_agent)

    graph.add_edge(START, "ExplanationAgent")
    graph.add_edge("ExplanationAgent", "FairnessAgent")
    graph.add_edge("FairnessAgent", "TransparencyAgent")
    graph.add_edge("TransparencyAgent", "SummaryAgent")
    graph.add_edge("SummaryAgent", END)

    return graph.compile()


explanation_graph = build_explanation_graph()


def run_explanation(decision: Dict[str, Any]) -> Dict[str, Any]:
    """Execute the LangGraph workflow and return its final report fields."""
    logger.info("Running explanation graph")
    result = explanation_graph.invoke({"decision": decision})
    return {
        "decision_explanation": result.get("decision_explanation", ""),
        "fairness_assessment": result.get("fairness_assessment", ""),
        "influencing_factors": result.get("influencing_factors", []),
        "final_summary": result.get("final_summary", ""),
    }

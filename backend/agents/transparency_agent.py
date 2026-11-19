"""Transparency agent for extracting the factors that influenced a decision."""

import json
import logging
from typing import Any, Dict, List

from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate

from .explanation_agent import create_explanation_llm

logger = logging.getLogger(__name__)

TRANSPARENCY_PROMPT = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """Identify the most influential factors in the operational decision.
Respond with a valid JSON array of concise factor names only.
Use existing keys where possible. Do not include explanations or markdown.
Example: ["experience", "traffic_score", "distance"]""",
        ),
        (
            "human",
            "Decision data:\n{decision_json}\n\nInfluencing factors:",
        ),
    ]
)


def _parse_factor_list(raw_result: str) -> List[str]:
    """Parse JSON factors while tolerating fenced or noisy model output."""
    cleaned = raw_result.strip()
    if cleaned.startswith("```"):
        cleaned = cleaned.strip("`")
        if "\n" in cleaned:
            cleaned = cleaned.split("\n", 1)[1]
        if cleaned.endswith("```"):
            cleaned = cleaned[:-3]
    try:
        parsed = json.loads(cleaned)
        if isinstance(parsed, list):
            return [str(item).strip() for item in parsed if str(item).strip()]
    except json.JSONDecodeError:
        pass

    decision_fields = [
        "experience",
        "traffic_score",
        "distance",
        "employee",
        "assigned_route",
    ]
    return [field for field in decision_fields if field in raw_result]


def transparency_agent(state: Dict[str, Any]) -> Dict[str, Any]:
    """Extract a list of factors likely or stated to influence the decision."""
    try:
        decision_json = json.dumps(state["decision"], ensure_ascii=False, indent=2)
        chain = TRANSPARENCY_PROMPT | create_explanation_llm() | StrOutputParser()
        raw_result = chain.invoke({"decision_json": decision_json}).strip()
        factors = _parse_factor_list(raw_result)
    except Exception as exc:
        logger.exception("Transparency agent failed")
        factors = [
            key
            for key in ("experience", "traffic_score", "distance")
            if key in state.get("decision", {})
        ]

    if not factors:
        factors = [
            key
            for key in state.get("decision", {})
            if key not in {"employee", "assigned_route"}
        ]

    return {**state, "influencing_factors": factors}

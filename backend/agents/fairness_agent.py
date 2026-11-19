"""Fairness agent for a cautious, data-grounded fairness assessment."""

import json
import logging
from typing import Any, Dict

from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI

from .explanation_agent import create_explanation_llm

logger = logging.getLogger(__name__)

FAIRNESS_PROMPT = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """Evaluate whether the operational decision appears fair based only on the provided data.
Consider consistency and whether factors appear relevant to the decision.
Do not claim protected characteristics or actual discrimination unless they appear in the data.
Begin with "The decision appears fair" or "The decision may need review".
Explain uncertainty. Keep the answer to 2-3 sentences.""",
        ),
        (
            "human",
            "Decision data:\n{decision_json}\n\nFairness assessment:",
        ),
    ]
)


def fairness_agent(state: Dict[str, Any]) -> Dict[str, Any]:
    """Assess apparent fairness without overstating conclusions."""
    try:
        decision_json = json.dumps(state["decision"], ensure_ascii=False, indent=2)
        chain = FAIRNESS_PROMPT | create_explanation_llm() | StrOutputParser()
        result = chain.invoke({"decision_json": decision_json}).strip()
    except Exception as exc:
        logger.exception("Fairness agent failed")
        result = (
            "The decision may need review because a complete fairness assessment "
            f"could not be generated: {exc}"
        )

    return {**state, "fairness_assessment": result}

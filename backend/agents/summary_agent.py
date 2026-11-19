"""Summary agent for assembling the final human-friendly report."""

import logging
from typing import Any, Dict

from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate

from .explanation_agent import create_explanation_llm

logger = logging.getLogger(__name__)

SUMMARY_PROMPT = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """Combine the explanation, fairness review, and influencing factors into one final report.
Write a short, plain-language summary for a non-technical audience.
Do not add facts that are not present in the supplied agent results.
Keep it to 2-4 sentences.""",
        ),
        (
            "human",
            """Decision explanation:
{decision_explanation}

Fairness assessment:
{fairness_assessment}

Influencing factors:
{influencing_factors}

Final summary:""",
        ),
    ]
)


def summary_agent(state: Dict[str, Any]) -> Dict[str, Any]:
    """Combine prior agent outputs into the final user-facing summary."""
    try:
        chain = SUMMARY_PROMPT | create_explanation_llm() | StrOutputParser()
        final_summary = chain.invoke(
            {
                "decision_explanation": state.get("decision_explanation", ""),
                "fairness_assessment": state.get("fairness_assessment", ""),
                "influencing_factors": ", ".join(
                    state.get("influencing_factors", [])
                ),
            }
        ).strip()
    except Exception as exc:
        logger.exception("Summary agent failed")
        factors = ", ".join(state.get("influencing_factors", []))
        final_summary = (
            f"{state.get('decision_explanation', '')} "
            f"{state.get('fairness_assessment', '')} "
            f"The main factors listed were: {factors or 'not identified'}. "
            f"An AI-generated summary could not be completed: {exc}"
        )

    return {**state, "final_summary": final_summary}

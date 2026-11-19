"""Explanation agent for producing a plain-language decision explanation."""

import json
import logging
import os
from typing import Any, Dict

from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI

logger = logging.getLogger(__name__)

EXPLANATION_PROMPT = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """You explain operational decisions to non-technical users.
Use only the supplied JSON data. Explain what was decided and why, in simple English.
Do not invent missing facts or data. Keep it concise (2-4 sentences).""",
        ),
        (
            "human",
            "Operational decision data:\n{decision_json}\n\nProduce the explanation:",
        ),
    ]
)


def create_explanation_llm() -> ChatOpenAI:
    """Create the shared OpenRouter-compatible chat model."""
    return ChatOpenAI(
        model="openai/gpt-4o-mini",
        base_url="https://openrouter.ai/api/v1",
        api_key=os.getenv("OPENROUTER_API_KEY"),
        temperature=0,
        timeout=60,
    )


def explanation_agent(state: Dict[str, Any]) -> Dict[str, Any]:
    """Analyze the decision and write a clear natural-language explanation."""
    try:
        decision_json = json.dumps(state["decision"], ensure_ascii=False, indent=2)
        chain = EXPLANATION_PROMPT | create_explanation_llm() | StrOutputParser()
        result = chain.invoke({"decision_json": decision_json}).strip()
    except Exception as exc:
        logger.exception("Explanation agent failed")
        decision = state.get("decision", {})
        employee = decision.get("employee", "The employee")
        route = decision.get("assigned_route", "the assigned option")
        result = (
            f"{employee} was assigned {route}. The available details suggest that "
            "experience, traffic conditions, and travel distance were considered. "
            f"A detailed AI explanation could not be generated: {exc}"
        )

    return {**state, "decision_explanation": result}

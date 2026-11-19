"""LangSmith LLM-as-a-judge evaluation for generated decision explanations.

Run from the project root:
    python evaluation/langsmith_evaluation.py
"""

import json
import logging
import os
from typing import Any, Dict

from dotenv import load_dotenv
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from langsmith import traceable

from backend.graph import run_explanation

load_dotenv()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

JUDGE_PROMPT = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """You are an impartial evaluator for an operational decision explanation.
Rate the report from 1 (poor) to 5 (excellent) on:
- clarity: understandable and well organized
- simplicity: suitable for a non-technical audience
- completeness: covers explanation, fairness, factors, and summary
- transparency: explicitly distinguishes provided facts from uncertainty

Return valid JSON only:
{{"clarity": 1-5, "simplicity": 1-5, "completeness": 1-5, "transparency": 1-5, "reason": "brief reason"}}""",
        ),
        (
            "human",
            "Decision:\n{decision}\n\nGenerated report:\n{report}",
        ),
    ]
)


def make_judge() -> ChatOpenAI:
    """Create the evaluator model using OpenRouter."""
    return ChatOpenAI(
        model="openai/gpt-4o-mini",
        base_url="https://openrouter.ai/api/v1",
        api_key=os.getenv("OPENROUTER_API_KEY"),
        temperature=0,
        timeout=60,
    )


@traceable(name="explanation-evaluation")
def evaluate_example(decision: Dict[str, Any]) -> Dict[str, Any]:
    """Generate a report, judge it, and return scores."""
    report = run_explanation(decision)
    judge = JUDGE_PROMPT | make_judge() | StrOutputParser()
    raw_scores = judge.invoke(
        {
            "decision": json.dumps(decision, ensure_ascii=False),
            "report": json.dumps(report, ensure_ascii=False),
        }
    )

    cleaned = raw_scores.strip()
    if cleaned.startswith("```"):
        cleaned = cleaned.strip("`").split("\n", 1)[-1]
        if cleaned.endswith("```"):
            cleaned = cleaned[:-3]

    try:
        scores = json.loads(cleaned)
    except json.JSONDecodeError:
        logger.error("Judge returned invalid JSON: %s", raw_scores)
        scores = {"reason": "Judge output could not be parsed"}

    return {"decision": decision, "report": report, "scores": scores}


def main() -> None:
    """Evaluate sample decisions and emit LangSmith-traced results."""
    if not os.getenv("OPENROUTER_API_KEY"):
        raise RuntimeError("OPENROUTER_API_KEY is required.")

    with open("sample_data/decisions.json", "r", encoding="utf-8") as file:
        decisions = json.load(file)

    results = [evaluate_example(decision) for decision in decisions]
    print(json.dumps(results, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()

"""FastAPI application for the Explainable Decision Assistant."""

import logging
from contextlib import asynccontextmanager

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from backend.graph import run_explanation
from backend.models import DecisionInput, ExplanationReport

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s - %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Explainable Decision Assistant API starting")
    yield
    logger.info("Explainable Decision Assistant API stopping")


app = FastAPI(
    title="Explainable Decision Assistant",
    description="Multi-agent explanations for operational decisions",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health() -> dict[str, str]:
    """Return API health status."""
    return {"status": "ok"}


@app.post("/explain", response_model=ExplanationReport)
def explain_decision(decision: DecisionInput) -> ExplanationReport:
    """Run the LangGraph agent workflow for one operational decision."""
    try:
        report = run_explanation(decision.to_decision_dict())
        return ExplanationReport(**report)
    except Exception as exc:
        logger.exception("Unable to explain operational decision")
        raise HTTPException(
            status_code=500,
            detail="The explanation workflow could not complete.",
        ) from exc

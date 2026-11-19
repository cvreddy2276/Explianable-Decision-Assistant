"""Pydantic request and response models for the Explainable Decision Assistant."""

from typing import Any, Dict, List

from pydantic import BaseModel, ConfigDict, Field


class DecisionInput(BaseModel):
    """Operational decision data accepted by the API and UI."""

    model_config = ConfigDict(extra="allow")

    employee: str = Field(..., description="Person or subject receiving the decision")
    experience: float = Field(..., ge=0, description="Relevant experience in years")
    traffic_score: float = Field(..., ge=0, description="Traffic or workload risk score")
    distance: float = Field(..., ge=0, description="Distance or travel requirement")
    assigned_route: str = Field(..., description="Route, shift, task, or allocation assigned")

    def to_decision_dict(self) -> Dict[str, Any]:
        """Return the complete input, including optional operational fields."""
        return self.model_dump(exclude_none=True)


class ExplanationReport(BaseModel):
    """Final explanation returned to API and frontend users."""

    decision_explanation: str
    fairness_assessment: str
    influencing_factors: List[str]
    final_summary: str

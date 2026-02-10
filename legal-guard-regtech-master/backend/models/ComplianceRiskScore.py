from pydantic import BaseModel
from typing import List, Dict

class ComplianceRiskScore(BaseModel):
    overall_score: int  # 0-100
    financial_risk_estimate: float
    violation_categories: List[str]
    jurisdiction_risks: Dict[str, int]
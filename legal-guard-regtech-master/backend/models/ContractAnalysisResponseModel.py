from pydantic import BaseModel
from typing import List, Optional

class ClauseFlag(BaseModel):
    clause_text: str
    issue: Optional[str] = None
    severity: Optional[str] = "low"

class ComplianceFeedback(BaseModel):
    law: str                      # e.g., PDPA, GDPR
    missing_requirements: List[str]
    recommendations: List[str]

class ContractAnalysisResponse(BaseModel):
    summary: str
    flagged_clauses: List[ClauseFlag]
    compliance_issues: Optional[List[ComplianceFeedback]] = []
    jurisdiction: Optional[str] = "Unknown"

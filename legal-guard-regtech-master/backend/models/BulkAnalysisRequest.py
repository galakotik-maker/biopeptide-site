import datetime
from typing import List, Optional
from pydantic import BaseModel
from models.ContractAnalysisModel import ContractAnalysisRequest

class BulkAnalysisRequest(BaseModel):
    contracts: List[ContractAnalysisRequest]
    priority: str = "normal"
    notification_email: Optional[str] = None
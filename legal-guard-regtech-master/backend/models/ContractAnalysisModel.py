from pydantic import BaseModel
from typing import Optional

class ContractAnalysisRequest(BaseModel):
    text: str                      
    jurisdiction: Optional[str] = "MY" 

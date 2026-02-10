from datetime import datetime
from typing import List
from pydantic import BaseModel

class RegulatoryAlert(BaseModel):
    id: str
    title: str
    jurisdiction: str
    severity: str
    impact_description: str
    affected_contract_types: List[str]
    published_date: datetime

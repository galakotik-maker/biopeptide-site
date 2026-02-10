from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Any

class Regulation(BaseModel):
    """Simplified model for regulation information"""
    law_id: str = Field(..., description="Unique identifier for the law")
    name: str = Field(..., description="Full name of the regulation")
    jurisdiction: str = Field(..., description="Jurisdiction (e.g., EU, MY, SG, US)")
    type: str = Field(..., description="Type of regulation (e.g., Data Protection, Employment)")
    description: str = Field(..., description="Brief description of the regulation")
    key_provisions: List[str] = Field(default_factory=list, description="Key provisions list")
    
class RegulationListResponse(BaseModel):
    """Response model for regulation list"""
    regulations: List[Regulation] = Field(..., description="List of available regulations")
    total_count: int = Field(..., description="Total number of regulations")
    jurisdictions: List[str] = Field(..., description="Available jurisdictions")

class RegulationDetailResponse(BaseModel):
    """Response model for detailed regulation information"""
    regulation: Regulation = Field(..., description="Regulation details")
    disclaimer: Optional[str] = Field(None, description="Disclaimer notes")
    sources: Optional[str] = Field(None, description="Source references")

class RegulationSearchRequest(BaseModel):
    """Request model for regulation search"""
    jurisdiction: Optional[str] = Field(None, description="Filter by jurisdiction")
    regulation_type: Optional[str] = Field(None, description="Filter by regulation type")
    search_term: Optional[str] = Field(None, description="Search term for regulation content")

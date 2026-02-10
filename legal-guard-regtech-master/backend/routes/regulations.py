from fastapi import APIRouter, HTTPException, Query, Path
from typing import List, Optional

from models.RegulationModel import (
    RegulationListResponse, RegulationDetailResponse, RegulationSearchRequest
)
from service.SimpleRegulationService import RegulationService

# Initialize router
router = APIRouter(prefix="/regulations", tags=["regulations"])

# Initialize service
regulation_service = RegulationService()

@router.get("/", response_model=RegulationListResponse)
async def get_all_regulations():
    """
    Get a list of all available regulations.
    """
    try:
        return regulation_service.get_all_regulations()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve regulations: {str(e)}")

@router.get("/{law_id}", response_model=RegulationDetailResponse)
async def get_regulation_detail(
    law_id: str = Path(..., description="The unique identifier of the regulation")
):
    """
    Get detailed information for a specific regulation.
    """
    try:
        regulation = regulation_service.get_regulation_by_id(law_id)
        if regulation is None:
            raise HTTPException(status_code=404, detail=f"Regulation {law_id} not found")
        return regulation
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve regulation: {str(e)}")

@router.post("/search", response_model=RegulationListResponse)
async def search_regulations(search_request: RegulationSearchRequest):
    """
    Search regulations with filters.
    """
    try:
        return regulation_service.search_regulations(
            jurisdiction=search_request.jurisdiction,
            regulation_type=search_request.regulation_type,
            search_term=search_request.search_term
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to search regulations: {str(e)}")

@router.get("/jurisdictions/list")
async def get_jurisdictions():
    """
    Get list of available jurisdictions.
    """
    try:
        jurisdictions = regulation_service.get_jurisdictions()
        return {"jurisdictions": jurisdictions}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve jurisdictions: {str(e)}")

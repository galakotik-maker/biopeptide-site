import json
import os
from typing import List, Optional, Dict, Any
from backend.models.RegulationModel import Regulation, RegulationListResponse, RegulationDetailResponse

class RegulationService:
    """Service for managing regulatory data and compliance guidance"""
    
    def __init__(self):
        self.base_path = Path(__file__).parent.parent / "data"
        self.laws_path = self.base_path / "laws"
        self.disclaimer_path = self.base_path / "disclaimer"
        self.sources_path = self.base_path / "sources"
        self.mappings_path = self.base_path / "general" / "mappings.json"
        
        # Cache for loaded regulations
        self._regulations_cache: Dict[str, Dict] = {}
        self._mappings_cache: Optional[Dict] = None
        
        # Load mappings on initialization
        self._load_mappings()
    
    def _load_mappings(self) -> None:
        """Load jurisdiction mappings"""
        try:
            with open(self.mappings_path, 'r', encoding='utf-8') as f:
                self._mappings_cache = json.load(f)
                logger.info("Loaded jurisdiction mappings")
        except Exception as e:
            logger.error(f"Failed to load mappings: {e}")
            self._mappings_cache = {}
    
    def _load_regulation_file(self, law_id: str) -> Optional[Dict]:
        """Load a specific regulation file"""
        if law_id in self._regulations_cache:
            return self._regulations_cache[law_id]
        
        file_path = self.laws_path / f"{law_id}.json"
        if not file_path.exists():
            logger.warning(f"Regulation file not found: {file_path}")
            return None
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                regulation_data = json.load(f)
                self._regulations_cache[law_id] = regulation_data
                return regulation_data
        except Exception as e:
            logger.error(f"Failed to load regulation {law_id}: {e}")
            return None
    
    def _load_disclaimer(self, law_id: str) -> Optional[str]:
        """Load disclaimer notes for a regulation"""
        file_path = self.disclaimer_path / f"{law_id}_notes.md"
        if not file_path.exists():
            return None
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            logger.error(f"Failed to load disclaimer for {law_id}: {e}")
            return None
    
    def _load_sources(self, law_id: str) -> Optional[str]:
        """Load source references for a regulation"""
        file_path = self.sources_path / f"{law_id}_sources.md"
        if not file_path.exists():
            return None
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            logger.error(f"Failed to load sources for {law_id}: {e}")
            return None
    
    def get_all_regulations(self) -> List[RegulationSummary]:
        """Get summary of all available regulations"""
        regulations = []
        
        # Get all law files
        if not self.laws_path.exists():
            logger.error(f"Laws directory not found: {self.laws_path}")
            return regulations
        
        for law_file in self.laws_path.glob("*.json"):
            law_id = law_file.stem
            regulation_data = self._load_regulation_file(law_id)
            
            if regulation_data:
                try:
                    # Create regulation summary
                    metadata = RegulationMetadata(**regulation_data.get("metadata", {}))
                    applicability = RegulationApplicability(**regulation_data.get("applicability", {}))
                    
                    summary = RegulationSummary(
                        law_id=law_id,
                        metadata=metadata,
                        applicability=applicability,
                        key_provisions_count=len(regulation_data.get("key_provisions", {})),
                        disclaimer_available=self._load_disclaimer(law_id) is not None,
                        sources_available=self._load_sources(law_id) is not None
                    )
                    regulations.append(summary)
                    
                except Exception as e:
                    logger.error(f"Failed to create summary for {law_id}: {e}")
        
        return regulations
    
    def get_regulation_detail(self, law_id: str) -> Optional[RegulationDetail]:
        """Get detailed information for a specific regulation"""
        regulation_data = self._load_regulation_file(law_id)
        if not regulation_data:
            return None
        
        try:
            # Parse provisions
            key_provisions = {}
            for provision_name, provision_data in regulation_data.get("key_provisions", {}).items():
                key_provisions[provision_name] = RegulationProvision(**provision_data)
            
            # Create detailed regulation model
            detail = RegulationDetail(
                law_id=law_id,
                metadata=RegulationMetadata(**regulation_data.get("metadata", {})),
                applicability=RegulationApplicability(**regulation_data.get("applicability", {})),
                key_provisions=key_provisions,
                disclaimer=self._load_disclaimer(law_id),
                sources=self._load_sources(law_id)
            )
            
            return detail
            
        except Exception as e:
            logger.error(f"Failed to create detailed regulation for {law_id}: {e}")
            return None
    
    def get_jurisdictions(self) -> List[str]:
        """Get list of available jurisdictions"""
        if self._mappings_cache and "jurisdiction_mapping" in self._mappings_cache:
            return list(self._mappings_cache["jurisdiction_mapping"].keys())
        return []
    
    def get_regulations_by_jurisdiction(self, jurisdiction: str) -> List[str]:
        """Get list of regulation IDs for a specific jurisdiction"""
        if not self._mappings_cache or "jurisdiction_mapping" not in self._mappings_cache:
            return []
        
        return self._mappings_cache["jurisdiction_mapping"].get(jurisdiction, [])
    
    def search_regulations(self, 
                          jurisdiction: Optional[str] = None,
                          regulation_type: Optional[str] = None,
                          contract_type: Optional[str] = None,
                          search_term: Optional[str] = None) -> List[RegulationSummary]:
        """Search regulations based on criteria"""
        all_regulations = self.get_all_regulations()
        
        filtered_regulations = []
        
        for regulation in all_regulations:
            # Filter by jurisdiction
            if jurisdiction and regulation.metadata.jurisdiction.upper() != jurisdiction.upper():
                continue
            
            # Filter by regulation type
            if regulation_type and regulation_type.lower() not in regulation.metadata.type.lower():
                continue
            
            # Filter by contract type
            if contract_type:
                contract_types_lower = [ct.lower() for ct in regulation.applicability.contract_types]
                if contract_type.lower() not in contract_types_lower:
                    continue
            
            # Filter by search term
            if search_term:
                search_term_lower = search_term.lower()
                searchable_text = f"{regulation.metadata.name} {regulation.metadata.type}".lower()
                if search_term_lower not in searchable_text:
                    continue
            
            filtered_regulations.append(regulation)
        
        return filtered_regulations
    
    def get_compliance_guidance(self, law_id: str) -> Optional[RegulationComplianceResponse]:
        """Get compliance guidance for a specific regulation"""
        regulation_detail = self.get_regulation_detail(law_id)
        if not regulation_detail:
            return None
        
        guidance_items = []
        total_requirements = 0
        high_risk_items = 0
        
        # Extract guidance from key provisions
        for provision_key, provision in regulation_detail.key_provisions.items():
            # Create guidance for each requirement
            for i, requirement in enumerate(provision.requirements):
                risk_level = self._assess_risk_level(provision_key, requirement)
                if risk_level == "high":
                    high_risk_items += 1
                
                guidance = ComplianceGuidance(
                    law_id=law_id,
                    provision_key=provision_key,
                    guidance_type="requirement",
                    title=f"{provision_key} - Requirement {i+1}",
                    description=requirement,
                    action_items=provision.compliance_checklist if provision.compliance_checklist else [],
                    risk_level=risk_level
                )
                guidance_items.append(guidance)
                total_requirements += 1
        
        return RegulationComplianceResponse(
            law_id=law_id,
            regulation_name=regulation_detail.metadata.name,
            guidance=guidance_items,
            total_requirements=total_requirements,
            high_risk_items=high_risk_items
        )
    
    def _assess_risk_level(self, provision_key: str, requirement: str) -> str:
        """Assess risk level based on provision and requirement content"""
        # Simple risk assessment based on keywords
        high_risk_keywords = [
            "transfer", "international", "penalty", "fine", "breach", "violation",
            "consent", "special category", "biometric", "genetic", "health"
        ]
        
        medium_risk_keywords = [
            "notification", "assessment", "documentation", "training", "policy"
        ]
        
        requirement_lower = requirement.lower()
        provision_lower = provision_key.lower()
        
        # Check for high-risk indicators
        for keyword in high_risk_keywords:
            if keyword in requirement_lower or keyword in provision_lower:
                return "high"
        
        # Check for medium-risk indicators
        for keyword in medium_risk_keywords:
            if keyword in requirement_lower or keyword in provision_lower:
                return "medium"
        
        return "low"
    
    def get_regulation_types(self) -> List[str]:
        """Get list of available regulation types"""
        all_regulations = self.get_all_regulations()
        types = set()
        
        for regulation in all_regulations:
            types.add(regulation.metadata.type)
        
        return sorted(list(types))
    
    def get_contract_types(self) -> List[str]:
        """Get list of available contract types across all regulations"""
        all_regulations = self.get_all_regulations()
        contract_types = set()
        
        for regulation in all_regulations:
            for contract_type in regulation.applicability.contract_types:
                contract_types.add(contract_type)
        
        return sorted(list(contract_types))

import json
import os
from typing import List, Optional, Dict, Any
from models.RegulationModel import Regulation, RegulationListResponse, RegulationDetailResponse

class RegulationService:
    """Simplified service for handling regulations data"""
    
    def __init__(self):
        self.data_dir = os.path.join(os.path.dirname(__file__), "..", "data")
        self.laws_dir = os.path.join(self.data_dir, "laws")
        self.disclaimer_dir = os.path.join(self.data_dir, "disclaimer")
        self.sources_dir = os.path.join(self.data_dir, "sources")
        self._regulations_cache = None
    
    def _load_regulations(self) -> Dict[str, Regulation]:
        """Load and cache all regulations from JSON files"""
        if self._regulations_cache is not None:
            return self._regulations_cache
        
        regulations = {}
        
        if not os.path.exists(self.laws_dir):
            return regulations
        
        for filename in os.listdir(self.laws_dir):
            if filename.endswith('.json'):
                law_id = filename.replace('.json', '')
                file_path = os.path.join(self.laws_dir, filename)
                
                try:
                    with open(file_path, 'r', encoding='utf-8') as file:
                        data = json.load(file)
                        
                        # Extract key provisions as simple strings
                        key_provisions = []
                        if 'key_provisions' in data:
                            for key, provision in data['key_provisions'].items():
                                if isinstance(provision, dict) and 'description' in provision:
                                    key_provisions.append(f"{key}: {provision['description']}")
                                else:
                                    key_provisions.append(str(provision))
                        
                        # Create simplified regulation object
                        regulation = Regulation(
                            law_id=law_id,
                            name=data.get('metadata', {}).get('name', law_id),
                            jurisdiction=data.get('metadata', {}).get('jurisdiction', 'Unknown'),
                            type=data.get('metadata', {}).get('type', 'General'),
                            description=data.get('metadata', {}).get('name', 'No description available'),
                            key_provisions=key_provisions
                        )
                        
                        regulations[law_id] = regulation
                        
                except Exception as e:
                    print(f"Error loading regulation {filename}: {str(e)}")
                    continue
        
        self._regulations_cache = regulations
        return regulations
    
    def get_all_regulations(self) -> RegulationListResponse:
        """Get all available regulations"""
        regulations = self._load_regulations()
        regulation_list = list(regulations.values())
        
        # Get unique jurisdictions
        jurisdictions = list(set(reg.jurisdiction for reg in regulation_list))
        
        return RegulationListResponse(
            regulations=regulation_list,
            total_count=len(regulation_list),
            jurisdictions=jurisdictions
        )
    
    def get_regulation_by_id(self, law_id: str) -> Optional[RegulationDetailResponse]:
        """Get detailed regulation information by ID"""
        regulations = self._load_regulations()
        
        if law_id not in regulations:
            return None
        
        regulation = regulations[law_id]
        
        # Load disclaimer and sources if available
        disclaimer = self._load_text_file(self.disclaimer_dir, f"{law_id}_notes.md")
        sources = self._load_text_file(self.sources_dir, f"{law_id}_sources.md")
        
        return RegulationDetailResponse(
            regulation=regulation,
            disclaimer=disclaimer,
            sources=sources
        )
    
    def search_regulations(self, jurisdiction: Optional[str] = None, 
                         regulation_type: Optional[str] = None,
                         search_term: Optional[str] = None) -> RegulationListResponse:
        """Search regulations with filters"""
        regulations = self._load_regulations()
        filtered_regulations = list(regulations.values())
        
        # Apply filters
        if jurisdiction:
            filtered_regulations = [r for r in filtered_regulations if r.jurisdiction.lower() == jurisdiction.lower()]
        
        if regulation_type:
            filtered_regulations = [r for r in filtered_regulations if regulation_type.lower() in r.type.lower()]
        
        if search_term:
            search_term = search_term.lower()
            filtered_regulations = [
                r for r in filtered_regulations 
                if (search_term in r.name.lower() or 
                    search_term in r.description.lower() or
                    any(search_term in provision.lower() for provision in r.key_provisions))
            ]
        
        # Get unique jurisdictions from filtered results
        jurisdictions = list(set(reg.jurisdiction for reg in filtered_regulations))
        
        return RegulationListResponse(
            regulations=filtered_regulations,
            total_count=len(filtered_regulations),
            jurisdictions=jurisdictions
        )
    
    def get_jurisdictions(self) -> List[str]:
        """Get list of available jurisdictions"""
        regulations = self._load_regulations()
        return list(set(reg.jurisdiction for reg in regulations.values()))
    
    def _load_text_file(self, directory: str, filename: str) -> Optional[str]:
        """Load text content from a file"""
        file_path = os.path.join(directory, filename)
        
        if not os.path.exists(file_path):
            return None
        
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                return file.read()
        except Exception as e:
            print(f"Error loading file {filename}: {str(e)}")
            return None

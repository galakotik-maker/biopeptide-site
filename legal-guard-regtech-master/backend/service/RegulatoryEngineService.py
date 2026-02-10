import json
import logging
from typing import Any, Dict, List, Optional

# Make sure the LawLoader class is importable from its location
from utils.law_loader import LawLoader

# Configure logging to see the output from the loader and the service
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class RegulatoryEngineService:
    def __init__(self, law_loader: LawLoader):
        if not isinstance(law_loader, LawLoader):
            raise TypeError("law_loader must be an instance of the LawLoader class.")
        
        self.law_loader = law_loader
        logger.info("RegulatoryEngineService initialized successfully.")

    def get_compliance_checklist(self, jurisdiction: str, contract_type: str) -> Dict[str, Any]:
        logger.debug(f"Service: Getting compliance checklist for J:{jurisdiction}, T:{contract_type}")
        return self.law_loader.get_compliance_checklist(jurisdiction, contract_type)

    def get_laws_for_jurisdiction(self, jurisdiction: str) -> Dict[str, Any]:
        logger.debug(f"Service: Getting all laws for jurisdiction '{jurisdiction}'.")
        return self.law_loader.get_laws_for_jurisdiction(jurisdiction)

    def get_law_details(self, law_code: str) -> Optional[Dict[str, Any]]:
        logger.debug(f"Service: Getting details for law_code '{law_code}'.")
        return self.law_loader.get_law_details(law_code)
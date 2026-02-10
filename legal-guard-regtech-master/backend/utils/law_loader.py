import json
import logging
from typing import Dict, List, Optional, Any
from pathlib import Path

logger = logging.getLogger(__name__)

class LawLoader:
    """
    Handles the loading and enrichment of legal data.
    1. Loads the base structure and mappings from a central `mappings.json`.
    2. Enriches the loaded laws with detailed data from individual JSON files
       in a specified directory.
    """
    def __init__(self, 
                 mappings_file: str = "data/general/mappings.json",
                 detailed_laws_dir: str = "data/laws"):
        
        self.mappings_file = Path(mappings_file)
        self.detailed_laws_dir = Path(detailed_laws_dir)
        
        # Initialize data stores
        self._law_cache: Dict[str, Dict[str, Any]] = {}
        self._jurisdiction_mapping: Dict[str, List[str]] = {}
        self._contract_types: Dict[str, Any] = {}
        self._risk_levels: Dict[str, Any] = {}
        self._metadata: Dict[str, Any] = {}
        
        # Perform the two-stage load
        self._initialize_from_mappings()
        self._enrich_with_detailed_laws()

    def _initialize_from_mappings(self):
        logger.info(f"Loading base mappings from {self.mappings_file}...")
        try:
            with open(self.mappings_file, 'r', encoding='utf-8') as f:
                mappings_data = json.load(f)
            
            # Load all sections from mappings.json
            self._jurisdiction_mapping = mappings_data.get("jurisdiction_mapping", {})
            self._law_cache = mappings_data.get("laws", {})
            self._contract_types = mappings_data.get("contract_types", {})
            self._risk_levels = mappings_data.get("risk_levels", {})
            self._metadata = mappings_data.get("metadata", {})
            logger.info(f"Loaded {len(self._law_cache)} base law definitions.")
        except FileNotFoundError:
            logger.error(f"FATAL: Mappings file not found at {self.mappings_file}. Cannot proceed.")
            raise
        except Exception as e:
            logger.error(f"FATAL: Failed to parse {self.mappings_file}: {e}")
            raise

    def _enrich_with_detailed_laws(self):
        logger.info(f"Enriching data with detailed laws from {self.detailed_laws_dir}...")
        if not self.detailed_laws_dir.is_dir():
            logger.warning(f"Detailed laws directory not found at {self.detailed_laws_dir}. Using base data only.")
            return

        enriched_count = 0
        for law_file_path in self.detailed_laws_dir.glob("*.json"):
            try:
                # The law_id is the filename (e.g., "GDPR_EU")
                law_id_from_filename = law_file_path.stem 
                
                with open(law_file_path, 'r', encoding='utf-8') as f:
                    detailed_data = json.load(f)
                
                # The key in the cache might be different (e.g., "GDPR" vs "GDPR_EU")
                # We find the correct key to update. For simplicity, we assume the file stem is the key.
                if law_id_from_filename in self._law_cache:
                    # Update the existing entry with the detailed data
                    self._law_cache[law_id_from_filename] = detailed_data
                    enriched_count += 1
                    logger.info(f"  -> Enriched '{law_id_from_filename}' with detailed data.")
                else:
                    # If it doesn't exist, add it.
                    self._law_cache[law_id_from_filename] = detailed_data
                    logger.info(f"  -> Loaded new detailed law '{law_id_from_filename}'.")

            except Exception as e:
                logger.error(f"Failed to load or enrich from {law_file_path.name}: {e}")
        logger.info(f"Enrichment complete. {enriched_count} laws were updated with detailed data.")


    # --- Public Accessor Methods ---
    # These methods remain largely the same, but now serve much richer data.

    def get_laws_for_jurisdiction(self, jurisdiction: str) -> Dict[str, Any]:
        """Get all applicable laws for a specific jurisdiction, including GLOBAL standards."""
        law_codes = self._jurisdiction_mapping.get(jurisdiction.upper(), [])
        global_codes = self._jurisdiction_mapping.get("GLOBAL", [])
        
        applicable_laws = {}
        for code in law_codes + global_codes:
            if code in self._law_cache:
                applicable_laws[code] = self._law_cache[code]
        return applicable_laws

    def get_compliance_checklist(self, jurisdiction: str, contract_type: str) -> Dict[str, Any]:
        """
        Builds a detailed compliance checklist for the AI, using the rich data.
        This is now the primary method for feeding context to the AI.
        """
        applicable_laws = self.get_laws_for_jurisdiction(jurisdiction)
        checklist = {}

        for law_id, law_data in applicable_laws.items():
            # Filter by contract type if applicable
            applicable_contracts = law_data.get("applicability", {}).get("contract_types", [])
            if contract_type in applicable_contracts or not applicable_contracts:
                # We only add the rich data needed for the AI prompt
                checklist[law_id] = {
                    "metadata": law_data.get("metadata"),
                    "key_provisions": law_data.get("key_provisions"),
                    "contract_specific_requirements": law_data.get("contract_specific_requirements")
                }
        return checklist

    def get_law_details(self, law_code: str) -> Optional[Dict[str, Any]]:
        return self._law_cache.get(law_code)
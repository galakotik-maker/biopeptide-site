"""
Legacy WatsonX client module - DEPRECATED

This module is deprecated in favor of the new modular ai_client package.
Use `from utils.ai_client import WatsonXClient, WatsonXConfig` instead.

This module is kept for backward compatibility during migration.
"""

import warnings
from typing import Dict, Any, Optional

# Import from the new modular structure
from .ai_client import WatsonXClient as NewWatsonXClient, WatsonXConfig as NewWatsonXConfig, ModelType

# Deprecated class - redirects to new implementation
class WatsonXClient:
    """
    DEPRECATED: Use backend.utils.ai_client.WatsonXClient instead.
    
    This class provides backward compatibility but will be removed in a future version.
    """
    
    def __init__(self, config: Optional[NewWatsonXConfig] = None):
        warnings.warn(
            "WatsonXClient from watsonx_client.py is deprecated. "
            "Use 'from utils.ai_client import WatsonXClient' instead.",
            DeprecationWarning,
            stacklevel=2
        )
        self._client = NewWatsonXClient(config)
    
    def analyze_contract(self, contract_text: str, compliance_checklist: Dict[str, Any]) -> str:
        """Analyze contract against compliance checklist - DEPRECATED"""
        return self._client.analyze_contract(contract_text, compliance_checklist)
    
    def extract_contract_metadata(self, contract_text: str) -> str:
        """Extract contract type and key metadata - DEPRECATED"""
        return self._client.extract_contract_metadata(contract_text)
    
    def generate_compliance_summary(self, analysis_results: Dict[str, Any]) -> str:
        """Generate executive summary of compliance analysis - DEPRECATED"""
        return self._client.generate_compliance_summary(analysis_results)


# Deprecated configuration class
class WatsonXConfig(NewWatsonXConfig):
    """
    DEPRECATED: Use backend.utils.ai_client.WatsonXConfig instead.
    """
    
    def __init__(self, *args, **kwargs):
        warnings.warn(
            "WatsonXConfig from watsonx_client.py is deprecated. "
            "Use 'from utils.ai_client import WatsonXConfig' instead.",
            DeprecationWarning,
            stacklevel=2
        )
        super().__init__(*args, **kwargs)


# Export the enum for backward compatibility
__all__ = ['WatsonXClient', 'WatsonXConfig', 'ModelType']
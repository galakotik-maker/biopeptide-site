"""
Configuration classes for AI client components.
"""
import os
from dataclasses import dataclass
from enum import Enum
from typing import Optional
from .exceptions import ConfigurationError


class ModelType(Enum):
    """Supported IBM Granite model types."""
    GRANITE_13B = "ibm/granite-13b-instruct-v2"
    GRANITE_20B = "ibm/granite-20b-instruct-v2"
    GRANITE_34B = "ibm/granite-34b-code-instruct"


@dataclass
class WatsonXConfig:
    """Configuration for WatsonX AI client."""
    api_key: str
    project_id: str
    base_url: str = "https://us-south.ml.cloud.ibm.com/ml/v1/text/generation?version=2023-05-29"
    model_id: str = ModelType.GRANITE_13B.value
    temperature: float = 0.1
    max_tokens: int = 8191  # Maximum allowed by IBM WatsonX
    top_p: float = 0.95
    timeout: int = 120  # Increased from 60 to 120 seconds for longer documents

    @classmethod
    def from_environment(cls) -> 'WatsonXConfig':
        """Create configuration from environment variables."""
        api_key = os.getenv("IBM_API_KEY")
        project_id = os.getenv("WATSONX_PROJECT_ID")
        
        if not api_key or not project_id:
            raise ConfigurationError("IBM_API_KEY and WATSONX_PROJECT_ID must be set")
        
        return cls(api_key=api_key, project_id=project_id)

    def validate(self) -> None:
        """Validate configuration parameters."""
        if not self.api_key:
            raise ConfigurationError("API key is required")
        if not self.project_id:
            raise ConfigurationError("Project ID is required")
        if not self.base_url:
            raise ConfigurationError("Base URL is required")
        if self.temperature < 0 or self.temperature > 1:
            raise ConfigurationError("Temperature must be between 0 and 1")
        if self.max_tokens <= 0:
            raise ConfigurationError("Max tokens must be positive")
        if self.top_p <= 0 or self.top_p > 1:
            raise ConfigurationError("Top-p must be between 0 and 1")

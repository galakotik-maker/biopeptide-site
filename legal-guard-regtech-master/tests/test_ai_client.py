"""
Tests for the refactored WatsonX AI client modules.
"""

import pytest
import os
from unittest.mock import Mock, patch, MagicMock
from backend.utils.ai_client import WatsonXClient, WatsonXConfig, ModelType
from backend.utils.ai_client.exceptions import ConfigurationError, AuthenticationError, APIError


class TestWatsonXConfig:
    """Test configuration handling"""
    
    def test_config_validation_success(self):
        """Test successful configuration validation"""
        config = WatsonXConfig(
            api_key="test_key",
            project_id="test_project"
        )
        config.validate()  # Should not raise
    
    def test_config_validation_missing_api_key(self):
        """Test configuration fails with missing API key"""
        with pytest.raises(ConfigurationError, match="API key is required"):
            config = WatsonXConfig(api_key="", project_id="test_project")
            config.validate()
    
    def test_config_validation_missing_project_id(self):
        """Test configuration fails with missing project ID"""
        with pytest.raises(ConfigurationError, match="Project ID is required"):
            config = WatsonXConfig(api_key="test_key", project_id="")
            config.validate()
    
    def test_config_validation_invalid_temperature(self):
        """Test configuration fails with invalid temperature"""
        with pytest.raises(ConfigurationError, match="Temperature must be between"):
            config = WatsonXConfig(
                api_key="test_key", 
                project_id="test_project",
                temperature=2.5
            )
            config.validate()
    
    @patch.dict(os.environ, {"IBM_API_KEY": "env_key", "WATSONX_PROJECT_ID": "env_project"})
    def test_config_from_environment(self):
        """Test loading configuration from environment variables"""
        config = WatsonXConfig.from_environment()
        assert config.api_key == "env_key"
        assert config.project_id == "env_project"
    
    @patch.dict(os.environ, {}, clear=True)
    def test_config_from_environment_missing_vars(self):
        """Test configuration fails when environment variables are missing"""
        with pytest.raises(ConfigurationError, match="IBM_API_KEY and WATSONX_PROJECT_ID must be set"):
            WatsonXConfig.from_environment()


class TestWatsonXClient:
    """Test WatsonX client functionality"""
    
    def setup_method(self):
        """Set up test configuration"""
        self.config = WatsonXConfig(
            api_key="test_key",
            project_id="test_project"
        )
    
    @patch('backend.utils.ai_client.auth.requests.post')
    def test_client_initialization(self, mock_post):
        """Test client initializes correctly"""
        client = WatsonXClient(self.config)
        assert client.config == self.config
        assert client.auth.api_key == "test_key"
    
    def test_client_initialization_without_config(self):
        """Test client initialization without config fails appropriately"""
        with patch.dict(os.environ, {}, clear=True):
            with pytest.raises(ConfigurationError):
                WatsonXClient()
    
    @patch('backend.utils.ai_client.auth.requests.post')
    @patch('backend.utils.ai_client.client.requests.post')
    def test_contract_analysis_success(self, mock_api_post, mock_auth_post):
        """Test successful contract analysis"""
        # Mock authentication
        mock_auth_post.return_value.json.return_value = {"access_token": "test_token"}
        mock_auth_post.return_value.raise_for_status.return_value = None
        
        # Mock API response
        mock_api_response = {
            "results": [{
                "generated_text": '{"summary": "Test analysis", "flagged_clauses": [], "compliance_issues": []}'
            }]
        }
        mock_api_post.return_value.json.return_value = mock_api_response
        mock_api_post.return_value.raise_for_status.return_value = None
        
        client = WatsonXClient(self.config)
        result = client.analyze_contract("Test contract", {"laws": []})
        
        assert "Test analysis" in result
        mock_api_post.assert_called_once()
    
    @patch('backend.utils.ai_client.auth.requests.post')
    def test_authentication_failure(self, mock_post):
        """Test authentication failure handling"""
        mock_post.side_effect = Exception("Auth failed")
        
        client = WatsonXClient(self.config)
        
        with pytest.raises(Exception):
            client.analyze_contract("Test contract", {"laws": []})
    
    @patch('backend.utils.ai_client.auth.requests.post')
    def test_health_check(self, mock_post):
        """Test health check functionality"""
        # Mock successful authentication
        mock_post.return_value.json.return_value = {"access_token": "test_token"}
        mock_post.return_value.raise_for_status.return_value = None
        
        client = WatsonXClient(self.config)
        
        with patch.object(client, '_make_request', return_value="healthy"):
            assert client.health_check() is True
        
        with patch.object(client, '_make_request', side_effect=Exception("Error")):
            assert client.health_check() is False


class TestModelType:
    """Test model type enum"""
    
    def test_model_type_values(self):
        """Test model type enum has expected values"""
        assert ModelType.GRANITE_13B.value == "ibm/granite-13b-instruct-v2"
        assert ModelType.GRANITE_20B.value == "ibm/granite-20b-instruct-v2"
        assert ModelType.GRANITE_34B.value == "ibm/granite-34b-code-instruct"


if __name__ == "__main__":
    pytest.main([__file__])

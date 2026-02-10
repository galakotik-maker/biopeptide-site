"""
Authentication handling for IBM Cloud WatsonX services.
"""

import requests
import logging
from typing import Optional
from .exceptions import AuthenticationError

logger = logging.getLogger(__name__)


class IBMCloudAuth:
    """Handles IBM Cloud IAM authentication for WatsonX services"""
    
    IAM_TOKEN_URL = "https://iam.cloud.ibm.com/identity/token"
    TOKEN_REQUEST_TIMEOUT = 30
    
    def __init__(self, api_key: str):
        """
        Initialize IBM Cloud authentication.
        
        Args:
            api_key: IBM Cloud API key
            
        Raises:
            AuthenticationError: If API key is not provided
        """
        if not api_key:
            raise AuthenticationError("IBM Cloud API key is required")
            
        self.api_key = api_key
        self._access_token: Optional[str] = None
    
    def get_access_token(self, force_refresh: bool = False) -> str:
        """
        Get a valid IBM Cloud IAM access token.
        
        Args:
            force_refresh: If True, forces token refresh even if cached token exists
            
        Returns:
            Valid access token string
            
        Raises:
            AuthenticationError: If token acquisition fails
        """
        if self._access_token and not force_refresh:
            return self._access_token
            
        return self._fetch_new_token()
    
    def _fetch_new_token(self) -> str:
        """
        Fetch a new access token from IBM Cloud IAM.
        
        Returns:
            New access token string
            
        Raises:
            AuthenticationError: If token fetch fails
        """
        headers = {
            "Content-Type": "application/x-www-form-urlencoded"
        }
        
        data = f"grant_type=urn:ibm:params:oauth:grant-type:apikey&apikey={self.api_key}"
        
        try:
            logger.debug("Requesting new IBM Cloud access token")
            response = requests.post(
                self.IAM_TOKEN_URL,
                headers=headers,
                data=data,
                timeout=self.TOKEN_REQUEST_TIMEOUT
            )
            response.raise_for_status()
            
            token_data = response.json()
            
            if "access_token" not in token_data:
                raise AuthenticationError("No access_token in response")
                
            self._access_token = token_data["access_token"]
            logger.info("Successfully obtained IBM Cloud access token")
            return self._access_token
            
        except requests.exceptions.Timeout:
            raise AuthenticationError("Token request timed out")
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to get IBM Cloud access token: {e}")
            raise AuthenticationError(f"Failed to authenticate with IBM Cloud: {e}")
        except (KeyError, ValueError) as e:
            raise AuthenticationError(f"Invalid token response format: {e}")
    
    def invalidate_token(self) -> None:
        """Invalidate the cached access token, forcing refresh on next request"""
        self._access_token = None
        logger.debug("Access token invalidated")

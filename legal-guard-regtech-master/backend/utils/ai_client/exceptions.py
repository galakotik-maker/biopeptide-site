"""
Custom exceptions for WatsonX AI client operations.
"""

class WatsonXError(Exception):
    """Base exception for WatsonX client errors"""
    pass


class AuthenticationError(WatsonXError):
    """Raised when authentication with IBM Cloud fails"""
    
    def __init__(self, message: str = "Failed to authenticate with IBM Cloud"):
        super().__init__(message)


class APIError(WatsonXError):
    """Raised when WatsonX API returns an error"""
    
    def __init__(self, message: str, status_code: int = None, response_data: dict = None):
        self.status_code = status_code
        self.response_data = response_data
        super().__init__(message)


class ConfigurationError(WatsonXError):
    """Raised when configuration is invalid or incomplete"""
    
    def __init__(self, message: str = "Invalid or incomplete configuration"):
        super().__init__(message)


class ResponseParsingError(WatsonXError):
    """Raised when unable to parse WatsonX response"""
    
    def __init__(self, message: str = "Failed to parse WatsonX response", response_text: str = None):
        self.response_text = response_text
        super().__init__(message)

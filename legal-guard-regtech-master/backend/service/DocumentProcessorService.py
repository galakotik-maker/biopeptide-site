import asyncio
import logging
from typing import List, Dict

from models.BulkAnalysisRequest import BulkAnalysisRequest
from models.ContractAnalysisModel import ContractAnalysisRequest
from models.ContractAnalysisResponseModel import ContractAnalysisResponse
from service.ContractAnalyzerService import ContractAnalyzerService

# Import our new helper modules
from utils.file_validators import FileValidator, TextSanitizer
from utils.text_extractors import TextExtractor, DocumentMetadataExtractor
from utils.process_managers import (
    BulkProcessManager, 
    JurisdictionValidator, 
    ProcessingLimiter
)

logger = logging.getLogger(__name__)


class DocumentProcessorService:
    """
    Enhanced service for processing and analyzing legal documents.
    
    This refactored version delegates responsibilities to specialized helper classes
    for better separation of concerns, maintainability, and testability.
    """
    
    def __init__(self):
        # Core analyzer
        self.contract_analyzer = ContractAnalyzerService()
        
        # Helper components for different responsibilities
        self.file_validator = FileValidator()
        self.text_sanitizer = TextSanitizer()
        self.text_extractor = TextExtractor()
        self.metadata_extractor = DocumentMetadataExtractor()
        self.bulk_processor = BulkProcessManager()
        self.jurisdiction_validator = JurisdictionValidator()
        self.processing_limiter = ProcessingLimiter()
    
    async def process_single_document(
        self, 
        file_content: bytes, 
        filename: str, 
        jurisdiction: str = "MY"
    ) -> ContractAnalysisResponse:
        """
        Process a single document with comprehensive validation and error handling.
        
        Args:
            file_content: The document content as bytes
            filename: The original filename
            jurisdiction: The legal jurisdiction for analysis
            
        Returns:
            ContractAnalysisResponse: Analysis results
            
        Raises:
            ValueError: For validation errors or processing failures
            TypeError: For incorrect input types
        """
        # Input validation
        if not file_content or not filename:
            raise ValueError("File content and filename are required")
        
        if not isinstance(file_content, bytes):
            raise TypeError("File content must be bytes")
        
        try:
            # Step 1: Validate file security and format
            self.file_validator.validate_file(file_content, filename)
            
            # Step 2: Extract text content
            extracted_text = await self.text_extractor.extract_text_async(file_content, filename)
            
            # Step 3: Clean and validate text
            cleaned_text = self.text_sanitizer.clean_and_validate_text(extracted_text)
            
            # Step 4: Apply processing limits
            self.processing_limiter.validate_processing_limits(
                len(file_content), 
                len(cleaned_text)
            )
            cleaned_text = self.processing_limiter.truncate_text_if_needed(cleaned_text)
            
            # Step 5: Validate jurisdiction
            validated_jurisdiction = self.jurisdiction_validator.validate_jurisdiction(jurisdiction)
            
            # Step 6: Create analysis request and process
            analysis_request = ContractAnalysisRequest(
                text=cleaned_text,
                jurisdiction=validated_jurisdiction
            )
            
            return await self.contract_analyzer.analyze_contract(analysis_request)
            
        except Exception as e:
            logger.error(f"Document processing failed for {filename}: {str(e)}")
            raise ValueError(f"Failed to process document {filename}: {str(e)}")
    
    async def process_bulk_documents(self, bulk_request: BulkAnalysisRequest) -> List[ContractAnalysisResponse]:
        """
        Process multiple documents with controlled concurrency and error handling.
        
        Args:
            bulk_request: Bulk analysis request containing multiple contracts
            
        Returns:
            List[ContractAnalysisResponse]: Analysis results for all processed documents
            
        Raises:
            ValueError: For invalid bulk requests or processing failures
        """
        return await self.bulk_processor.process_bulk_documents(bulk_request)
    
    async def extract_contract_metadata(self, file_content: bytes, filename: str) -> Dict:
        """
        Extract comprehensive metadata from contract with error handling.
        
        Args:
            file_content: The document content as bytes
            filename: The original filename
            
        Returns:
            Dict: Metadata dictionary with extracted information
        """
        if not file_content or not filename:
            return {
                'filename': filename, 
                'error': 'Invalid input parameters'
            }
        
        try:
            # Validate file first
            self.file_validator.validate_file(file_content, filename)
            
            # Extract text
            text = await self.text_extractor.extract_text(file_content, filename)
            
            # Clean text
            cleaned_text = self.text_sanitizer.clean_and_validate_text(text)
            
            # Extract metadata
            return await self.metadata_extractor.extract_metadata(
                cleaned_text, 
                filename, 
                len(file_content)
            )
            
        except Exception as e:
            logger.error(f"Metadata extraction failed for {filename}: {str(e)}")
            return {
                'filename': filename, 
                'error': f'Extraction failed: {str(e)}'
            }
    
    async def validate_document_format(self, file_content: bytes, filename: str) -> Dict:
        """
        Validate document format and basic requirements without full processing.
        
        Args:
            file_content: The document content as bytes
            filename: The original filename
            
        Returns:
            Dict: Validation results
        """
        try:
            self.file_validator.validate_file(file_content, filename)
            return {
                'valid': True,
                'filename': filename,
                'file_size': len(file_content),
                'message': 'Document format is valid'
            }
        except Exception as e:
            return {
                'valid': False,
                'filename': filename,
                'file_size': len(file_content),
                'error': str(e)
            }
    
    def get_supported_formats(self) -> List[str]:
        """Get list of supported file formats."""
        return self.file_validator.supported_formats.copy()
    
    def get_processing_limits(self) -> Dict:
        """Get current processing limits and constraints."""
        return {
            'max_file_size_mb': self.processing_limiter.max_file_size / (1024 * 1024),
            'max_text_length': self.processing_limiter.max_text_length,
            'min_text_length': self.processing_limiter.min_text_length,
            'max_bulk_size': self.processing_limiter.max_bulk_size,
            'max_concurrent_tasks': self.processing_limiter.max_concurrent_tasks,
            'supported_formats': self.get_supported_formats(),
            'valid_jurisdictions': self.jurisdiction_validator.get_valid_jurisdictions()
        }
    
    async def health_check(self) -> Dict:
        """Perform a health check of the service and its components."""
        try:
            # Test basic functionality
            test_text = "This is a test contract agreement between parties."
            
            # Test text sanitizer
            sanitized = self.text_sanitizer.clean_and_validate_text(test_text)
            
            # Test metadata extraction
            metadata = await self.metadata_extractor.extract_metadata(
                sanitized, 
                "test.txt", 
                len(test_text.encode())
            )
            
            return {
                'status': 'healthy',
                'components': {
                    'file_validator': 'operational',
                    'text_sanitizer': 'operational',
                    'text_extractor': 'operational',
                    'metadata_extractor': 'operational',
                    'bulk_processor': 'operational',
                    'contract_analyzer': 'operational'
                },
                'limits': self.get_processing_limits(),
                'test_results': {
                    'text_processing': len(sanitized) > 0,
                    'metadata_extraction': 'error' not in metadata
                }
            }
            
        except Exception as e:
            logger.error(f"Health check failed: {str(e)}")
            return {
                'status': 'unhealthy',
                'error': str(e),
                'limits': self.get_processing_limits()
            }

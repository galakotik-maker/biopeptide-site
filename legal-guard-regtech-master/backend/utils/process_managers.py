"""Process management utilities for bulk document operations."""

import asyncio
import logging
from typing import List, Optional

from models.BulkAnalysisRequest import BulkAnalysisRequest
from models.ContractAnalysisModel import ContractAnalysisRequest
from models.ContractAnalysisResponseModel import ContractAnalysisResponse
from service.ContractAnalyzerService import ContractAnalyzerService

logger = logging.getLogger(__name__)


class BulkProcessManager:
    """Manages bulk document processing with concurrency control."""
    
    def __init__(self, max_concurrent_tasks: int = 5, max_bulk_size: int = 100):
        self.max_concurrent_tasks = max_concurrent_tasks
        self.max_bulk_size = max_bulk_size
        self.contract_analyzer = ContractAnalyzerService()
    
    async def process_bulk_documents(self, bulk_request: BulkAnalysisRequest) -> List[ContractAnalysisResponse]:
        """Process multiple documents with controlled concurrency."""
        self._validate_bulk_request(bulk_request)
        
        try:
            if bulk_request.priority == "urgent":
                results = await self._process_concurrent(bulk_request.contracts)
            else:
                results = await self._process_sequential(bulk_request.contracts)
            
            # Send notification if email provided
            if bulk_request.notification_email:
                await self._send_completion_notification(
                    bulk_request.notification_email,
                    len(results),
                    len(bulk_request.contracts)
                )
            
            return results
            
        except Exception as e:
            logger.error(f"Bulk processing failed: {str(e)}")
            raise ValueError(f"Bulk processing failed: {str(e)}")
    
    def _validate_bulk_request(self, bulk_request: BulkAnalysisRequest) -> None:
        """Validate bulk request parameters."""
        if not bulk_request or not bulk_request.contracts:
            raise ValueError("Valid bulk request with contracts is required")
        
        if len(bulk_request.contracts) > self.max_bulk_size:
            raise ValueError(f"Too many contracts in bulk request (max: {self.max_bulk_size})")
        
        # Validate individual contracts
        for i, contract in enumerate(bulk_request.contracts):
            if not contract or not contract.text:
                raise ValueError(f"Contract {i + 1} is missing required text content")
    
    async def _process_concurrent(self, contracts: List[ContractAnalysisRequest]) -> List[ContractAnalysisResponse]:
        """Process contracts concurrently with limited parallelism."""
        semaphore = asyncio.Semaphore(self.max_concurrent_tasks)
        
        async def process_with_semaphore(contract_index: int, contract: ContractAnalysisRequest):
            async with semaphore:
                try:
                    logger.debug(f"Processing contract {contract_index + 1}/{len(contracts)}")
                    result = await self.contract_analyzer.analyze_contract(contract)
                    return result
                except Exception as e:
                    logger.error(f"Contract {contract_index + 1} analysis failed: {str(e)}")
                    return self._create_error_response(contract, str(e))
        
        tasks = [
            process_with_semaphore(i, contract) 
            for i, contract in enumerate(contracts)
        ]
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Filter out exceptions and return valid responses
        valid_results = []
        for result in results:
            if isinstance(result, ContractAnalysisResponse):
                valid_results.append(result)
            elif isinstance(result, Exception):
                logger.error(f"Contract processing exception: {result}")
                # Could create an error response here if needed
        
        return valid_results
    
    async def _process_sequential(self, contracts: List[ContractAnalysisRequest]) -> List[ContractAnalysisResponse]:
        """Process contracts sequentially for better resource management."""
        results = []
        
        for i, contract in enumerate(contracts):
            try:
                logger.debug(f"Processing contract {i + 1}/{len(contracts)} sequentially")
                result = await self.contract_analyzer.analyze_contract(contract)
                results.append(result)
            except Exception as e:
                logger.error(f"Contract {i + 1} analysis failed: {str(e)}")
                # Add error response to maintain order
                error_response = self._create_error_response(contract, str(e))
                results.append(error_response)
        
        return results
    
    def _create_error_response(self, contract: ContractAnalysisRequest, error_message: str) -> ContractAnalysisResponse:
        """Create an error response for failed contract analysis."""
        # This is a placeholder - adjust based on your ContractAnalysisResponse structure
        try:
            return ContractAnalysisResponse(
                analysis_id=f"error_{hash(contract.text) % 10000}",
                jurisdiction=contract.jurisdiction or "UNKNOWN",
                contract_type="error",
                risk_score=0.0,
                compliance_status="error",
                analysis_summary=f"Analysis failed: {error_message}",
                recommendations=[f"Error processing contract: {error_message}"],
                identified_clauses=[],
                missing_clauses=[],
                regulatory_alerts=[]
            )
        except Exception as e:
            logger.error(f"Failed to create error response: {e}")
            # Return a minimal error response
            return None
    
    async def _send_completion_notification(self, email: str, processed_count: int, total_count: int) -> None:
        """Send notification about bulk processing completion."""
        if not self._is_valid_email(email):
            logger.warning(f"Invalid email address for notification: {email}")
            return
        
        success_rate = (processed_count / total_count * 100) if total_count > 0 else 0
        
        logger.info(
            f"Bulk processing completed: {processed_count}/{total_count} contracts "
            f"({success_rate:.1f}% success rate)"
        )
        logger.info(f"Notification should be sent to: {email}")
        
        # TODO: Implement actual email service integration
        # Consider using services like SendGrid, AWS SES, or similar
        await self._mock_send_email(email, processed_count, total_count, success_rate)
    
    def _is_valid_email(self, email: str) -> bool:
        """Basic email validation."""
        if not email or '@' not in email:
            return False
        
        # Basic regex for email validation
        import re
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(email_pattern, email) is not None
    
    async def _mock_send_email(self, email: str, processed: int, total: int, success_rate: float) -> None:
        """Mock email sending - replace with actual implementation."""
        # This is where you would integrate with an actual email service
        message = (
            f"Bulk document processing completed!\n\n"
            f"Processed: {processed}/{total} documents\n"
            f"Success rate: {success_rate:.1f}%\n\n"
            f"Thank you for using our document analysis service."
        )
        
        logger.info(f"Email notification sent to {email}: {message}")


class JurisdictionValidator:
    """Validates and normalizes jurisdiction codes."""
    
    def __init__(self):
        self.valid_jurisdictions = {'MY', 'SG', 'EU', 'US', 'UK', 'GLOBAL'}
        self.default_jurisdiction = "MY"
    
    def validate_jurisdiction(self, jurisdiction: str) -> str:
        """Validate and normalize jurisdiction code."""
        if not jurisdiction or not isinstance(jurisdiction, str):
            logger.info(f"No jurisdiction provided, defaulting to {self.default_jurisdiction}")
            return self.default_jurisdiction
        
        jurisdiction = jurisdiction.upper().strip()
        
        if jurisdiction not in self.valid_jurisdictions:
            logger.warning(
                f"Invalid jurisdiction '{jurisdiction}', defaulting to {self.default_jurisdiction}. "
                f"Valid options: {', '.join(self.valid_jurisdictions)}"
            )
            return self.default_jurisdiction
        
        return jurisdiction
    
    def get_valid_jurisdictions(self) -> List[str]:
        """Get list of valid jurisdiction codes."""
        return list(self.valid_jurisdictions)


class ProcessingLimiter:
    """Manages processing limits and resource constraints."""
    
    def __init__(self):
        self.max_file_size = 10 * 1024 * 1024  # 10MB
        self.max_text_length = 1_000_000  # 1MB text
        self.min_text_length = 50
        self.max_bulk_size = 100
        self.max_concurrent_tasks = 5
    
    def validate_processing_limits(self, file_size: int, text_length: int) -> None:
        """Validate file and text size limits."""
        if file_size > self.max_file_size:
            raise ValueError(f"File exceeds {self.max_file_size / (1024*1024):.1f}MB limit")
        
        if text_length < self.min_text_length:
            raise ValueError(f"Text too short (min: {self.min_text_length} chars)")
        
        if text_length > self.max_text_length:
            logger.warning(f"Text length {text_length} exceeds limit, will be truncated")
    
    def truncate_text_if_needed(self, text: str) -> str:
        """Truncate text if it exceeds maximum length."""
        if len(text) > self.max_text_length:
            logger.warning(f"Truncating text from {len(text)} to {self.max_text_length} characters")
            return text[:self.max_text_length]
        return text

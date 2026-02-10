"""File validation utilities for document processing."""

import logging
import re
from pathlib import Path
from typing import Dict, Any

logger = logging.getLogger(__name__)


class FileValidator:
    """Handles file validation with security checks."""
    
    def __init__(self, max_file_size: int = 10 * 1024 * 1024):
        self.max_file_size = max_file_size
        self.supported_formats = ['.pdf', '.docx', '.txt']
    
    def validate_file(self, file_content: bytes, filename: str) -> None:
        """Comprehensive file validation with security checks."""
        self._validate_basic_requirements(file_content, filename)
        self._validate_filename_security(filename)
        self._validate_file_size(file_content)
        self._validate_file_format(filename)
        self._validate_file_content(file_content, filename)
    
    def _validate_basic_requirements(self, file_content: bytes, filename: str) -> None:
        """Basic input validation."""
        if not file_content:
            raise ValueError("File content is empty")
        
        if not filename or not filename.strip():
            raise ValueError("Filename is required")
        
        if not isinstance(file_content, bytes):
            raise TypeError("File content must be bytes")
    
    def _validate_filename_security(self, filename: str) -> None:
        """Security validation for filename."""
        safe_filename = Path(filename).name
        if safe_filename != filename:
            logger.warning(f"Potential path traversal attempt: {filename}")
            raise ValueError("Invalid filename - potential security risk")
        
        # Check for suspicious characters
        if re.search(r'[<>:"|?*\x00-\x1f]', filename):
            raise ValueError("Filename contains invalid characters")
    
    def _validate_file_size(self, file_content: bytes) -> None:
        """File size validation."""
        if len(file_content) > self.max_file_size:
            raise ValueError(f"File exceeds {self.max_file_size / (1024*1024):.1f}MB limit")
        
        if len(file_content) < 100:  # Very small files are suspicious
            raise ValueError("File too small to contain meaningful content")
    
    def _validate_file_format(self, filename: str) -> None:
        """File extension validation."""
        file_ext = Path(filename).suffix.lower()
        if file_ext not in self.supported_formats:
            raise ValueError(f"Unsupported format. Supported: {', '.join(self.supported_formats)}")
    
    def _validate_file_content(self, file_content: bytes, filename: str) -> None:
        """Validate file content matches expected format."""
        file_ext = Path(filename).suffix.lower()
        
        try:
            if file_ext == '.pdf':
                self._validate_pdf_content(file_content)
            elif file_ext == '.txt':
                self._validate_text_content(file_content)
            elif file_ext == '.docx':
                self._validate_docx_content(file_content)
        except Exception as e:
            raise ValueError(f"File content validation failed: {str(e)}")
    
    def _validate_pdf_content(self, content: bytes) -> None:
        """Validate PDF file content."""
        if not content.startswith(b'%PDF'):
            raise ValueError("Invalid PDF file format")
        
        # Check for PDF version
        if not re.match(rb'%PDF-\d\.\d', content[:10]):
            raise ValueError("Unsupported PDF version")
    
    def _validate_text_content(self, content: bytes) -> None:
        """Validate text file content."""
        encodings = ['utf-8', 'utf-16', 'latin-1', 'cp1252']
        
        for encoding in encodings:
            try:
                content.decode(encoding)
                return  # Successfully decoded
            except UnicodeDecodeError:
                continue
        
        raise ValueError("Text file encoding not supported")
    
    def _validate_docx_content(self, content: bytes) -> None:
        """Validate DOCX file content."""
        if not content.startswith(b'PK'):
            raise ValueError("Invalid DOCX file format")
        
        # Basic ZIP header validation for DOCX
        if len(content) < 30:  # Minimum ZIP header size
            raise ValueError("DOCX file appears corrupted")


class TextSanitizer:
    """Handles text cleaning and sanitization."""
    
    def __init__(self, min_length: int = 50, max_length: int = 1_000_000):
        self.min_length = min_length
        self.max_length = max_length
    
    def clean_and_validate_text(self, text: str) -> str:
        """Clean and validate extracted text."""
        if not text or not isinstance(text, str):
            raise ValueError("Invalid text input")
        
        # Clean the text
        cleaned = self._normalize_whitespace(text)
        cleaned = self._remove_page_artifacts(cleaned)
        cleaned = self._sanitize_content(cleaned)
        
        # Validate length
        self._validate_text_length(cleaned)
        
        return cleaned.strip()
    
    def _normalize_whitespace(self, text: str) -> str:
        """Normalize whitespace while preserving document structure for legal analysis."""
        # Remove excessive spaces within lines, but preserve line breaks
        lines = text.split('\n')
        normalized_lines = []
        
        for line in lines:
            # Normalize spaces within each line
            normalized_line = re.sub(r'[ \t]+', ' ', line.strip())
            normalized_lines.append(normalized_line)
        
        # Join lines back with single line breaks
        text = '\n'.join(normalized_lines)
        
        # Fix hyphenated line breaks (but preserve intentional line breaks)
        text = re.sub(r'-\n(?=[a-z])', '', text)
        
        # Normalize excessive line breaks (3+ become 2) but preserve structure
        text = re.sub(r'\n{3,}', '\n\n', text)
        
        # Remove leading/trailing whitespace
        return text.strip()
    
    def _remove_page_artifacts(self, text: str) -> str:
        """Remove common page artifacts."""
        # Remove page numbers
        text = re.sub(r'\n\s*\d+\s*\n', '\n', text)
        text = re.sub(r'\n\s*Page \d+ of \d+\s*\n', '\n', text, flags=re.IGNORECASE)
        
        # Remove headers/footers patterns
        text = re.sub(r'\n\s*-+\s*\n', '\n', text)
        
        return text
    
    def _sanitize_content(self, text: str) -> str:
        """Remove potentially harmful content."""
        # Remove control characters except common whitespace
        text = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]', '', text)
        
        # Prevent potential DoS with excessive repeated characters
        text = re.sub(r'(.)\1{100,}', r'\1' * 10, text)
        
        return text
    
    def _validate_text_length(self, text: str) -> None:
        """Validate text meets length requirements."""
        if len(text) < self.min_length:
            raise ValueError(f"Text too short (min: {self.min_length} chars)")
        
        if len(text) > self.max_length:
            logger.warning(f"Text truncated to {self.max_length} characters")
            # Note: We don't truncate here, caller should handle this

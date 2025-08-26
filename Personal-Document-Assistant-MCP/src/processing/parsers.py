"""
Document parsers for various file formats.
"""

import os
import logging
from typing import Dict, List, Optional
from pathlib import Path
import tempfile
import mimetypes

logger = logging.getLogger(__name__)

class DocumentParser:
    """Base class for document parsers."""
    
    def can_parse(self, file_path: str, mime_type: str) -> bool:
        """Check if this parser can handle the given file."""
        raise NotImplementedError
    
    def parse(self, file_path: str) -> Dict[str, any]:
        """Parse document and return content with metadata."""
        raise NotImplementedError

class TextParser(DocumentParser):
    """Parser for plain text files."""
    
    def can_parse(self, file_path: str, mime_type: str) -> bool:
        return mime_type.startswith('text/') or file_path.endswith('.txt')
    
    def parse(self, file_path: str) -> Dict[str, any]:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            return {
                'content': content,
                'metadata': {
                    'parser': 'text',
                    'file_size': os.path.getsize(file_path),
                    'char_count': len(content),
                    'line_count': content.count('\n') + 1
                }
            }
        except Exception as e:
            logger.error(f"Error parsing text file {file_path}: {e}")
            return {'content': '', 'metadata': {'error': str(e)}}

class HTMLParser(DocumentParser):
    """Parser for HTML files."""
    
    def can_parse(self, file_path: str, mime_type: str) -> bool:
        return mime_type in ['text/html', 'application/xhtml+xml'] or file_path.endswith('.html')
    
    def parse(self, file_path: str) -> Dict[str, any]:
        try:
            # For now, simple HTML parsing
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Basic HTML tag removal
            import re
            text_content = re.sub(r'<[^>]+>', '', content)
            text_content = re.sub(r'\s+', ' ', text_content).strip()
            
            return {
                'content': text_content,
                'metadata': {
                    'parser': 'html',
                    'file_size': os.path.getsize(file_path),
                    'char_count': len(text_content),
                    'original_html_size': len(content)
                }
            }
        except Exception as e:
            logger.error(f"Error parsing HTML file {file_path}: {e}")
            return {'content': '', 'metadata': {'error': str(e)}}

class PDFParser(DocumentParser):
    """Parser for PDF files."""
    
    def can_parse(self, file_path: str, mime_type: str) -> bool:
        return mime_type == 'application/pdf' or file_path.endswith('.pdf')
    
    def parse(self, file_path: str) -> Dict[str, any]:
        try:
            # Simple PDF parsing without external dependencies
            # In production, you'd use PyPDF2 or similar
            return {
                'content': f"PDF content from {os.path.basename(file_path)} (parser simulation)",
                'metadata': {
                    'parser': 'pdf',
                    'file_size': os.path.getsize(file_path),
                    'note': 'Full PDF parsing requires PyPDF2 or similar library'
                }
            }
        except Exception as e:
            logger.error(f"Error parsing PDF file {file_path}: {e}")
            return {'content': '', 'metadata': {'error': str(e)}}

class DOCXParser(DocumentParser):
    """Parser for DOCX files."""
    
    def can_parse(self, file_path: str, mime_type: str) -> bool:
        return (mime_type == 'application/vnd.openxmlformats-officedocument.wordprocessingml.document' 
                or file_path.endswith('.docx'))
    
    def parse(self, file_path: str) -> Dict[str, any]:
        try:
            # Simple DOCX parsing without external dependencies
            # In production, you'd use python-docx
            return {
                'content': f"DOCX content from {os.path.basename(file_path)} (parser simulation)",
                'metadata': {
                    'parser': 'docx',
                    'file_size': os.path.getsize(file_path),
                    'note': 'Full DOCX parsing requires python-docx library'
                }
            }
        except Exception as e:
            logger.error(f"Error parsing DOCX file {file_path}: {e}")
            return {'content': '', 'metadata': {'error': str(e)}}

class DocumentParserFactory:
    """Factory for creating appropriate document parsers."""
    
    def __init__(self):
        self.parsers = [
            TextParser(),
            HTMLParser(),
            PDFParser(),
            DOCXParser()
        ]
    
    def get_parser(self, file_path: str) -> Optional[DocumentParser]:
        """Get appropriate parser for the file."""
        mime_type, _ = mimetypes.guess_type(file_path)
        if not mime_type:
            mime_type = 'application/octet-stream'
        
        for parser in self.parsers:
            if parser.can_parse(file_path, mime_type):
                return parser
        
        return None
    
    def parse_document(self, file_path: str) -> Dict[str, any]:
        """Parse document using appropriate parser."""
        parser = self.get_parser(file_path)
        if not parser:
            return {
                'content': '',
                'metadata': {'error': f'No parser available for {file_path}'}
            }
        
        return parser.parse(file_path)

# Global factory instance
parser_factory = DocumentParserFactory()

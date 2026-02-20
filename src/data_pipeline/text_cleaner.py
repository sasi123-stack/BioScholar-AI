"""Text cleaning and normalization utilities."""

import re
from typing import Optional

from bs4 import BeautifulSoup


class TextCleaner:
    """Cleans and normalizes biomedical text."""
    
    @staticmethod
    def remove_html(text: str) -> str:
        """Remove HTML tags from text.
        
        Args:
            text: Text potentially containing HTML
            
        Returns:
            Text with HTML removed
        """
        if not text:
            return ""
        
        soup = BeautifulSoup(text, "html.parser")
        return soup.get_text()
    
    @staticmethod
    def normalize_whitespace(text: str) -> str:
        """Normalize whitespace in text.
        
        Args:
            text: Text with irregular whitespace
            
        Returns:
            Text with normalized whitespace
        """
        if not text:
            return ""
        
        # Replace multiple whitespaces with single space
        text = re.sub(r'\s+', ' ', text)
        
        # Remove leading/trailing whitespace
        text = text.strip()
        
        return text
    
    @staticmethod
    def remove_special_chars(text: str, keep_punctuation: bool = True) -> str:
        """Remove special characters from text.
        
        Args:
            text: Text containing special characters
            keep_punctuation: Whether to keep basic punctuation
            
        Returns:
            Cleaned text
        """
        if not text:
            return ""
        
        if keep_punctuation:
            # Keep letters, numbers, spaces, and basic punctuation
            text = re.sub(r'[^\w\s.,;:!?()\-\'\"]+', ' ', text)
        else:
            # Keep only letters, numbers, and spaces
            text = re.sub(r'[^\w\s]+', ' ', text)
        
        return text
    
    @staticmethod
    def normalize_unicode(text: str) -> str:
        """Normalize Unicode characters.
        
        Args:
            text: Text with Unicode characters
            
        Returns:
            Normalized text
        """
        if not text:
            return ""
        
        # Common replacements
        replacements = {
            '\u2018': "'",  # Left single quote
            '\u2019': "'",  # Right single quote
            '\u201c': '"',  # Left double quote
            '\u201d': '"',  # Right double quote
            '\u2013': '-',  # En dash
            '\u2014': '-',  # Em dash
            '\u2026': '...',  # Ellipsis
            '\xa0': ' ',  # Non-breaking space
        }
        
        for old, new in replacements.items():
            text = text.replace(old, new)
        
        return text
    
    @staticmethod
    def fix_encoding_issues(text: str) -> str:
        """Fix common encoding issues.
        
        Args:
            text: Text with encoding issues
            
        Returns:
            Fixed text
        """
        if not text:
            return ""
        
        # Fix common encoding issues
        text = text.encode('utf-8', errors='ignore').decode('utf-8')
        
        return text
    
    @classmethod
    def clean(
        cls,
        text: Optional[str],
        remove_html_tags: bool = True,
        normalize_ws: bool = True,
        remove_special: bool = False,
        normalize_uni: bool = True,
        fix_encoding: bool = True
    ) -> str:
        """Comprehensive text cleaning pipeline.
        
        Args:
            text: Text to clean
            remove_html_tags: Remove HTML tags
            normalize_ws: Normalize whitespace
            remove_special: Remove special characters
            normalize_uni: Normalize Unicode
            fix_encoding: Fix encoding issues
            
        Returns:
            Cleaned text
        """
        if not text:
            return ""
        
        if fix_encoding:
            text = cls.fix_encoding_issues(text)
        
        if remove_html_tags:
            text = cls.remove_html(text)
        
        if normalize_uni:
            text = cls.normalize_unicode(text)
        
        if remove_special:
            text = cls.remove_special_chars(text)
        
        if normalize_ws:
            text = cls.normalize_whitespace(text)
        
        return text

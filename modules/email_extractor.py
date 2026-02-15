"""
Email Extractor module
Extracts email addresses from web pages
"""
import re
from typing import List, Set
from bs4 import BeautifulSoup
from modules.logger import get_logger
from modules.browser_manager import BrowserManager
from config import EMAIL_PATTERN

logger = get_logger(__name__)

class EmailExtractor:
    """Extracts email addresses from web pages"""
    
    def __init__(self, browser_manager: BrowserManager):
        """
        Initialize email extractor
        
        Args:
            browser_manager: BrowserManager instance
        """
        self.browser = browser_manager
        self.email_pattern = re.compile(EMAIL_PATTERN)
    
    async def extract_emails(self, url: str = None) -> List[str]:
        """
        Extract all email addresses from current page or specified URL
        
        Args:
            url: Optional URL to navigate to first
            
        Returns:
            List of unique email addresses
        """
        try:
            if url:
                logger.info(f"[EMAIL] Extracting emails from {url}")
                success = await self.browser.navigate(url)
                if not success:
                    logger.warning("Failed to load page for email extraction")
                    return []
            else:
                logger.info("[EMAIL] Extracting emails from current page")
            
            # Get page content
            content = await self.browser.get_page_content()
            
            # Extract emails from HTML
            emails = self._extract_from_html(content)
            
            # Also check for contact page
            contact_emails = await self._check_contact_page()
            emails.update(contact_emails)
            
            # Filter out common non-HR emails
            filtered_emails = self._filter_emails(emails)
            
            logger.success(f"Found {len(filtered_emails)} email(s)")
            
            return list(filtered_emails)
            
        except Exception as e:
            logger.error(f"Error extracting emails: {str(e)}")
            return []
    
    def _extract_from_html(self, html_content: str) -> Set[str]:
        """
        Extract emails from HTML content
        
        Args:
            html_content: HTML content
            
        Returns:
            Set of email addresses
        """
        emails = set()
        
        # Parse HTML
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Method 1: Find mailto links
        mailto_links = soup.find_all('a', href=re.compile(r'^mailto:', re.I))
        for link in mailto_links:
            href = link.get('href', '')
            email = href.replace('mailto:', '').split('?')[0].strip()
            if self._is_valid_email(email):
                emails.add(email.lower())
        
        # Method 2: Regex search in text
        text_content = soup.get_text()
        found_emails = self.email_pattern.findall(text_content)
        for email in found_emails:
            if self._is_valid_email(email):
                emails.add(email.lower())
        
        # Method 3: Search in HTML source (for obfuscated emails)
        source_emails = self.email_pattern.findall(html_content)
        for email in source_emails:
            if self._is_valid_email(email):
                emails.add(email.lower())
        
        return emails
    
    async def _check_contact_page(self) -> Set[str]:
        """
        Try to find and extract emails from contact page
        
        Returns:
            Set of email addresses
        """
        emails = set()
        
        try:
            # Get all links
            links = await self.browser.get_all_links()
            
            # Look for contact page
            contact_keywords = ['contact', 'about', 'team', 'support']
            
            for link in links:
                href = link.get('href', '').lower()
                text = link.get('text', '').lower()
                
                # Check if it's a contact-related link
                if any(keyword in href or keyword in text for keyword in contact_keywords):
                    if href.startswith('http'):
                        logger.debug(f"Checking contact page: {href}")
                        
                        # Navigate to contact page
                        success = await self.browser.navigate(href)
                        if success:
                            content = await self.browser.get_page_content()
                            page_emails = self._extract_from_html(content)
                            emails.update(page_emails)
                        
                        # Return to previous page
                        await self.browser.page.go_back()
                        break  # Only check first contact page found
            
        except Exception as e:
            logger.debug(f"Error checking contact page: {str(e)}")
        
        return emails
    
    def _is_valid_email(self, email: str) -> bool:
        """
        Validate email address
        
        Args:
            email: Email address to validate
            
        Returns:
            True if valid
        """
        if not email or len(email) < 5:
            return False
        
        # Check format
        if not re.match(EMAIL_PATTERN, email):
            return False
        
        # Exclude common false positives
        invalid_patterns = [
            r'\.png$', r'\.jpg$', r'\.gif$', r'\.svg$',  # Image files
            r'example\.com', r'test\.com', r'sample\.com',  # Example domains
            r'@2x\.', r'@3x\.',  # Retina image naming
        ]
        
        for pattern in invalid_patterns:
            if re.search(pattern, email, re.I):
                return False
        
        return True
    
    def _filter_emails(self, emails: Set[str]) -> Set[str]:
        """
        Filter out non-HR/recruitment emails
        
        Args:
            emails: Set of email addresses
            
        Returns:
            Filtered set of emails
        """
        filtered = set()
        
        # Preferred email prefixes (HR/recruitment related)
        preferred_prefixes = [
            'hr', 'careers', 'jobs', 'recruitment', 'talent',
            'hiring', 'recruit', 'people', 'join'
        ]
        
        # Unwanted email prefixes
        unwanted_prefixes = [
            'noreply', 'no-reply', 'donotreply', 'support',
            'info', 'sales', 'marketing', 'press'
        ]
        
        for email in emails:
            email_lower = email.lower()
            
            # Skip unwanted emails
            if any(prefix in email_lower for prefix in unwanted_prefixes):
                continue
            
            # Prioritize HR-related emails
            if any(prefix in email_lower for prefix in preferred_prefixes):
                filtered.add(email)
            else:
                # Include other emails but with lower priority
                filtered.add(email)
        
        return filtered
    
    async def extract_from_job_description(self, job_description: str) -> List[str]:
        """
        Extract emails directly from job description text
        
        Args:
            job_description: Job description text
            
        Returns:
            List of email addresses
        """
        emails = set()
        
        found_emails = self.email_pattern.findall(job_description)
        
        for email in found_emails:
            if self._is_valid_email(email):
                emails.add(email.lower())
        
        return list(emails)

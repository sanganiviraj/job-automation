"""
Career Finder module
Detects and navigates to career/jobs pages on company websites
"""
import re
from typing import Optional, List, Tuple
from bs4 import BeautifulSoup
from modules.logger import get_logger
from modules.browser_manager import BrowserManager
from config import CAREER_KEYWORDS
import urllib.parse

logger = get_logger(__name__)

class CareerFinder:
    """Finds career pages on company websites"""
    
    def __init__(self, browser_manager: BrowserManager):
        """
        Initialize career finder
        
        Args:
            browser_manager: BrowserManager instance
        """
        self.browser = browser_manager
    
    async def find_career_page(self, company_url: str) -> Optional[str]:
        """
        Find career page URL for a company
        
        Args:
            company_url: Company homepage URL
            
        Returns:
            Career page URL or None
        """
        try:
            logger.info(f"[SEARCH] Searching for career page on {company_url}")
            
            # Navigate to homepage
            success = await self.browser.navigate(company_url)
            if not success:
                logger.warning("Failed to load homepage")
                return None
            
            # Method 1: Look for career links on homepage
            career_url = await self._find_career_link_on_page()
            if career_url:
                logger.success(f"Found career page: {career_url}")
                return career_url
            
            # Method 2: Try common career page URLs
            career_url = await self._try_common_career_urls(company_url)
            if career_url:
                logger.success(f"Found career page via common URL: {career_url}")
                return career_url
            
            # Method 3: Google search
            career_url = await self._google_search_career_page(company_url)
            if career_url:
                logger.success(f"Found career page via Google: {career_url}")
                return career_url
            
            logger.warning(f"[X] No career page found for {company_url}")
            return None
            
        except Exception as e:
            logger.error(f"Error finding career page: {str(e)}")
            return None
    
    async def _find_career_link_on_page(self) -> Optional[str]:
        """
        Search for career links on current page
        
        Returns:
            Career page URL or None
        """
        try:
            # Get all links
            links = await self.browser.get_all_links()
            
            # Search for career-related links
            for link in links:
                href = link.get('href', '').lower()
                text = link.get('text', '').lower()
                
                # Check if link text or href contains career keywords
                for keyword in CAREER_KEYWORDS:
                    if keyword in text or keyword in href:
                        # Validate it's a proper URL
                        if href.startswith('http'):
                            logger.debug(f"Found career link: {href} (text: {text})")
                            return href
            
            return None
            
        except Exception as e:
            logger.error(f"Error searching for career links: {str(e)}")
            return None
    
    async def _try_common_career_urls(self, base_url: str) -> Optional[str]:
        """
        Try common career page URL patterns
        
        Args:
            base_url: Company base URL
            
        Returns:
            Valid career page URL or None
        """
        # Parse base URL
        parsed = urllib.parse.urlparse(base_url)
        base_domain = f"{parsed.scheme}://{parsed.netloc}"
        
        # Common career page patterns
        common_paths = [
            '/careers',
            '/jobs',
            '/career',
            '/join-us',
            '/work-with-us',
            '/opportunities',
            '/hiring',
            '/careers/',
            '/jobs/',
            '/about/careers',
            '/company/careers',
            '/en/careers',
        ]
        
        for path in common_paths:
            test_url = base_domain + path
            
            try:
                # Try to navigate
                success = await self.browser.navigate(test_url)
                
                if success:
                    # Check if page actually loaded (not 404)
                    page_content = await self.browser.get_page_content()
                    
                    # Simple check: if page contains career keywords, it's likely valid
                    if self._contains_career_keywords(page_content):
                        logger.debug(f"Valid career page found: {test_url}")
                        return test_url
                        
            except Exception as e:
                logger.debug(f"URL {test_url} not accessible: {str(e)}")
                continue
        
        return None
    
    async def _google_search_career_page(self, company_url: str) -> Optional[str]:
        """
        Use Google search to find career page
        
        Args:
            company_url: Company URL
            
        Returns:
            Career page URL or None
        """
        try:
            # Extract domain from URL
            parsed = urllib.parse.urlparse(company_url)
            domain = parsed.netloc.replace('www.', '')
            
            # Construct Google search query
            search_query = f"site:{domain} careers OR jobs"
            google_url = f"https://www.google.com/search?q={urllib.parse.quote(search_query)}"
            
            logger.debug(f"Searching Google: {search_query}")
            
            # Navigate to Google search
            success = await self.browser.navigate(google_url)
            if not success:
                return None
            
            # Wait for results
            await self.browser.human_delay(2, 3)
            
            # Get search results
            content = await self.browser.get_page_content()
            soup = BeautifulSoup(content, 'html.parser')
            
            # Find first result link
            for link in soup.find_all('a'):
                href = link.get('href', '')
                
                # Google result links start with /url?q=
                if '/url?q=' in href:
                    # Extract actual URL
                    match = re.search(r'/url\?q=([^&]+)', href)
                    if match:
                        actual_url = urllib.parse.unquote(match.group(1))
                        
                        # Verify it's from the same domain and contains career keywords
                        if domain in actual_url and self._url_contains_career_keywords(actual_url):
                            return actual_url
            
            return None
            
        except Exception as e:
            logger.error(f"Google search failed: {str(e)}")
            return None
    
    def _contains_career_keywords(self, content: str) -> bool:
        """
        Check if content contains career-related keywords
        
        Args:
            content: HTML content
            
        Returns:
            True if career keywords found
        """
        content_lower = content.lower()
        
        # Check for multiple keywords to reduce false positives
        keyword_count = sum(1 for keyword in CAREER_KEYWORDS if keyword in content_lower)
        
        return keyword_count >= 2
    
    def _url_contains_career_keywords(self, url: str) -> bool:
        """
        Check if URL contains career keywords
        
        Args:
            url: URL to check
            
        Returns:
            True if career keywords found in URL
        """
        url_lower = url.lower()
        return any(keyword in url_lower for keyword in CAREER_KEYWORDS)
    
    async def verify_career_page(self, url: str) -> bool:
        """
        Verify that a URL is actually a career page
        
        Args:
            url: URL to verify
            
        Returns:
            True if valid career page
        """
        try:
            success = await self.browser.navigate(url)
            if not success:
                return False
            
            content = await self.browser.get_page_content()
            return self._contains_career_keywords(content)
            
        except Exception as e:
            logger.error(f"Failed to verify career page: {str(e)}")
            return False

"""
Browser Manager module
Handles Playwright browser initialization and human-like interactions
"""
import asyncio
import random
from typing import Optional, List
from playwright.async_api import async_playwright, Browser, Page, BrowserContext
from modules.logger import get_logger
from config import BROWSER_CONFIG, AUTOMATION_CONFIG

logger = get_logger(__name__)

class BrowserManager:
    """Manages browser instance and provides human-like interaction methods"""
    
    def __init__(self):
        """Initialize browser manager"""
        self.playwright = None
        self.browser: Optional[Browser] = None
        self.context: Optional[BrowserContext] = None
        self.page: Optional[Page] = None
    
    async def start(self):
        """Start browser instance"""
        try:
            logger.info("[START] Starting browser...")
            self.playwright = await async_playwright().start()
            
            self.browser = await self.playwright.chromium.launch(
                headless=BROWSER_CONFIG["headless"],
                slow_mo=BROWSER_CONFIG["slow_mo"]
            )
            
            self.context = await self.browser.new_context(
                viewport=BROWSER_CONFIG["viewport"],
                user_agent=BROWSER_CONFIG["user_agent"]
            )
            
            # Set default timeout
            self.context.set_default_timeout(BROWSER_CONFIG["timeout"])
            
            self.page = await self.context.new_page()
            
            logger.success("Browser started successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to start browser: {str(e)}")
            return False
    
    async def close(self):
        """Close browser instance"""
        try:
            if self.page:
                await self.page.close()
            if self.context:
                await self.context.close()
            if self.browser:
                await self.browser.close()
            if self.playwright:
                await self.playwright.stop()
            logger.info("[CLOSE] Browser closed")
        except Exception as e:
            logger.error(f"Error closing browser: {str(e)}")
    
    async def navigate(self, url: str, wait_until: str = "networkidle") -> bool:
        """
        Navigate to URL with human-like delay
        
        Args:
            url: Target URL
            wait_until: Wait condition (load, domcontentloaded, networkidle)
            
        Returns:
            Success status
        """
        try:
            if not self.page:
                logger.error("Browser page not initialized. Call start() first.")
                return False
            
            await self.human_delay()
            logger.info(f"[WEB] Navigating to: {url}")
            await self.page.goto(url, wait_until=wait_until, timeout=BROWSER_CONFIG["timeout"])
            await self.human_delay()
            return True
        except Exception as e:
            logger.error(f"Navigation failed: {str(e)}")
            return False
    
    async def human_delay(self, min_delay: float = None, max_delay: float = None):
        """
        Add random human-like delay
        
        Args:
            min_delay: Minimum delay in seconds
            max_delay: Maximum delay in seconds
        """
        min_d = min_delay or AUTOMATION_CONFIG["min_delay"]
        max_d = max_delay or AUTOMATION_CONFIG["max_delay"]
        delay = random.uniform(min_d, max_d)
        await asyncio.sleep(delay)
    
    async def human_type(self, selector: str, text: str, clear_first: bool = True):
        """
        Type text with human-like delays
        
        Args:
            selector: Element selector
            text: Text to type
            clear_first: Clear field before typing
        """
        try:
            element = await self.page.wait_for_selector(selector, timeout=10000)
            
            if clear_first:
                await element.click(click_count=3)  # Select all
                await element.press("Backspace")
            
            for char in text:
                await element.type(char)
                delay = random.randint(
                    AUTOMATION_CONFIG["typing_delay_min"],
                    AUTOMATION_CONFIG["typing_delay_max"]
                )
                await asyncio.sleep(delay / 1000)
            
            logger.debug(f"Typed text into {selector}")
            
        except Exception as e:
            logger.error(f"Failed to type into {selector}: {str(e)}")
            raise
    
    async def human_click(self, selector: str):
        """
        Click element with human-like delay
        
        Args:
            selector: Element selector
        """
        try:
            await self.human_delay(0.5, 1.5)
            await self.page.click(selector)
            await self.human_delay(0.5, 1.0)
            logger.debug(f"Clicked {selector}")
        except Exception as e:
            logger.error(f"Failed to click {selector}: {str(e)}")
            raise
    
    async def scroll_page(self, direction: str = "down", amount: int = 500):
        """
        Scroll page with human-like behavior
        
        Args:
            direction: Scroll direction (down, up)
            amount: Scroll amount in pixels
        """
        try:
            scroll_amount = amount if direction == "down" else -amount
            await self.page.evaluate(f"window.scrollBy(0, {scroll_amount})")
            await asyncio.sleep(AUTOMATION_CONFIG["scroll_delay"])
        except Exception as e:
            logger.error(f"Scroll failed: {str(e)}")
    
    async def scroll_to_bottom(self):
        """Scroll to bottom of page with multiple steps"""
        try:
            previous_height = 0
            while True:
                # Scroll down
                await self.page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                await asyncio.sleep(AUTOMATION_CONFIG["scroll_delay"])
                
                # Get new height
                new_height = await self.page.evaluate("document.body.scrollHeight")
                
                # Break if no more content
                if new_height == previous_height:
                    break
                    
                previous_height = new_height
                
            logger.debug("Scrolled to bottom of page")
            
        except Exception as e:
            logger.error(f"Failed to scroll to bottom: {str(e)}")
    
    async def wait_for_selector(self, selector: str, timeout: int = 10000):
        """
        Wait for element to appear
        
        Args:
            selector: Element selector
            timeout: Timeout in milliseconds
            
        Returns:
            Element handle or None
        """
        try:
            element = await self.page.wait_for_selector(selector, timeout=timeout)
            return element
        except Exception as e:
            logger.debug(f"Element {selector} not found within timeout")
            return None
    
    async def get_page_content(self) -> str:
        """Get current page HTML content"""
        try:
            return await self.page.content()
        except Exception as e:
            logger.error(f"Failed to get page content: {str(e)}")
            return ""
    
    async def get_page_url(self) -> str:
        """Get current page URL"""
        try:
            return self.page.url
        except Exception as e:
            logger.error(f"Failed to get page URL: {str(e)}")
            return ""
    
    async def screenshot(self, path: str):
        """
        Take screenshot of current page
        
        Args:
            path: Save path for screenshot
        """
        try:
            await self.page.screenshot(path=path, full_page=True)
            logger.debug(f"Screenshot saved to {path}")
        except Exception as e:
            logger.error(f"Failed to take screenshot: {str(e)}")
    
    async def get_all_links(self) -> List[dict]:
        """
        Get all links on current page
        
        Returns:
            List of dicts with href and text
        """
        try:
            links = await self.page.evaluate("""
                () => {
                    const anchors = Array.from(document.querySelectorAll('a'));
                    return anchors.map(a => ({
                        href: a.href,
                        text: a.textContent.trim()
                    }));
                }
            """)
            return links
        except Exception as e:
            logger.error(f"Failed to get links: {str(e)}")
            return []
    
    async def retry_action(self, action_func, max_retries: int = None):
        """
        Retry an action with exponential backoff
        
        Args:
            action_func: Async function to retry
            max_retries: Maximum retry attempts
            
        Returns:
            Action result or None
        """
        retries = max_retries or AUTOMATION_CONFIG["max_retries"]
        
        for attempt in range(retries):
            try:
                result = await action_func()
                return result
            except Exception as e:
                if attempt < retries - 1:
                    wait_time = AUTOMATION_CONFIG["retry_delay"] * (2 ** attempt)
                    logger.warning(f"Attempt {attempt + 1} failed, retrying in {wait_time}s...")
                    await asyncio.sleep(wait_time)
                else:
                    logger.error(f"All {retries} attempts failed")
                    raise e

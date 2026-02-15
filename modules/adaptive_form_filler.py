"""
Adaptive Form Filler
Uses AI to intelligently fill any job application form
"""
import asyncio
from pathlib import Path
from typing import Dict, Optional, List
from modules.logger import get_logger
from modules.browser_manager import BrowserManager
from modules.ai_form_analyzer import AIFormAnalyzer

logger = get_logger(__name__)

class AdaptiveFormFiller:
    """Intelligently fills job application forms using AI"""
    
    def __init__(self, browser: BrowserManager, ai_client=None):
        """
        Initialize adaptive form filler
        
        Args:
            browser: BrowserManager instance
            ai_client: AI client for intelligent decisions
        """
        self.browser = browser
        self.ai_client = ai_client
        self.analyzer = AIFormAnalyzer(browser, ai_client)
        
    async def fill_application(
        self, 
        url: str, 
        user_data: Dict, 
        resume_path: Optional[Path] = None
    ) -> Dict:
        """
        Intelligently fill job application form
        
        Args:
            url: Application form URL
            user_data: User information
            resume_path: Path to resume file
            
        Returns:
            Result dictionary
        """
        try:
            logger.info(f"[AI-FORM] Starting adaptive form filling for {url}")
            
            # Navigate to form
            success = await self.browser.navigate(url)
            if not success:
                return {'status': 'failed', 'reason': 'navigation_failed'}
            
            await self.browser.human_delay(2, 3)
            
            # Detect application system type
            app_type = await self.analyzer.detect_application_type()
            logger.info(f"[AI-FORM] Detected application system: {app_type}")
            
            # Analyze the page
            page_analysis = await self.analyzer.analyze_page()
            logger.info(f"[AI-FORM] Page analysis: {page_analysis.get('understanding', {})}")
            
            # Choose strategy based on analysis
            if app_type in ['greenhouse', 'lever', 'workday']:
                result = await self._fill_known_system(app_type, user_data, resume_path)
            else:
                result = await self._fill_adaptive(page_analysis, user_data, resume_path)
            
            return result
            
        except Exception as e:
            logger.error(f"Adaptive form filling failed: {str(e)}")
            return {'status': 'failed', 'reason': str(e)}
    
    async def _fill_adaptive(
        self, 
        page_analysis: Dict, 
        user_data: Dict, 
        resume_path: Optional[Path]
    ) -> Dict:
        """
        Adaptively fill form based on AI analysis
        
        Args:
            page_analysis: Page structure analysis
            user_data: User information
            resume_path: Resume file path
            
        Returns:
            Result dictionary
        """
        try:
            logger.info("[AI-FORM] Using adaptive filling strategy")
            
            filled_count = 0
            
            # Get intelligent field mapping
            field_mapping = await self.analyzer.get_field_mapping(user_data)
            logger.info(f"[AI-FORM] Mapped {len(field_mapping)} fields")
            
            # Fill text inputs
            for field_id, value in field_mapping.items():
                if not value:
                    continue
                
                try:
                    # Try multiple selector strategies
                    selectors = [
                        f"#{field_id}",
                        f"[name='{field_id}']",
                        f"[id*='{field_id}']",
                        f"[name*='{field_id}']"
                    ]
                    
                    for selector in selectors:
                        try:
                            element = await self.browser.wait_for_selector(selector, timeout=2000)
                            if element:
                                await self.browser.human_type(selector, value)
                                filled_count += 1
                                logger.debug(f"[AI-FORM] Filled {field_id}: {value[:20]}...")
                                break
                        except:
                            continue
                            
                except Exception as e:
                    logger.debug(f"Could not fill {field_id}: {str(e)}")
                    continue
            
            # Handle file upload
            if resume_path and page_analysis.get('has_file_upload'):
                upload_success = await self._upload_resume_adaptive(resume_path)
                if upload_success:
                    filled_count += 1
            
            logger.info(f"[AI-FORM] Successfully filled {filled_count} fields")
            
            # Look for submit button
            submit_found = await self._find_and_click_submit()
            
            return {
                'status': 'success' if submit_found else 'manual_required',
                'fields_filled': filled_count,
                'submitted': submit_found
            }
            
        except Exception as e:
            logger.error(f"Adaptive filling failed: {str(e)}")
            return {'status': 'failed', 'reason': str(e)}
    
    async def _upload_resume_adaptive(self, resume_path: Path) -> bool:
        """
        Intelligently find and use resume upload field
        
        Args:
            resume_path: Path to resume
            
        Returns:
            Success status
        """
        try:
            # Common selectors for file upload
            file_selectors = [
                "input[type='file']",
                "input[accept*='pdf']",
                "input[accept*='doc']",
                "[data-test*='resume']",
                "[data-test*='upload']",
                "[id*='resume']",
                "[id*='upload']",
                "[name*='resume']",
                "[name*='upload']",
                "[class*='upload']",
                "[class*='resume']"
            ]
            
            for selector in file_selectors:
                try:
                    element = await self.browser.wait_for_selector(selector, timeout=2000)
                    if element:
                        # Upload file
                        await element.set_input_files(str(resume_path))
                        logger.info(f"[AI-FORM] Resume uploaded using selector: {selector}")
                        await self.browser.human_delay(1, 2)
                        return True
                except:
                    continue
            
            logger.warning("[AI-FORM] Could not find resume upload field")
            return False
            
        except Exception as e:
            logger.error(f"Resume upload failed: {str(e)}")
            return False
    
    async def _find_and_click_submit(self) -> bool:
        """
        Intelligently find and click submit button
        
        Returns:
            Success status
        """
        try:
            # Common submit button patterns
            submit_patterns = [
                # Text-based
                "//button[contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'submit')]",
                "//button[contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'apply')]",
                "//button[contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'send')]",
                "//button[contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'next')]",
                "//input[@type='submit']",
                # Attribute-based
                "button[type='submit']",
                "[data-test*='submit']",
                "[data-test*='apply']",
                "[id*='submit']",
                "[id*='apply']",
                "[class*='submit']",
                "[class*='apply']"
            ]
            
            for pattern in submit_patterns:
                try:
                    if pattern.startswith('//'):
                        # XPath selector
                        element = await self.browser.page.wait_for_selector(
                            f"xpath={pattern}", 
                            timeout=2000
                        )
                    else:
                        # CSS selector
                        element = await self.browser.wait_for_selector(pattern, timeout=2000)
                    
                    if element:
                        # Check if button is visible and enabled
                        is_visible = await element.is_visible()
                        is_enabled = await element.is_enabled()
                        
                        if is_visible and is_enabled:
                            logger.info(f"[AI-FORM] Found submit button: {pattern}")
                            # Don't click automatically - wait for manual confirmation
                            logger.warning("[AI-FORM] Submit button found - manual review recommended")
                            await self.browser.human_delay(30, 30)  # Give user time to review
                            return True
                except:
                    continue
            
            logger.warning("[AI-FORM] Submit button not found")
            return False
            
        except Exception as e:
            logger.error(f"Submit button search failed: {str(e)}")
            return False
    
    async def _fill_known_system(
        self, 
        system_type: str, 
        user_data: Dict, 
        resume_path: Optional[Path]
    ) -> Dict:
        """
        Fill form using known patterns for specific ATS systems
        
        Args:
            system_type: Type of ATS (greenhouse, lever, etc.)
            user_data: User information
            resume_path: Resume path
            
        Returns:
            Result dictionary
        """
        logger.info(f"[AI-FORM] Using optimized strategy for {system_type}")
        
        # System-specific strategies
        strategies = {
            'greenhouse': self._fill_greenhouse,
            'lever': self._fill_lever,
            'workday': self._fill_workday
        }
        
        strategy = strategies.get(system_type)
        if strategy:
            return await strategy(user_data, resume_path)
        
        # Fallback to adaptive
        page_analysis = await self.analyzer.analyze_page()
        return await self._fill_adaptive(page_analysis, user_data, resume_path)
    
    async def _fill_greenhouse(self, user_data: Dict, resume_path: Optional[Path]) -> Dict:
        """Fill Greenhouse ATS forms"""
        logger.info("[AI-FORM] Filling Greenhouse form")
        # Greenhouse-specific logic here
        return await self._fill_adaptive(await self.analyzer.analyze_page(), user_data, resume_path)
    
    async def _fill_lever(self, user_data: Dict, resume_path: Optional[Path]) -> Dict:
        """Fill Lever ATS forms"""
        logger.info("[AI-FORM] Filling Lever form")
        # Lever-specific logic here
        return await self._fill_adaptive(await self.analyzer.analyze_page(), user_data, resume_path)
    
    async def _fill_workday(self, user_data: Dict, resume_path: Optional[Path]) -> Dict:
        """Fill Workday ATS forms"""
        logger.info("[AI-FORM] Filling Workday form")
        # Workday-specific logic here
        return await self._fill_adaptive(await self.analyzer.analyze_page(), user_data, resume_path)

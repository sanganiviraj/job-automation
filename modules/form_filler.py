"""
Form Filler module
Automatically fills job application forms
"""
from typing import Dict, List, Optional
from modules.logger import get_logger
from modules.browser_manager import BrowserManager
from config import USER_CONFIG, FORM_FIELD_MAPPINGS, TEST_MODE

logger = get_logger(__name__)

class FormFiller:
    """Fills application forms automatically"""
    
    def __init__(self, browser_manager: BrowserManager):
        """
        Initialize form filler
        
        Args:
            browser_manager: BrowserManager instance
        """
        self.browser = browser_manager
        self.user_data = USER_CONFIG
    
    async def fill_application_form(
        self,
        apply_url: str,
        resume_path: str,
        cover_letter: str = None
    ) -> Dict:
        """
        Fill and submit application form
        
        Args:
            apply_url: Application form URL
            resume_path: Path to resume PDF
            cover_letter: Optional cover letter text
            
        Returns:
            Result dictionary with status and message
        """
        try:
            logger.info(f"[FORM] Filling application form at {apply_url}")
            
            # Navigate to application page
            success = await self.browser.navigate(apply_url)
            if not success:
                return {
                    'success': False,
                    'message': 'Failed to load application page'
                }
            
            # Wait for page to load
            await self.browser.human_delay(2, 3)
            
            # Detect and fill form fields
            filled_fields = await self._detect_and_fill_fields()
            
            # Upload resume
            resume_uploaded = await self._upload_resume(resume_path)
            
            # Upload cover letter if provided
            if cover_letter:
                await self._fill_cover_letter(cover_letter)
            
            # Check for submit button
            submit_found = await self._find_submit_button()
            
            if TEST_MODE:
                logger.warning("🧪 TEST MODE: Form filled but not submitted")
                return {
                    'success': True,
                    'message': 'Form filled (test mode - not submitted)',
                    'fields_filled': filled_fields,
                    'resume_uploaded': resume_uploaded
                }
            
            # Try to submit
            if submit_found:
                submitted = await self._submit_form()
                
                if submitted:
                    logger.success("[OK] Application submitted successfully")
                    return {
                        'success': True,
                        'message': 'Application submitted',
                        'fields_filled': filled_fields,
                        'resume_uploaded': resume_uploaded
                    }
                else:
                    logger.warning("[PAUSE] Manual intervention required for submission")
                    return {
                        'success': False,
                        'message': 'Manual submission required',
                        'fields_filled': filled_fields,
                        'resume_uploaded': resume_uploaded,
                        'manual_required': True
                    }
            else:
                logger.warning("[PAUSE] Submit button not found - manual intervention required")
                return {
                    'success': False,
                    'message': 'Submit button not found',
                    'fields_filled': filled_fields,
                    'resume_uploaded': resume_uploaded,
                    'manual_required': True
                }
                
        except Exception as e:
            logger.error(f"Error filling form: {str(e)}")
            return {
                'success': False,
                'message': f'Error: {str(e)}'
            }
    
    async def _detect_and_fill_fields(self) -> int:
        """
        Detect and fill form fields
        
        Returns:
            Number of fields filled
        """
        filled_count = 0
        
        try:
            # Get all input fields
            inputs = await self.browser.page.query_selector_all('input, textarea, select')
            
            for input_elem in inputs:
                try:
                    # Get field attributes
                    field_type = await input_elem.get_attribute('type') or 'text'
                    field_name = await input_elem.get_attribute('name') or ''
                    field_id = await input_elem.get_attribute('id') or ''
                    field_placeholder = await input_elem.get_attribute('placeholder') or ''
                    
                    # Skip hidden and file inputs (handled separately)
                    if field_type in ['hidden', 'file', 'submit', 'button']:
                        continue
                    
                    # Determine field purpose and fill
                    field_info = f"{field_name} {field_id} {field_placeholder}".lower()
                    
                    # Name field
                    if any(keyword in field_info for keyword in FORM_FIELD_MAPPINGS['name']):
                        await self._fill_text_field(input_elem, self.user_data['name'])
                        filled_count += 1
                    
                    # Email field
                    elif any(keyword in field_info for keyword in FORM_FIELD_MAPPINGS['email']):
                        await self._fill_text_field(input_elem, self.user_data['email'])
                        filled_count += 1
                    
                    # Phone field
                    elif any(keyword in field_info for keyword in FORM_FIELD_MAPPINGS['phone']):
                        await self._fill_text_field(input_elem, self.user_data['phone'])
                        filled_count += 1
                    
                    # Address field
                    elif any(keyword in field_info for keyword in FORM_FIELD_MAPPINGS['address']):
                        await self._fill_text_field(input_elem, self.user_data['address'])
                        filled_count += 1
                    
                    # LinkedIn field
                    elif any(keyword in field_info for keyword in FORM_FIELD_MAPPINGS['linkedin']):
                        await self._fill_text_field(input_elem, self.user_data['linkedin'])
                        filled_count += 1
                    
                    # Portfolio field
                    elif any(keyword in field_info for keyword in FORM_FIELD_MAPPINGS['portfolio']):
                        await self._fill_text_field(input_elem, self.user_data['portfolio'])
                        filled_count += 1
                    
                    # Experience field
                    elif any(keyword in field_info for keyword in FORM_FIELD_MAPPINGS['experience']):
                        await self._fill_text_field(input_elem, self.user_data['years_experience'])
                        filled_count += 1
                    
                except Exception as e:
                    logger.debug(f"Error processing field: {str(e)}")
                    continue
            
            logger.info(f"Filled {filled_count} form fields")
            return filled_count
            
        except Exception as e:
            logger.error(f"Error detecting fields: {str(e)}")
            return filled_count
    
    async def _fill_text_field(self, element, value: str):
        """
        Fill a text input field
        
        Args:
            element: Element handle
            value: Value to fill
        """
        try:
            # Clear existing value
            await element.click(click_count=3)
            await element.press('Backspace')
            
            # Type new value with human-like delay
            for char in value:
                await element.type(char)
                await self.browser.human_delay(0.05, 0.15)
            
        except Exception as e:
            logger.debug(f"Error filling text field: {str(e)}")
    
    async def _upload_resume(self, resume_path: str) -> bool:
        """
        Upload resume file
        
        Args:
            resume_path: Path to resume file
            
        Returns:
            Success status
        """
        try:
            # Look for file input
            file_inputs = await self.browser.page.query_selector_all('input[type="file"]')
            
            for file_input in file_inputs:
                try:
                    # Get input attributes
                    input_name = await file_input.get_attribute('name') or ''
                    input_id = await file_input.get_attribute('id') or ''
                    
                    # Check if it's for resume/CV
                    input_info = f"{input_name} {input_id}".lower()
                    
                    if any(keyword in input_info for keyword in FORM_FIELD_MAPPINGS['resume']):
                        logger.info(f"📎 Uploading resume: {resume_path}")
                        await file_input.set_input_files(resume_path)
                        await self.browser.human_delay(1, 2)
                        logger.success("Resume uploaded")
                        return True
                        
                except Exception as e:
                    logger.debug(f"Error with file input: {str(e)}")
                    continue
            
            logger.warning("Resume upload field not found")
            return False
            
        except Exception as e:
            logger.error(f"Error uploading resume: {str(e)}")
            return False
    
    async def _fill_cover_letter(self, cover_letter: str) -> bool:
        """
        Fill cover letter field
        
        Args:
            cover_letter: Cover letter text
            
        Returns:
            Success status
        """
        try:
            # Look for textarea or large text input
            textareas = await self.browser.page.query_selector_all('textarea')
            
            for textarea in textareas:
                try:
                    field_name = await textarea.get_attribute('name') or ''
                    field_id = await textarea.get_attribute('id') or ''
                    
                    field_info = f"{field_name} {field_id}".lower()
                    
                    if any(keyword in field_info for keyword in FORM_FIELD_MAPPINGS['cover_letter']):
                        logger.info("[FILE] Filling cover letter")
                        await self._fill_text_field(textarea, cover_letter)
                        return True
                        
                except Exception as e:
                    logger.debug(f"Error with textarea: {str(e)}")
                    continue
            
            return False
            
        except Exception as e:
            logger.error(f"Error filling cover letter: {str(e)}")
            return False
    
    async def _find_submit_button(self) -> bool:
        """
        Find submit button
        
        Returns:
            True if submit button found
        """
        try:
            # Common submit button selectors
            submit_selectors = [
                'button[type="submit"]',
                'input[type="submit"]',
                'button:has-text("Submit")',
                'button:has-text("Apply")',
                'button:has-text("Send")',
                'a:has-text("Submit Application")'
            ]
            
            for selector in submit_selectors:
                element = await self.browser.wait_for_selector(selector, timeout=5000)
                if element:
                    logger.debug(f"Submit button found: {selector}")
                    return True
            
            return False
            
        except Exception as e:
            logger.debug(f"Error finding submit button: {str(e)}")
            return False
    
    async def _submit_form(self) -> bool:
        """
        Submit the form
        
        Returns:
            Success status
        """
        try:
            # Try different submit methods
            submit_selectors = [
                'button[type="submit"]',
                'input[type="submit"]',
                'button:has-text("Submit")',
                'button:has-text("Apply")',
            ]
            
            for selector in submit_selectors:
                try:
                    element = await self.browser.wait_for_selector(selector, timeout=5000)
                    if element:
                        await self.browser.human_click(selector)
                        await self.browser.human_delay(3, 5)
                        return True
                except:
                    continue
            
            return False
            
        except Exception as e:
            logger.error(f"Error submitting form: {str(e)}")
            return False
    
    async def wait_for_manual_submission(self, timeout: int = 300):
        """
        Wait for user to manually submit form
        
        Args:
            timeout: Wait timeout in seconds
        """
        logger.warning(f"[PAUSE] Waiting for manual submission (timeout: {timeout}s)")
        logger.warning("Please complete and submit the form manually...")
        
        try:
            # Wait for URL change or timeout
            await self.browser.page.wait_for_url(lambda url: url != self.browser.get_page_url(), timeout=timeout * 1000)
            logger.success("Form appears to be submitted")
            return True
        except:
            logger.warning("Manual submission timeout")
            return False

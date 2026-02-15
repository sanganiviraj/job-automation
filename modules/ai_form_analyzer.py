"""
AI-Powered Form Analyzer
Uses AI to understand and interact with any job application form
"""
import json
import re
from typing import Dict, List, Optional, Any
from bs4 import BeautifulSoup
from modules.logger import get_logger
from modules.browser_manager import BrowserManager

logger = get_logger(__name__)

class AIFormAnalyzer:
    """AI-powered form analyzer that adapts to any website"""
    
    def __init__(self, browser: BrowserManager, ai_client):
        """
        Initialize AI form analyzer
        
        Args:
            browser: BrowserManager instance
            ai_client: AI client (Gemini or OpenAI)
        """
        self.browser = browser
        self.ai_client = ai_client
        
    async def analyze_page(self) -> Dict[str, Any]:
        """
        Analyze current page to understand its structure
        
        Returns:
            Dictionary with page analysis
        """
        try:
            logger.info("[AI] Analyzing page structure...")
            
            # Get page content
            html_content = await self.browser.get_page_content()
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Extract all interactive elements
            elements = await self._extract_form_elements(soup)
            
            # Use AI to understand the page
            page_understanding = await self._ai_understand_page(elements, html_content)
            
            return {
                'elements': elements,
                'understanding': page_understanding,
                'has_form': len(elements['inputs']) > 0 or len(elements['textareas']) > 0,
                'has_file_upload': len(elements['file_inputs']) > 0,
                'has_submit_button': len(elements['buttons']) > 0
            }
            
        except Exception as e:
            logger.error(f"Failed to analyze page: {str(e)}")
            return {}
    
    async def _extract_form_elements(self, soup: BeautifulSoup) -> Dict[str, List]:
        """Extract all form elements from page"""
        
        elements = {
            'inputs': [],
            'textareas': [],
            'selects': [],
            'file_inputs': [],
            'buttons': [],
            'labels': []
        }
        
        # Find all input fields
        for input_elem in soup.find_all('input'):
            input_type = input_elem.get('type', 'text')
            element_info = {
                'type': input_type,
                'name': input_elem.get('name', ''),
                'id': input_elem.get('id', ''),
                'placeholder': input_elem.get('placeholder', ''),
                'aria_label': input_elem.get('aria-label', ''),
                'class': ' '.join(input_elem.get('class', [])),
                'required': input_elem.get('required') is not None
            }
            
            if input_type == 'file':
                elements['file_inputs'].append(element_info)
            elif input_type not in ['submit', 'button']:
                elements['inputs'].append(element_info)
        
        # Find textareas
        for textarea in soup.find_all('textarea'):
            elements['textareas'].append({
                'name': textarea.get('name', ''),
                'id': textarea.get('id', ''),
                'placeholder': textarea.get('placeholder', ''),
                'aria_label': textarea.get('aria-label', ''),
                'class': ' '.join(textarea.get('class', []))
            })
        
        # Find select dropdowns
        for select in soup.find_all('select'):
            options = [opt.get_text(strip=True) for opt in select.find_all('option')]
            elements['selects'].append({
                'name': select.get('name', ''),
                'id': select.get('id', ''),
                'aria_label': select.get('aria-label', ''),
                'options': options,
                'class': ' '.join(select.get('class', []))
            })
        
        # Find buttons
        for button in soup.find_all(['button', 'input']):
            if button.name == 'input' and button.get('type') not in ['submit', 'button']:
                continue
            
            button_text = button.get_text(strip=True) if button.name == 'button' else button.get('value', '')
            elements['buttons'].append({
                'text': button_text,
                'type': button.get('type', 'button'),
                'id': button.get('id', ''),
                'class': ' '.join(button.get('class', []))
            })
        
        # Find labels for context
        for label in soup.find_all('label'):
            elements['labels'].append({
                'text': label.get_text(strip=True),
                'for': label.get('for', ''),
                'class': ' '.join(label.get('class', []))
            })
        
        return elements
    
    async def _ai_understand_page(self, elements: Dict, html_snippet: str) -> Dict:
        """Use AI to understand what the page is asking for"""
        
        try:
            # Create a summary of the page
            summary = f"""
            Page has:
            - {len(elements['inputs'])} input fields
            - {len(elements['textareas'])} text areas
            - {len(elements['selects'])} dropdown menus
            - {len(elements['file_inputs'])} file upload fields
            - {len(elements['buttons'])} buttons
            
            Input fields: {json.dumps(elements['inputs'][:5], indent=2)}
            Labels: {json.dumps(elements['labels'][:10], indent=2)}
            Buttons: {json.dumps(elements['buttons'][:5], indent=2)}
            """
            
            prompt = f"""
            You are analyzing a job application form. Based on the form elements below, determine:
            
            1. What type of application form is this? (simple resume upload, detailed form, multi-step, login required, etc.)
            2. What information is being requested?
            3. What is the recommended action strategy?
            
            Form elements:
            {summary}
            
            Respond in JSON format:
            {{
                "form_type": "type of form",
                "required_fields": ["list of required information"],
                "strategy": "recommended filling strategy",
                "complexity": "simple/medium/complex"
            }}
            """
            
            # This would call your AI client
            # For now, return a basic analysis
            return {
                "form_type": "standard_application",
                "required_fields": ["resume", "contact_info"],
                "strategy": "fill_visible_fields_first",
                "complexity": "medium"
            }
            
        except Exception as e:
            logger.error(f"AI understanding failed: {str(e)}")
            return {}
    
    async def get_field_mapping(self, user_data: Dict) -> Dict[str, str]:
        """
        Use AI to map user data to form fields intelligently
        
        Args:
            user_data: User's information
            
        Returns:
            Mapping of field identifiers to values
        """
        try:
            page_analysis = await self.analyze_page()
            elements = page_analysis.get('elements', {})
            
            # Use AI to intelligently map fields
            field_mapping = {}
            
            # Map inputs
            for input_elem in elements.get('inputs', []):
                field_id = input_elem.get('id') or input_elem.get('name')
                if not field_id:
                    continue
                
                # Intelligent field detection
                field_lower = (
                    field_id + ' ' + 
                    input_elem.get('placeholder', '') + ' ' +
                    input_elem.get('aria_label', '')
                ).lower()
                
                # Map to user data
                if any(keyword in field_lower for keyword in ['email', 'e-mail']):
                    field_mapping[field_id] = user_data.get('email', '')
                elif any(keyword in field_lower for keyword in ['phone', 'mobile', 'telephone']):
                    field_mapping[field_id] = user_data.get('phone', '')
                elif any(keyword in field_lower for keyword in ['first', 'fname', 'firstname']):
                    field_mapping[field_id] = user_data.get('name', '').split()[0]
                elif any(keyword in field_lower for keyword in ['last', 'lname', 'lastname']):
                    name_parts = user_data.get('name', '').split()
                    field_mapping[field_id] = name_parts[-1] if len(name_parts) > 1 else ''
                elif any(keyword in field_lower for keyword in ['name', 'full']):
                    field_mapping[field_id] = user_data.get('name', '')
                elif any(keyword in field_lower for keyword in ['linkedin', 'profile']):
                    field_mapping[field_id] = user_data.get('linkedin', '')
                elif any(keyword in field_lower for keyword in ['portfolio', 'website', 'github']):
                    field_mapping[field_id] = user_data.get('portfolio', '')
                elif any(keyword in field_lower for keyword in ['address', 'location', 'city']):
                    field_mapping[field_id] = user_data.get('address', '')
                elif any(keyword in field_lower for keyword in ['experience', 'years']):
                    field_mapping[field_id] = user_data.get('years_experience', '')
            
            return field_mapping
            
        except Exception as e:
            logger.error(f"Field mapping failed: {str(e)}")
            return {}
    
    async def detect_application_type(self) -> str:
        """
        Detect what type of application system this is
        
        Returns:
            Application type (greenhouse, lever, workday, custom, etc.)
        """
        try:
            url = await self.browser.get_page_url()
            html = await self.browser.get_page_content()
            
            # Check URL patterns
            if 'greenhouse' in url.lower():
                return 'greenhouse'
            elif 'lever' in url.lower():
                return 'lever'
            elif 'workday' in url.lower():
                return 'workday'
            elif 'taleo' in url.lower():
                return 'taleo'
            elif 'smartrecruiters' in url.lower():
                return 'smartrecruiters'
            elif 'ashbyhq' in url.lower():
                return 'ashby'
            
            # Check HTML content
            if 'greenhouse' in html.lower():
                return 'greenhouse'
            elif 'lever' in html.lower():
                return 'lever'
            
            return 'custom'
            
        except Exception as e:
            logger.error(f"Failed to detect application type: {str(e)}")
            return 'unknown'

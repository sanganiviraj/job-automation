"""
Resume Modifier module
Uses AI to customize resumes based on job descriptions
Supports both OpenAI and Google Gemini APIs
"""
import os
from typing import Optional
from pathlib import Path
from PyPDF2 import PdfReader
from fpdf import FPDF
from modules.logger import get_logger
from config import (
    AI_PROVIDER,
    OPENAI_API_KEY, OPENAI_MODEL, OPENAI_TEMPERATURE,
    GEMINI_API_KEY, GEMINI_MODEL, GEMINI_TEMPERATURE,
    RESUME_CUSTOMIZATION_PROMPT, MODIFIED_RESUMES_DIR
)

# Conditional imports based on AI provider
try:
    import openai
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False

logger = get_logger(__name__)

class ResumeModifier:
    """Modifies resumes using AI based on job descriptions"""
    
    def __init__(self):
        """Initialize resume modifier"""
        self.provider = AI_PROVIDER
        self.enabled = False
        
        if self.provider == "openai":
            if not OPENAI_API_KEY:
                logger.warning("[WARN] OpenAI API key not set. Resume modification will be disabled.")
            elif not OPENAI_AVAILABLE:
                logger.error("[ERROR] OpenAI library not installed. Run: pip install openai")
            else:
                openai.api_key = OPENAI_API_KEY
                self.enabled = True
                logger.info(f"[OK] Resume modifier initialized with OpenAI ({OPENAI_MODEL})")
        
        elif self.provider == "gemini":
            if not GEMINI_API_KEY:
                logger.warning("[WARN] Gemini API key not set. Resume modification will be disabled.")
            elif not GEMINI_AVAILABLE:
                logger.error("[ERROR] Gemini library not installed. Run: pip install google-generativeai")
            else:
                genai.configure(api_key=GEMINI_API_KEY)
                self.model = genai.GenerativeModel(GEMINI_MODEL)
                self.enabled = True
                logger.info(f"[OK] Resume modifier initialized with Gemini ({GEMINI_MODEL})")
        
        else:
            logger.error(f"[ERROR] Unknown AI provider: {self.provider}. Use 'openai' or 'gemini'")
            self.enabled = False
    
    def extract_text_from_pdf(self, pdf_path: str) -> str:
        """
        Extract text from PDF resume
        
        Args:
            pdf_path: Path to PDF file
            
        Returns:
            Extracted text
        """
        try:
            reader = PdfReader(pdf_path)
            text = ""
            
            for page in reader.pages:
                text += page.extract_text() + "\n"
            
            logger.debug(f"Extracted {len(text)} characters from PDF")
            return text.strip()
            
        except Exception as e:
            logger.error(f"Failed to extract text from PDF: {str(e)}")
            return ""
    
    async def customize_resume(
        self,
        base_resume_path: str,
        job_description: str,
        job_title: str,
        company_name: str
    ) -> Optional[str]:
        """
        Customize resume for specific job using AI
        
        Args:
            base_resume_path: Path to base resume PDF
            job_description: Job description text
            job_title: Job title
            company_name: Company name
            
        Returns:
            Path to customized resume PDF or None
        """
        if not self.enabled:
            logger.warning("Resume modification disabled - returning base resume")
            return base_resume_path
        
        try:
            logger.info(f"[AI] Customizing resume for {job_title} at {company_name}")
            
            # Extract text from base resume
            base_resume_text = self.extract_text_from_pdf(base_resume_path)
            
            if not base_resume_text:
                logger.error("Failed to extract resume text")
                return None
            
            # Generate customized resume using AI
            customized_text = await self._generate_customized_resume(
                base_resume_text,
                job_description,
                job_title,
                company_name
            )
            
            if not customized_text:
                logger.error("Failed to generate customized resume")
                return None
            
            # Create PDF from customized text
            output_path = self._create_resume_pdf(
                customized_text,
                job_title,
                company_name
            )
            
            if output_path:
                logger.success(f"Resume customized and saved to {output_path}")
                return output_path
            else:
                return None
                
        except Exception as e:
            logger.error(f"Error customizing resume: {str(e)}")
            return None
    
    async def _generate_customized_resume(
        self,
        base_resume: str,
        job_description: str,
        job_title: str,
        company_name: str
    ) -> Optional[str]:
        """
        Use AI to generate customized resume
        
        Args:
            base_resume: Base resume text
            job_description: Job description
            job_title: Job title
            company_name: Company name
            
        Returns:
            Customized resume text or None
        """
        try:
            # Prepare prompt
            prompt = RESUME_CUSTOMIZATION_PROMPT.format(
                base_resume=base_resume,
                job_description=job_description[:2000],  # Limit to avoid token limits
                job_title=job_title,
                company_name=company_name
            )
            
            if self.provider == "openai":
                return await self._generate_with_openai(prompt)
            elif self.provider == "gemini":
                return await self._generate_with_gemini(prompt)
            else:
                logger.error(f"Unknown provider: {self.provider}")
                return None
                
        except Exception as e:
            logger.error(f"AI API error: {str(e)}")
            return None
    
    async def _generate_with_openai(self, prompt: str) -> Optional[str]:
        """Generate resume using OpenAI"""
        try:
            logger.debug("Sending request to OpenAI...")
            
            response = openai.chat.completions.create(
                model=OPENAI_MODEL,
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert resume writer who customizes resumes to match job descriptions while maintaining authenticity."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=OPENAI_TEMPERATURE,
                max_tokens=2000
            )
            
            customized_resume = response.choices[0].message.content.strip()
            logger.debug(f"Received {len(customized_resume)} characters from OpenAI")
            return customized_resume
            
        except Exception as e:
            logger.error(f"OpenAI API error: {str(e)}")
            return None
    
    async def _generate_with_gemini(self, prompt: str) -> Optional[str]:
        """Generate resume using Gemini"""
        try:
            logger.debug("Sending request to Gemini...")
            
            # Add system instruction to the prompt
            full_prompt = """You are an expert resume writer who customizes resumes to match job descriptions while maintaining authenticity.

""" + prompt
            
            # Generate content
            response = self.model.generate_content(
                full_prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=GEMINI_TEMPERATURE,
                    max_output_tokens=2000,
                )
            )
            
            customized_resume = response.text.strip()
            logger.debug(f"Received {len(customized_resume)} characters from Gemini")
            return customized_resume
            
        except Exception as e:
            logger.error(f"Gemini API error: {str(e)}")
            return None
    
    def _create_resume_pdf(
        self,
        resume_text: str,
        job_title: str,
        company_name: str
    ) -> Optional[str]:
        """
        Create PDF from resume text
        
        Args:
            resume_text: Resume text content
            job_title: Job title
            company_name: Company name
            
        Returns:
            Path to created PDF or None
        """
        try:
            # Create safe filename
            safe_job_title = "".join(c for c in job_title if c.isalnum() or c in (' ', '-', '_'))[:50]
            safe_company = "".join(c for c in company_name if c.isalnum() or c in (' ', '-', '_'))[:30]
            
            filename = f"{safe_company}_{safe_job_title}.pdf"
            output_path = MODIFIED_RESUMES_DIR / filename
            
            # Create PDF
            pdf = FPDF()
            pdf.add_page()
            pdf.set_auto_page_break(auto=True, margin=15)
            
            # Set font
            pdf.set_font("Arial", size=10)
            
            # Add content
            # Split text into lines and add to PDF
            for line in resume_text.split('\n'):
                # Handle special characters
                line = line.encode('latin-1', 'replace').decode('latin-1')
                pdf.multi_cell(0, 5, line)
            
            # Save PDF
            pdf.output(str(output_path))
            
            logger.debug(f"PDF created: {output_path}")
            
            return str(output_path)
            
        except Exception as e:
            logger.error(f"Failed to create PDF: {str(e)}")
            return None
    
    def get_resume_summary(self, resume_path: str) -> str:
        """
        Get a brief summary of resume content
        
        Args:
            resume_path: Path to resume PDF
            
        Returns:
            Summary text
        """
        try:
            text = self.extract_text_from_pdf(resume_path)
            
            # Return first 500 characters as summary
            return text[:500] + "..." if len(text) > 500 else text
            
        except Exception as e:
            logger.error(f"Failed to get resume summary: {str(e)}")
            return ""

# Modules Package
# Job Application Automation System

"""
This package contains all the core modules for the automation system:

- browser_manager: Playwright browser control with human-like interactions
- career_finder: Career page detection and navigation
- job_scraper: Job listing extraction and parsing
- resume_modifier: AI-powered resume customization
- form_filler: Automatic form filling and submission
- email_extractor: HR email detection and extraction
- excel_writer: Application tracking and reporting
- logger: Comprehensive logging system
"""

__version__ = "1.0.0"
__author__ = "Job Automation Team"

from .browser_manager import BrowserManager
from .career_finder import CareerFinder
from .job_scraper import JobScraper
from .resume_modifier import ResumeModifier
from .form_filler import FormFiller
from .email_extractor import EmailExtractor
from .excel_writer import ExcelWriter
from .logger import get_logger

__all__ = [
    'BrowserManager',
    'CareerFinder',
    'JobScraper',
    'ResumeModifier',
    'FormFiller',
    'EmailExtractor',
    'ExcelWriter',
    'get_logger'
]

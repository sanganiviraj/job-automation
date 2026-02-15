"""
Main application file
Job Application Automation System
"""
import asyncio
import argparse
import sys
from pathlib import Path
from datetime import datetime
from typing import List, Dict

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from modules.browser_manager import BrowserManager
from modules.career_finder import CareerFinder
from modules.job_scraper import JobScraper
from modules.resume_modifier import ResumeModifier
from modules.form_filler import FormFiller
from modules.email_extractor import EmailExtractor
from modules.excel_writer import ExcelWriter
from modules.logger import get_logger

from utils.helpers import (
    read_companies_csv, create_companies_csv, print_banner,
    print_summary, ensure_directories, validate_environment
)
from utils.text_cleaner import clean_text, normalize_company_name

from config import (
    COMPANIES_CSV, USER_CONFIG, TEST_MODE,
    STATUS_SUCCESS, STATUS_MANUAL, STATUS_FAILED,
    STATUS_NO_JOBS, STATUS_NO_CAREER_PAGE, STATUS_ERROR
)

logger = get_logger(__name__)

class JobAutomationPipeline:
    """Main automation pipeline"""
    
    def __init__(self, test_mode: bool = False):
        """
        Initialize automation pipeline
        
        Args:
            test_mode: Whether to run in test mode
        """
        self.test_mode = test_mode or TEST_MODE
        self.browser = None
        self.career_finder = None
        self.job_scraper = None
        self.resume_modifier = None
        self.form_filler = None
        self.email_extractor = None
        self.excel_writer = None
        
        logger.info(f"[INIT] Initializing Job Automation Pipeline (Test Mode: {self.test_mode})")
    
    async def initialize(self):
        """Initialize all components"""
        try:
            # Initialize browser
            self.browser = BrowserManager()
            browser_started = await self.browser.start()
            
            if not browser_started:
                logger.error("Failed to start browser - cannot continue")
                return False
            
            # Initialize modules
            self.career_finder = CareerFinder(self.browser)
            self.job_scraper = JobScraper(self.browser)
            self.resume_modifier = ResumeModifier()
            self.form_filler = FormFiller(self.browser)
            self.email_extractor = EmailExtractor(self.browser)
            self.excel_writer = ExcelWriter()
            
            logger.success("All components initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize components: {str(e)}")
            return False
    
    async def cleanup(self):
        """Cleanup resources"""
        try:
            if self.browser:
                await self.browser.close()
            logger.info("Cleanup completed")
        except Exception as e:
            logger.error(f"Error during cleanup: {str(e)}")
    
    async def process_company(self, company: Dict) -> Dict:
        """
        Process a single company
        
        Args:
            company: Company dictionary with name and url
            
        Returns:
            Processing result dictionary
        """
        company_name = normalize_company_name(company.get('name', 'Unknown'))
        company_url = company.get('url', '')
        
        logger.section(f"Processing: {company_name}")
        logger.info(f"URL: {company_url}")
        
        result = {
            'company_name': company_name,
            'company_url': company_url,
            'career_url': '',
            'jobs_found': 0,
            'applications_submitted': 0,
            'emails_found': [],
            'status': STATUS_ERROR,
            'error': ''
        }
        
        try:
            # Step 1: Find career page
            logger.subsection("Step 1: Finding Career Page")
            career_url = await self.career_finder.find_career_page(company_url)
            
            if not career_url:
                logger.warning(f"[X] No career page found for {company_name}")
                result['status'] = STATUS_NO_CAREER_PAGE
                self.excel_writer.add_application({
                    'company_name': company_name,
                    'company_url': company_url,
                    'status': STATUS_NO_CAREER_PAGE
                })
                return result
            
            result['career_url'] = career_url
            logger.success(f"Career page: {career_url}")
            
            # Step 2: Extract emails
            logger.subsection("Step 2: Extracting Emails")
            emails = await self.email_extractor.extract_emails(career_url)
            result['emails_found'] = emails
            
            if emails:
                logger.success(f"Found {len(emails)} email(s): {', '.join(emails)}")
            else:
                logger.info("No emails found")
            
            # Step 3: Scrape jobs
            logger.subsection("Step 3: Scraping Job Listings")
            jobs = await self.job_scraper.scrape_jobs(career_url, company_name)
            result['jobs_found'] = len(jobs)
            
            if not jobs:
                logger.warning(f"[INFO] No relevant jobs found at {company_name}")
                result['status'] = STATUS_NO_JOBS
                self.excel_writer.add_application({
                    'company_name': company_name,
                    'company_url': company_url,
                    'career_url': career_url,
                    'hr_email': ', '.join(emails) if emails else '',
                    'status': STATUS_NO_JOBS
                })
                return result
            
            logger.success(f"Found {len(jobs)} relevant job(s)")
            
            # Step 4: Process each job
            logger.subsection(f"Step 4: Processing {len(jobs)} Job(s)")
            
            for idx, job in enumerate(jobs, 1):
                logger.info(f"\n--- Job {idx}/{len(jobs)}: {job['title']} ---")
                
                job_result = await self.process_job(
                    job,
                    company_name,
                    company_url,
                    career_url,
                    emails
                )
                
                if job_result['success']:
                    result['applications_submitted'] += 1
            
            # Set overall status
            if result['applications_submitted'] > 0:
                result['status'] = STATUS_SUCCESS
            else:
                result['status'] = STATUS_FAILED
            
            return result
            
        except Exception as e:
            logger.error(f"Error processing {company_name}: {str(e)}")
            result['status'] = STATUS_ERROR
            result['error'] = str(e)
            
            self.excel_writer.add_application({
                'company_name': company_name,
                'company_url': company_url,
                'status': STATUS_ERROR,
                'error': str(e)
            })
            
            return result
    
    async def process_job(
        self,
        job: Dict,
        company_name: str,
        company_url: str,
        career_url: str,
        emails: List[str]
    ) -> Dict:
        """
        Process a single job application
        
        Args:
            job: Job dictionary
            company_name: Company name
            company_url: Company URL
            career_url: Career page URL
            emails: List of HR emails
            
        Returns:
            Result dictionary
        """
        result = {'success': False, 'message': ''}
        
        try:
            job_title = job.get('title', 'Unknown Position')
            job_description = job.get('description', '')
            apply_link = job.get('apply_link')
            
            logger.info(f"[JOB] Job: {job_title}")
            logger.info(f"[LOC] Location: {job.get('location', 'N/A')}")
            
            # Step 4.1: Customize resume
            logger.info("[AI] Customizing resume...")
            
            customized_resume = await self.resume_modifier.customize_resume(
                base_resume_path=USER_CONFIG['base_resume_path'],
                job_description=job_description,
                job_title=job_title,
                company_name=company_name
            )
            
            if not customized_resume:
                logger.warning("Failed to customize resume, using base resume")
                customized_resume = USER_CONFIG['base_resume_path']
            else:
                logger.success(f"Resume customized: {Path(customized_resume).name}")
            
            # Step 4.2: Fill application form
            if apply_link:
                logger.info(f"[FORM] Filling application form...")
                
                form_result = await self.form_filler.fill_application_form(
                    apply_url=apply_link,
                    resume_path=customized_resume
                )
                
                if form_result.get('success'):
                    status = STATUS_SUCCESS
                    logger.success("[OK] Application submitted successfully")
                    result['success'] = True
                    result['message'] = 'Application submitted'
                elif form_result.get('manual_required'):
                    status = STATUS_MANUAL
                    logger.warning("[MANUAL] Manual intervention required")
                    result['message'] = 'Manual submission required'
                else:
                    status = STATUS_FAILED
                    logger.error("[FAIL] Application failed")
                    result['message'] = form_result.get('message', 'Unknown error')
            else:
                status = STATUS_FAILED
                logger.warning("[WARN] No apply link found")
                result['message'] = 'No apply link'
            
            # Log to Excel
            self.excel_writer.add_application({
                'company_name': company_name,
                'company_url': company_url,
                'career_url': career_url,
                'job_title': job_title,
                'job_location': job.get('location', ''),
                'job_description': job_description,
                'apply_link': apply_link or '',
                'hr_email': ', '.join(emails) if emails else '',
                'status': status,
                'error': result.get('message', ''),
                'resume_path': customized_resume
            })
            
            return result
            
        except Exception as e:
            logger.error(f"Error processing job: {str(e)}")
            result['message'] = str(e)
            return result
    
    async def run(self, companies: List[Dict], limit: int = None):
        """
        Run automation pipeline
        
        Args:
            companies: List of company dictionaries
            limit: Optional limit on number of companies to process
        """
        start_time = datetime.now()
        
        # Limit companies if specified
        if limit:
            companies = companies[:limit]
        
        total_companies = len(companies)
        logger.info(f"[START] Starting automation for {total_companies} companies")
        
        # Process each company
        for idx, company in enumerate(companies, 1):
            logger.progress(idx, total_companies, f"- {company.get('name', 'Unknown')}")
            
            try:
                await self.process_company(company)
            except Exception as e:
                logger.error(f"Unexpected error: {str(e)}")
                continue
            
            # Small delay between companies
            if idx < total_companies:
                await asyncio.sleep(2)
        
        # Calculate duration
        duration = (datetime.now() - start_time).total_seconds()
        
        # Print summary
        logger.section("AUTOMATION COMPLETED")
        logger.info(f"[TIME] Total time: {duration:.1f} seconds")
        
        # Get and print statistics
        stats = self.excel_writer.get_statistics()
        print_summary(stats)
        
        # Export emails
        if stats.get('emails_found', 0) > 0:
            self.excel_writer.export_emails()

async def main():
    """Main entry point"""
    # Parse arguments
    parser = argparse.ArgumentParser(description='Job Application Automation System')
    parser.add_argument('--test', action='store_true', help='Run in test mode (no submissions)')
    parser.add_argument('--limit', type=int, help='Limit number of companies to process')
    parser.add_argument('--create-sample', action='store_true', help='Create sample companies.csv')
    
    args = parser.parse_args()
    
    # Print banner
    print_banner()
    
    # Create sample CSV if requested
    if args.create_sample:
        create_companies_csv(COMPANIES_CSV, sample_data=True)
        return
    
    # Ensure directories exist
    ensure_directories()
    
    # Validate environment
    is_valid, errors = validate_environment()
    if not is_valid:
        logger.error("[FAIL] Environment validation failed:")
        for error in errors:
            logger.error(f"  - {error}")
        
        # Create companies CSV if missing
        if not COMPANIES_CSV.exists():
            logger.info("Creating sample companies.csv...")
            create_companies_csv(COMPANIES_CSV, sample_data=True)
        
        return
    
    # Read companies
    companies = read_companies_csv(COMPANIES_CSV)
    
    if not companies:
        logger.error("No companies found in CSV file")
        logger.info(f"Please add companies to: {COMPANIES_CSV}")
        return
    
    # Initialize pipeline
    pipeline = JobAutomationPipeline(test_mode=args.test)
    
    try:
        # Initialize components
        success = await pipeline.initialize()
        if not success:
            logger.error("Failed to initialize pipeline")
            return
        
        # Run automation
        await pipeline.run(companies, limit=args.limit)
        
    except KeyboardInterrupt:
        logger.warning("\n[INTERRUPT] Interrupted by user")
    except Exception as e:
        logger.error(f"Fatal error: {str(e)}")
    finally:
        # Cleanup
        await pipeline.cleanup()
        logger.info("[BYE] Goodbye!")

if __name__ == "__main__":
    # Run async main
    asyncio.run(main())

"""
Job Scraper module
Extracts job listings and details from career pages
"""
import re
from typing import List, Dict, Optional
from bs4 import BeautifulSoup
from modules.logger import get_logger
from modules.browser_manager import BrowserManager
from config import JOB_RELEVANCE_KEYWORDS

logger = get_logger(__name__)

class JobScraper:
    """Scrapes job listings from career pages"""
    
    def __init__(self, browser_manager: BrowserManager):
        """
        Initialize job scraper
        
        Args:
            browser_manager: BrowserManager instance
        """
        self.browser = browser_manager
    
    async def scrape_jobs(self, career_url: str, company_name: str) -> List[Dict]:
        """
        Scrape all jobs from career page
        
        Args:
            career_url: Career page URL
            company_name: Company name
            
        Returns:
            List of job dictionaries
        """
        try:
            logger.info(f"[JOB] Scraping jobs from {career_url}")
            
            # Navigate to career page
            success = await self.browser.navigate(career_url)
            if not success:
                logger.error("Failed to load career page")
                return []
            
            # Scroll to load all jobs (lazy loading)
            await self.browser.scroll_to_bottom()
            
            # Get page content
            content = await self.browser.get_page_content()
            soup = BeautifulSoup(content, 'html.parser')
            
            # Extract jobs using multiple strategies
            jobs = []
            
            # Strategy 1: Look for common job listing patterns
            jobs.extend(await self._extract_jobs_strategy_1(soup, company_name))
            
            # Strategy 2: Look for links containing "apply" or "job"
            if not jobs:
                jobs.extend(await self._extract_jobs_strategy_2(soup, company_name))
            
            # Strategy 3: Generic extraction
            if not jobs:
                jobs.extend(await self._extract_jobs_strategy_3(soup, company_name))
            
            logger.success(f"Found {len(jobs)} job listings")
            
            # Filter relevant jobs
            relevant_jobs = self._filter_relevant_jobs(jobs)
            logger.info(f"🎯 {len(relevant_jobs)} relevant jobs after filtering")
            
            return relevant_jobs
            
        except Exception as e:
            logger.error(f"Error scraping jobs: {str(e)}")
            return []
    
    async def _extract_jobs_strategy_1(self, soup: BeautifulSoup, company_name: str) -> List[Dict]:
        """
        Extract jobs using common HTML patterns
        
        Args:
            soup: BeautifulSoup object
            company_name: Company name
            
        Returns:
            List of job dictionaries
        """
        jobs = []
        
        # Common job listing selectors
        job_selectors = [
            {'class': re.compile(r'job.*item', re.I)},
            {'class': re.compile(r'position.*item', re.I)},
            {'class': re.compile(r'opening', re.I)},
            {'class': re.compile(r'vacancy', re.I)},
            {'class': re.compile(r'career.*card', re.I)},
        ]
        
        for selector in job_selectors:
            job_elements = soup.find_all(['div', 'li', 'article'], selector)
            
            for element in job_elements:
                job = self._parse_job_element(element, company_name)
                if job and job not in jobs:
                    jobs.append(job)
        
        return jobs
    
    async def _extract_jobs_strategy_2(self, soup: BeautifulSoup, company_name: str) -> List[Dict]:
        """
        Extract jobs by finding apply/job links
        
        Args:
            soup: BeautifulSoup object
            company_name: Company name
            
        Returns:
            List of job dictionaries
        """
        jobs = []
        
        # Find all links
        links = soup.find_all('a', href=True)
        
        for link in links:
            href = link.get('href', '')
            text = link.get_text(strip=True)
            
            # Check if link is job-related
            if any(keyword in href.lower() for keyword in ['job', 'apply', 'position', 'opening']):
                job = {
                    'title': text or 'Unknown Position',
                    'location': 'Not specified',
                    'description': '',
                    'skills': [],
                    'apply_link': href if href.startswith('http') else None,
                    'company': company_name
                }
                
                if job not in jobs:
                    jobs.append(job)
        
        return jobs
    
    async def _extract_jobs_strategy_3(self, soup: BeautifulSoup, company_name: str) -> List[Dict]:
        """
        Generic job extraction from headings and links
        
        Args:
            soup: BeautifulSoup object
            company_name: Company name
            
        Returns:
            List of job dictionaries
        """
        jobs = []
        
        # Look for headings that might be job titles
        headings = soup.find_all(['h1', 'h2', 'h3', 'h4'])
        
        for heading in headings:
            text = heading.get_text(strip=True)
            
            # Check if heading looks like a job title
            if len(text) > 10 and len(text) < 100:
                # Look for nearby apply link
                parent = heading.parent
                apply_link = None
                
                if parent:
                    link = parent.find('a', href=True)
                    if link:
                        apply_link = link.get('href')
                
                job = {
                    'title': text,
                    'location': 'Not specified',
                    'description': '',
                    'skills': [],
                    'apply_link': apply_link if apply_link and apply_link.startswith('http') else None,
                    'company': company_name
                }
                
                if job not in jobs:
                    jobs.append(job)
        
        return jobs[:20]  # Limit to prevent too many false positives
    
    def _parse_job_element(self, element, company_name: str) -> Optional[Dict]:
        """
        Parse individual job element
        
        Args:
            element: BeautifulSoup element
            company_name: Company name
            
        Returns:
            Job dictionary or None
        """
        try:
            # Extract title
            title_elem = element.find(['h1', 'h2', 'h3', 'h4', 'h5', 'a'])
            title = title_elem.get_text(strip=True) if title_elem else 'Unknown Position'
            
            # Extract location
            location = 'Not specified'
            location_patterns = [
                re.compile(r'location', re.I),
                re.compile(r'city', re.I),
                re.compile(r'office', re.I)
            ]
            
            for pattern in location_patterns:
                location_elem = element.find(class_=pattern)
                if location_elem:
                    location = location_elem.get_text(strip=True)
                    break
            
            # Extract description
            description = element.get_text(strip=True)[:500]  # First 500 chars
            
            # Extract skills
            skills = self._extract_skills(description)
            
            # Extract apply link
            apply_link = None
            link_elem = element.find('a', href=True)
            if link_elem:
                href = link_elem.get('href')
                if href.startswith('http'):
                    apply_link = href
            
            return {
                'title': title,
                'location': location,
                'description': description,
                'skills': skills,
                'apply_link': apply_link,
                'company': company_name
            }
            
        except Exception as e:
            logger.debug(f"Failed to parse job element: {str(e)}")
            return None
    
    def _extract_skills(self, text: str) -> List[str]:
        """
        Extract skills from text
        
        Args:
            text: Job description text
            
        Returns:
            List of skills
        """
        skills = []
        text_lower = text.lower()
        
        # Common technical skills
        skill_keywords = [
            'python', 'java', 'javascript', 'react', 'node.js', 'sql',
            'aws', 'docker', 'kubernetes', 'git', 'agile', 'scrum',
            'machine learning', 'ai', 'data science', 'backend', 'frontend',
            'full stack', 'devops', 'cloud', 'api', 'rest', 'graphql'
        ]
        
        for skill in skill_keywords:
            if skill in text_lower:
                skills.append(skill)
        
        return skills
    
    def _filter_relevant_jobs(self, jobs: List[Dict]) -> List[Dict]:
        """
        Filter jobs based on relevance keywords
        
        Args:
            jobs: List of job dictionaries
            
        Returns:
            Filtered list of relevant jobs
        """
        if not JOB_RELEVANCE_KEYWORDS:
            return jobs
        
        relevant_jobs = []
        
        for job in jobs:
            # Combine title and description for matching
            job_text = f"{job['title']} {job['description']}".lower()
            
            # Check if any relevance keyword matches
            match_count = sum(1 for keyword in JOB_RELEVANCE_KEYWORDS if keyword.lower() in job_text)
            
            # If at least one keyword matches, consider it relevant
            if match_count > 0:
                job['relevance_score'] = match_count
                relevant_jobs.append(job)
        
        # Sort by relevance score
        relevant_jobs.sort(key=lambda x: x.get('relevance_score', 0), reverse=True)
        
        return relevant_jobs
    
    async def get_job_details(self, job_url: str) -> Dict:
        """
        Get detailed job information from job page
        
        Args:
            job_url: Job detail page URL
            
        Returns:
            Job details dictionary
        """
        try:
            logger.info(f"[FILE] Fetching job details from {job_url}")
            
            success = await self.browser.navigate(job_url)
            if not success:
                return {}
            
            content = await self.browser.get_page_content()
            soup = BeautifulSoup(content, 'html.parser')
            
            # Extract full description
            description = soup.get_text(strip=True)
            
            # Extract skills
            skills = self._extract_skills(description)
            
            return {
                'description': description,
                'skills': skills,
                'url': job_url
            }
            
        except Exception as e:
            logger.error(f"Failed to get job details: {str(e)}")
            return {}

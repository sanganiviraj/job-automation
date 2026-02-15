"""
Helper utilities
General helper functions for the automation system
"""
import asyncio
import csv
from pathlib import Path
from typing import List, Dict
from datetime import datetime

def read_companies_csv(csv_path: str) -> List[Dict]:
    """
    Read companies from CSV file
    
    Args:
        csv_path: Path to CSV file
        
    Returns:
        List of company dictionaries
    """
    companies = []
    
    try:
        with open(csv_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                companies.append({
                    'name': row.get('name', ''),
                    'url': row.get('url', ''),
                })
        
        return companies
        
    except Exception as e:
        print(f"Error reading CSV: {str(e)}")
        return []

def create_companies_csv(csv_path: str, sample_data: bool = True):
    """
    Create sample companies CSV file
    
    Args:
        csv_path: Path to create CSV
        sample_data: Whether to include sample data
    """
    try:
        with open(csv_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=['name', 'url'])
            writer.writeheader()
            
            if sample_data:
                # Sample companies
                sample_companies = [
                    {'name': 'Google', 'url': 'https://www.google.com'},
                    {'name': 'Microsoft', 'url': 'https://www.microsoft.com'},
                    {'name': 'Amazon', 'url': 'https://www.amazon.com'},
                    {'name': 'Meta', 'url': 'https://www.meta.com'},
                    {'name': 'Apple', 'url': 'https://www.apple.com'},
                ]
                writer.writerows(sample_companies)
        
        print(f"[OK] Created companies CSV: {csv_path}")
        
    except Exception as e:
        print(f"Error creating CSV: {str(e)}")

def format_duration(seconds: float) -> str:
    """
    Format duration in human-readable format
    
    Args:
        seconds: Duration in seconds
        
    Returns:
        Formatted string
    """
    if seconds < 60:
        return f"{seconds:.1f}s"
    elif seconds < 3600:
        minutes = seconds / 60
        return f"{minutes:.1f}m"
    else:
        hours = seconds / 3600
        return f"{hours:.1f}h"

def print_banner():
    """Print application banner"""
    banner = """
    ==============================================================
                                                                  
           JOB APPLICATION AUTOMATION SYSTEM                     
                                                                  
          Intelligent automation for job applications            
                                                                  
    ==============================================================
    """
    print(banner)

def print_summary(stats: Dict):
    """
    Print summary statistics
    
    Args:
        stats: Statistics dictionary
    """
    print("\n" + "="*60)
    print("[SUMMARY] APPLICATION SUMMARY")
    print("="*60)
    print(f"Total Companies Processed: {stats.get('companies_processed', 0)}")
    print(f"Total Applications: {stats.get('total_applications', 0)}")
    print(f"[SUCCESS] Successful: {stats.get('successful', 0)}")
    print(f"[MANUAL] Manual Required: {stats.get('manual_required', 0)}")
    print(f"[FAILED] Failed: {stats.get('failed', 0)}")
    print(f"[INFO] No Relevant Jobs: {stats.get('no_jobs', 0)}")
    print(f"[WARNING] No Career Page: {stats.get('no_career_page', 0)}")
    print(f"[EMAIL] Emails Found: {stats.get('emails_found', 0)}")
    print("="*60 + "\n")

async def async_retry(func, max_retries: int = 3, delay: float = 1.0):
    """
    Retry async function with exponential backoff
    
    Args:
        func: Async function to retry
        max_retries: Maximum retry attempts
        delay: Initial delay in seconds
        
    Returns:
        Function result
    """
    for attempt in range(max_retries):
        try:
            return await func()
        except Exception as e:
            if attempt < max_retries - 1:
                wait_time = delay * (2 ** attempt)
                await asyncio.sleep(wait_time)
            else:
                raise e

def ensure_directories():
    """Ensure all required directories exist"""
    from config import DATA_DIR, OUTPUT_DIR, RESUMES_DIR, MODIFIED_RESUMES_DIR
    
    for directory in [DATA_DIR, OUTPUT_DIR, RESUMES_DIR, MODIFIED_RESUMES_DIR]:
        directory.mkdir(parents=True, exist_ok=True)

def validate_environment():
    """
    Validate environment setup
    
    Returns:
        Tuple of (is_valid, error_messages)
    """
    errors = []
    
    # Check Python version
    import sys
    if sys.version_info < (3, 10):
        errors.append("Python 3.10+ required")
    
    # Check required files
    from config import COMPANIES_CSV, USER_CONFIG
    
    if not COMPANIES_CSV.exists():
        errors.append(f"Companies CSV not found: {COMPANIES_CSV}")
    
    # Check base resume
    base_resume = Path(USER_CONFIG['base_resume_path'])
    if not base_resume.exists():
        errors.append(f"Base resume not found: {base_resume}")
    
    # Check AI API key based on provider
    from config import AI_PROVIDER, OPENAI_API_KEY, GEMINI_API_KEY
    
    if AI_PROVIDER == "openai":
        if not OPENAI_API_KEY:
            errors.append("OpenAI API key not set (resume customization will be disabled)")
    elif AI_PROVIDER == "gemini":
        if not GEMINI_API_KEY:
            errors.append("Gemini API key not set (resume customization will be disabled)")
    else:
        errors.append(f"Unknown AI provider: {AI_PROVIDER}. Use 'openai' or 'gemini'")
    
    return (len(errors) == 0, errors)

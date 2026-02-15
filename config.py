"""
Configuration file for Job Application Automation System
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Base paths
BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"
OUTPUT_DIR = DATA_DIR / "output"
RESUMES_DIR = DATA_DIR / "resumes"
MODIFIED_RESUMES_DIR = OUTPUT_DIR / "modified_resumes"

# Create directories if they don't exist
for directory in [DATA_DIR, OUTPUT_DIR, RESUMES_DIR, MODIFIED_RESUMES_DIR]:
    directory.mkdir(parents=True, exist_ok=True)

# User configuration
USER_CONFIG = {
    "name": os.getenv("USER_NAME", "John Doe"),
    "email": os.getenv("USER_EMAIL", "john.doe@example.com"),
    "phone": os.getenv("USER_PHONE", "+1234567890"),
    "address": os.getenv("USER_ADDRESS", "123 Main St, City, State 12345"),
    "linkedin": os.getenv("USER_LINKEDIN", "https://linkedin.com/in/johndoe"),
    "portfolio": os.getenv("USER_PORTFOLIO", "https://johndoe.com"),
    "base_resume_path": os.getenv("BASE_RESUME_PATH", str(RESUMES_DIR / "base_resume.pdf")),
    "years_experience": os.getenv("YEARS_EXPERIENCE", "5"),
    "current_title": os.getenv("CURRENT_TITLE", "Software Engineer"),
    "skills": os.getenv("USER_SKILLS", "Python, JavaScript, React, Node.js, SQL"),
}

# AI Provider configuration (openai or gemini)
AI_PROVIDER = os.getenv("AI_PROVIDER", "gemini").lower()

# OpenAI configuration
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4")
OPENAI_TEMPERATURE = float(os.getenv("OPENAI_TEMPERATURE", "0.7"))

# Gemini configuration
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")  # Free tier model
GEMINI_TEMPERATURE = float(os.getenv("GEMINI_TEMPERATURE", "0.7"))

# Browser configuration
BROWSER_CONFIG = {
    "headless": os.getenv("HEADLESS", "False").lower() == "true",
    "slow_mo": int(os.getenv("SLOW_MO", "100")),  # milliseconds
    "timeout": int(os.getenv("TIMEOUT", "30000")),  # milliseconds
    "viewport": {
        "width": int(os.getenv("VIEWPORT_WIDTH", "1920")),
        "height": int(os.getenv("VIEWPORT_HEIGHT", "1080"))
    },
    "user_agent": os.getenv("USER_AGENT", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
}

# Automation settings
AUTOMATION_CONFIG = {
    "min_delay": float(os.getenv("MIN_DELAY", "1.0")),  # seconds
    "max_delay": float(os.getenv("MAX_DELAY", "3.0")),  # seconds
    "typing_delay_min": int(os.getenv("TYPING_DELAY_MIN", "50")),  # milliseconds
    "typing_delay_max": int(os.getenv("TYPING_DELAY_MAX", "150")),  # milliseconds
    "scroll_delay": float(os.getenv("SCROLL_DELAY", "0.5")),  # seconds
    "max_retries": int(os.getenv("MAX_RETRIES", "3")),
    "retry_delay": float(os.getenv("RETRY_DELAY", "2.0")),  # seconds
}

# Career page keywords
CAREER_KEYWORDS = [
    "careers", "jobs", "join us", "work with us", "opportunities",
    "hiring", "employment", "job openings", "open positions", "vacancies",
    "join our team", "we're hiring", "job opportunities", "career opportunities"
]

# Job relevance keywords (customize based on your profile)
JOB_RELEVANCE_KEYWORDS = os.getenv("JOB_KEYWORDS", "python,software engineer,developer,backend,full stack,api,web development").split(",")

# Email regex pattern
EMAIL_PATTERN = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'

# File paths
COMPANIES_CSV = DATA_DIR / "companies.csv"
APPLICATIONS_LOG = OUTPUT_DIR / "applications_log.xlsx"
SYSTEM_LOG = OUTPUT_DIR / "system_logs.txt"

# Test mode
TEST_MODE = os.getenv("TEST_MODE", "False").lower() == "true"

# Resume modification settings
RESUME_MODIFICATION = {
    "modification_percentage": float(os.getenv("RESUME_MOD_PERCENTAGE", "0.20")),  # 20%
    "preserve_formatting": True,
    "maintain_structure": True,
}

# AI Resume customization prompt template
RESUME_CUSTOMIZATION_PROMPT = """
You are an expert resume writer. Your task is to customize a resume for a specific job description.

IMPORTANT RULES:
1. Modify ONLY approximately 20% of the content
2. Emphasize skills and experiences that match the job description
3. Keep the same overall structure and formatting
4. Maintain a professional tone
5. Do not fabricate experience or skills
6. Focus on reordering, rephrasing, and highlighting relevant points

BASE RESUME:
{base_resume}

JOB DESCRIPTION:
{job_description}

JOB TITLE:
{job_title}

COMPANY:
{company_name}

Please provide a customized version of the resume that highlights the most relevant skills and experiences for this position. Return ONLY the modified resume text, no additional commentary.
"""

# Logging configuration
LOGGING_CONFIG = {
    "level": os.getenv("LOG_LEVEL", "INFO"),
    "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    "date_format": "%Y-%m-%d %H:%M:%S",
    "file": str(SYSTEM_LOG),
    "console": True,
    "colors": True,
}

# Excel columns
EXCEL_COLUMNS = [
    "Timestamp",
    "Company Name",
    "Company URL",
    "Career Page URL",
    "Job Title",
    "Job Location",
    "Job Description",
    "Apply Link",
    "HR Email",
    "Application Status",
    "Error Message",
    "Resume Path"
]

# Application statuses
STATUS_SUCCESS = "[SUCCESS] Applied Successfully"
STATUS_MANUAL = "[MANUAL] Manual Intervention Required"
STATUS_FAILED = "[FAILED] Failed"
STATUS_NO_JOBS = "[INFO] No Relevant Jobs Found"
STATUS_NO_CAREER_PAGE = "[WARNING] Career Page Not Found"
STATUS_ERROR = "[ERROR] Error Occurred"

# Form field mappings (common field names to look for)
FORM_FIELD_MAPPINGS = {
    "name": ["name", "full name", "fullname", "your name", "applicant name", "first name", "last name"],
    "email": ["email", "e-mail", "email address", "your email", "contact email"],
    "phone": ["phone", "telephone", "mobile", "contact number", "phone number", "cell"],
    "address": ["address", "location", "city", "state", "country"],
    "linkedin": ["linkedin", "linkedin profile", "linkedin url"],
    "portfolio": ["portfolio", "website", "personal website", "github"],
    "resume": ["resume", "cv", "curriculum vitae", "upload resume", "attach resume"],
    "cover_letter": ["cover letter", "coverletter", "letter"],
    "experience": ["experience", "years of experience", "work experience"],
}

# Dashboard display
DASHBOARD_ENABLED = True

print(f"[OK] Configuration loaded successfully")
print(f"[DIR] Data directory: {DATA_DIR}")
print(f"[FILE] Companies file: {COMPANIES_CSV}")
print(f"[TEST] Test mode: {TEST_MODE}")
print(f"[BROWSER] Headless browser: {BROWSER_CONFIG['headless']}")

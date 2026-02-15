# Utils Package
# Job Application Automation System

"""
Utility functions for the automation system:

- text_cleaner: Text processing and normalization
- helpers: General helper functions and utilities
"""

__version__ = "1.0.0"

from .text_cleaner import (
    clean_text,
    extract_domain,
    truncate_text,
    normalize_company_name,
    sanitize_filename,
    extract_keywords
)

from .helpers import (
    read_companies_csv,
    create_companies_csv,
    format_duration,
    print_banner,
    print_summary,
    ensure_directories,
    validate_environment
)

__all__ = [
    'clean_text',
    'extract_domain',
    'truncate_text',
    'normalize_company_name',
    'sanitize_filename',
    'extract_keywords',
    'read_companies_csv',
    'create_companies_csv',
    'format_duration',
    'print_banner',
    'print_summary',
    'ensure_directories',
    'validate_environment'
]

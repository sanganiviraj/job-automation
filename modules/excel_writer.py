"""
Excel Writer module
Writes application data to Excel files
"""
import pandas as pd
from datetime import datetime
from pathlib import Path
from typing import Dict, List
from modules.logger import get_logger
from config import APPLICATIONS_LOG, EXCEL_COLUMNS

logger = get_logger(__name__)

class ExcelWriter:
    """Writes application data to Excel"""
    
    def __init__(self):
        """Initialize Excel writer"""
        self.log_file = APPLICATIONS_LOG
        self.columns = EXCEL_COLUMNS
        
        # Initialize Excel file if it doesn't exist
        if not self.log_file.exists():
            self._create_new_log()
        
        logger.info(f"[STATS] Excel writer initialized: {self.log_file}")
    
    def _create_new_log(self):
        """Create new Excel log file"""
        try:
            df = pd.DataFrame(columns=self.columns)
            df.to_excel(self.log_file, index=False, engine='openpyxl')
            logger.info("Created new applications log file")
        except Exception as e:
            logger.error(f"Failed to create log file: {str(e)}")
    
    def add_application(self, application_data: Dict):
        """
        Add application record to Excel
        
        Args:
            application_data: Dictionary with application details
        """
        try:
            # Read existing data
            try:
                df = pd.read_excel(self.log_file, engine='openpyxl')
            except:
                df = pd.DataFrame(columns=self.columns)
            
            # Prepare row data
            row_data = {
                'Timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'Company Name': application_data.get('company_name', ''),
                'Company URL': application_data.get('company_url', ''),
                'Career Page URL': application_data.get('career_url', ''),
                'Job Title': application_data.get('job_title', ''),
                'Job Location': application_data.get('job_location', ''),
                'Job Description': application_data.get('job_description', '')[:500],  # Limit length
                'Apply Link': application_data.get('apply_link', ''),
                'HR Email': application_data.get('hr_email', ''),
                'Application Status': application_data.get('status', ''),
                'Error Message': application_data.get('error', ''),
                'Resume Path': application_data.get('resume_path', '')
            }
            
            # Append row
            df = pd.concat([df, pd.DataFrame([row_data])], ignore_index=True)
            
            # Save to Excel
            df.to_excel(self.log_file, index=False, engine='openpyxl')
            
            logger.debug(f"Added application record for {application_data.get('company_name')}")
            
        except Exception as e:
            logger.error(f"Failed to add application to Excel: {str(e)}")
    
    def get_statistics(self) -> Dict:
        """
        Get application statistics
        
        Returns:
            Dictionary with statistics
        """
        try:
            df = pd.read_excel(self.log_file, engine='openpyxl')
            
            stats = {
                'total_applications': len(df),
                'successful': len(df[df['Application Status'].str.contains('Successfully', na=False)]),
                'manual_required': len(df[df['Application Status'].str.contains('Manual', na=False)]),
                'failed': len(df[df['Application Status'].str.contains('Failed', na=False)]),
                'no_jobs': len(df[df['Application Status'].str.contains('No Relevant Jobs', na=False)]),
                'no_career_page': len(df[df['Application Status'].str.contains('Career Page Not Found', na=False)]),
                'emails_found': len(df[df['HR Email'].notna() & (df['HR Email'] != '')]),
                'companies_processed': df['Company Name'].nunique()
            }
            
            return stats
            
        except Exception as e:
            logger.error(f"Failed to get statistics: {str(e)}")
            return {}
    
    def export_emails(self, output_file: str = None):
        """
        Export all collected emails to a separate file
        
        Args:
            output_file: Optional output file path
        """
        try:
            df = pd.read_excel(self.log_file, engine='openpyxl')
            
            # Filter rows with emails
            emails_df = df[df['HR Email'].notna() & (df['HR Email'] != '')]
            
            # Select relevant columns
            export_df = emails_df[['Company Name', 'HR Email', 'Job Title', 'Career Page URL']]
            
            # Output file
            if not output_file:
                output_file = self.log_file.parent / 'extracted_emails.xlsx'
            
            # Save
            export_df.to_excel(output_file, index=False, engine='openpyxl')
            
            logger.success(f"Exported {len(export_df)} emails to {output_file}")
            
        except Exception as e:
            logger.error(f"Failed to export emails: {str(e)}")
    
    def get_all_applications(self) -> pd.DataFrame:
        """
        Get all application records
        
        Returns:
            DataFrame with all applications
        """
        try:
            return pd.read_excel(self.log_file, engine='openpyxl')
        except Exception as e:
            logger.error(f"Failed to read applications: {str(e)}")
            return pd.DataFrame()

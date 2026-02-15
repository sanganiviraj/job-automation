"""
Logger module for Job Application Automation System
Provides comprehensive logging with colors and file output
"""
import logging
import sys
from pathlib import Path
from datetime import datetime
import colorlog
from config import LOGGING_CONFIG, SYSTEM_LOG

class AutomationLogger:
    """Custom logger for the automation system"""
    
    def __init__(self, name: str = "JobAutomation"):
        """
        Initialize logger with console and file handlers
        
        Args:
            name: Logger name
        """
        self.logger = logging.getLogger(name)
        self.logger.setLevel(getattr(logging, LOGGING_CONFIG["level"]))
        
        # Prevent duplicate handlers
        if self.logger.handlers:
            return
            
        # Console handler with colors
        if LOGGING_CONFIG["console"]:
            console_handler = logging.StreamHandler(sys.stdout)
            console_handler.setLevel(logging.DEBUG)
            
            if LOGGING_CONFIG["colors"]:
                console_formatter = colorlog.ColoredFormatter(
                    "%(log_color)s%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                    datefmt=LOGGING_CONFIG["date_format"],
                    log_colors={
                        'DEBUG': 'cyan',
                        'INFO': 'green',
                        'WARNING': 'yellow',
                        'ERROR': 'red',
                        'CRITICAL': 'red,bg_white',
                    }
                )
                console_handler.setFormatter(console_formatter)
            else:
                console_formatter = logging.Formatter(
                    LOGGING_CONFIG["format"],
                    datefmt=LOGGING_CONFIG["date_format"]
                )
                console_handler.setFormatter(console_formatter)
            
            self.logger.addHandler(console_handler)
        
        # File handler
        file_handler = logging.FileHandler(LOGGING_CONFIG["file"], encoding='utf-8')
        file_handler.setLevel(logging.DEBUG)
        file_formatter = logging.Formatter(
            LOGGING_CONFIG["format"],
            datefmt=LOGGING_CONFIG["date_format"]
        )
        file_handler.setFormatter(file_formatter)
        self.logger.addHandler(file_handler)
    
    def debug(self, message: str):
        """Log debug message"""
        self.logger.debug(message)
    
    def info(self, message: str):
        """Log info message"""
        self.logger.info(message)
    
    def warning(self, message: str):
        """Log warning message"""
        self.logger.warning(message)
    
    def error(self, message: str):
        """Log error message"""
        self.logger.error(message)
    
    def critical(self, message: str):
        """Log critical message"""
        self.logger.critical(message)
    
    def section(self, title: str):
        """Log a section header"""
        separator = "=" * 80
        self.logger.info(f"\n{separator}\n{title.center(80)}\n{separator}")
    
    def subsection(self, title: str):
        """Log a subsection header"""
        separator = "-" * 80
        self.logger.info(f"\n{separator}\n{title}\n{separator}")
    
    def success(self, message: str):
        """Log success message"""
        self.logger.info(f"[OK] {message}")
    
    def failure(self, message: str):
        """Log failure message"""
        self.logger.error(f"[FAIL] {message}")
    
    def progress(self, current: int, total: int, message: str = ""):
        """Log progress"""
        percentage = (current / total) * 100 if total > 0 else 0
        self.logger.info(f"[PROGRESS] {current}/{total} ({percentage:.1f}%) {message}")

# Global logger instance
logger = AutomationLogger()

def get_logger(name: str = None) -> AutomationLogger:
    """
    Get logger instance
    
    Args:
        name: Optional logger name
        
    Returns:
        AutomationLogger instance
    """
    if name:
        return AutomationLogger(name)
    return logger

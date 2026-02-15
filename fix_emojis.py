"""
Script to fix emoji characters in Python files for Windows console compatibility
"""
import os
import re
from pathlib import Path

# Emoji replacements
EMOJI_REPLACEMENTS = {
    '🤖': '[AI]',
    '✅': '[OK]',
    '❌': '[X]',
    '⏸️': '[PAUSE]',
    'ℹ️': '[INFO]',
    '⚠️': '[WARN]',
    '🔴': '[ERROR]',
    '📊': '[STATS]',
    '📧': '[EMAIL]',
    '🌐': '[WEB]',
    '📁': '[DIR]',
    '📄': '[FILE]',
    '📋': '[JOB]',
    '📍': '[LOC]',
    '📝': '[FORM]',
    '🚀': '[START]',
    '⏱️': '[TIME]',
    '👋': '[BYE]',
}

def fix_file(filepath):
    """Fix emoji characters in a file"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        
        # Replace each emoji
        for emoji, replacement in EMOJI_REPLACEMENTS.items():
            content = content.replace(emoji, replacement)
        
        # Only write if changes were made
        if content != original_content:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"Fixed: {filepath}")
            return True
        return False
    except Exception as e:
        print(f"Error fixing {filepath}: {e}")
        return False

def main():
    """Main function"""
    base_dir = Path(__file__).parent
    modules_dir = base_dir / 'modules'
    
    fixed_count = 0
    
    # Fix all Python files in modules directory
    for py_file in modules_dir.glob('*.py'):
        if fix_file(py_file):
            fixed_count += 1
    
    print(f"\nTotal files fixed: {fixed_count}")

if __name__ == '__main__':
    main()

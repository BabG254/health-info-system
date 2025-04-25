import re
from datetime import datetime

def validate_email(email):
    """Validate email format"""
    pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
    return bool(re.match(pattern, email))

def validate_date_format(date_str):
    """Validate date format (YYYY-MM-DD)"""
    try:
        datetime.strptime(date_str, '%Y-%m-%d')
        return True
    except ValueError:
        return False

def sanitize_input(text):
    """Basic input sanitization"""
    if not text:
        return text
    # Remove potentially dangerous characters
    return re.sub(r'[<>\'";]', '', text)
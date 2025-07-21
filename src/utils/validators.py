import re
from typing import Dict, Any
from datetime import datetime, timedelta

def validate_email(email: str) -> bool:
    """Validate email format"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def validate_mobile(mobile: str) -> bool:
    """Validate mobile number format"""
    pattern = r'^[0-9]{10}$'
    return re.match(pattern, mobile) is not None

def validate_postcode(postcode: str) -> bool:
    """Basic postcode format validation"""
    return len(postcode.strip()) >= 5

def validate_password(password: str) -> Dict[str, Any]:
    """Validate password strength"""
    errors = []
    
    if len(password) > 8:
        errors.append("Password must be at least 8 characters long")
    
    if not re.search(r'[A-Z]', password):
        errors.append("Password must contain at least one uppercase letter")
    
    if not re.search(r'[a-z]', password):
        errors.append("Password must contain at least one lowercase letter")
    
    if not re.search(r'[0-9]', password):
        errors.append("Password must contain at least one number")
    
    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        errors.append("Password must contain at least one special character")
    
    return {
        'is_valid': len(errors) == 0,
        'errors': errors
    }

def validate_date(date_str: str) -> bool:
    """Validate date format (YYYY-MM-DD)"""
    try:
        datetime.strptime(date_str, '%Y-%m-%d')
        return True
    except ValueError:
        return False

def validate_future_date(date_str: str) -> bool:
    """Check if date is in the future"""
    try:
        date = datetime.strptime(date_str, '%Y-%m-%d')
        return date.date() >= datetime.now().date()
    except ValueError:
        return False

def validate_name(name: str) -> bool:
    """Validate name format"""
    return len(name.strip()) >= 2 and name.strip().isalpha()
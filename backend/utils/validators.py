import re
from datetime import datetime

def validate_email(email):
    """
    Validate email format
    Rules:
    - Must contain @ symbol
    - Must have domain with at least one dot
    - No spaces allowed
    """
    if not email or not isinstance(email, str):
        return False
    
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def validate_phone(phone):
    """
    Validate phone number (Indian format)
    Rules:
    - 10 digits for Indian numbers
    - Optional +91 prefix
    - Only digits allowed (after removing + and spaces)
    """
    if not phone or not isinstance(phone, str):
        return False
    
    cleaned = phone.replace(' ', '').replace('-', '').replace('+', '')
    
    if cleaned.isdigit():
        if len(cleaned) == 10:
            return True
        elif len(cleaned) == 12 and cleaned.startswith('91'):
            return True
    
    return False

def validate_password(password):
    """
    Validate password strength
    Returns: (is_valid, message)
    """
    if not password or not isinstance(password, str):
        return False, "Password is required"
    
    if len(password) < 8:
        return False, "Password must be at least 8 characters long"
    
    if not re.search(r'[A-Z]', password):
        return False, "Password must contain at least one uppercase letter"
    
    if not re.search(r'[a-z]', password):
        return False, "Password must contain at least one lowercase letter"
    
    if not re.search(r'[0-9]', password):
        return False, "Password must contain at least one number"
    
    has_special = bool(re.search(r'[!@#$%^&*(),.?":{}|<>]', password))
    
    if has_special:
        return True, "Strong password"
    else:
        return True, "Password is acceptable. Adding special characters makes it stronger."

def validate_name(name):
    """Validate name (2-50 characters, letters and spaces only)"""
    if not name or not isinstance(name, str):
        return False
    
    name = name.strip()
    if len(name) < 2 or len(name) > 50:
        return False
    
    pattern = r'^[a-zA-Z\s\-\']+$'
    return re.match(pattern, name) is not None

def validate_location(latitude, longitude):
    """Validate geographical coordinates"""
    try:
        lat = float(latitude)
        lng = float(longitude)
        
        if -90 <= lat <= 90 and -180 <= lng <= 180:
            return True, "Valid location"
        else:
            return False, "Invalid coordinates"
    except (ValueError, TypeError):
        return False, "Invalid coordinate format"

def sanitize_input(text):
    """Basic input sanitization - remove HTML tags, escape special characters"""
    if not text or not isinstance(text, str):
        return text
    
    text = re.sub(r'<[^>]+>', '', text)
    text = text.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
    text = text.replace('"', '&quot;').replace("'", '&#39;')
    
    return text.strip()

def validate_severity(severity):
    """Validate severity level"""
    valid_severity = ['low', 'medium', 'high', 'critical']
    return severity in valid_severity

def get_password_strength(password):
    """Get password strength score and description"""
    if not password:
        return 0, "No password"
    
    score = 0
    if len(password) >= 8:
        score += 1
    if len(password) >= 12:
        score += 1
    if re.search(r'[a-z]', password):
        score += 1
    if re.search(r'[A-Z]', password):
        score += 1
    if re.search(r'[0-9]', password):
        score += 1
    if re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        score += 1
    
    if score <= 2:
        return score, "Weak"
    elif score <= 4:
        return score, "Medium"
    elif score <= 6:
        return score, "Strong"
    else:
        return score, "Very Strong"
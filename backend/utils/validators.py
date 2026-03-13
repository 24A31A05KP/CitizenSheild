import re

def validate_email(email):
    """Validate email format"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def validate_phone(phone):
    """Validate phone number (10-15 digits, optional + prefix)"""
    pattern = r'^\+?[1-9][0-9]{9,14}$'
    return re.match(pattern, phone.replace(' ', '')) is not None

def validate_password(password):
    """Validate password strength"""
    if len(password) < 8:
        return False, "Password must be at least 8 characters long"
    
    if not re.search(r'[A-Z]', password):
        return False, "Password must contain at least one uppercase letter"
    
    if not re.search(r'[a-z]', password):
        return False, "Password must contain at least one lowercase letter"
    
    if not re.search(r'[0-9]', password):
        return False, "Password must contain at least one number"
    
    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        return False, "Password must contain at least one special character"
    
    return True, "Password is valid"

def validate_name(name):
    """Validate name (2-50 characters, letters and spaces only)"""
    if len(name) < 2 or len(name) > 50:
        return False
    pattern = r'^[a-zA-Z\s]+$'
    return re.match(pattern, name) is not None

def sanitize_input(text):
    """Basic input sanitization"""
    if not text:
        return text
    # Remove any HTML tags
    text = re.sub(r'<[^>]+>', '', text)
    # Escape special characters
    text = text.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
    return text
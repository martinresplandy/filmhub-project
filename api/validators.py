import re
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User

def validate_email(email):
    if '@' not in email:
        raise ValidationError('Email format is invalid. Use format: name@example.com')
    
    first_part, domain_part = email.rsplit('@', 1)
    
    if not first_part or not domain_part:
        raise ValidationError('Email format is invalid. Use format: name@example.com')
    
    if '.' not in domain_part:
        raise ValidationError('Email format is invalid. Use format: name@example.com')
    
    if domain_part.startswith('.') or domain_part.endswith('.'):
        raise ValidationError('Email format is invalid. Use format: name@example.com')

def validate_email_unique(email):
    if User.objects.filter(email=email).exists():
        raise ValidationError('This email already exists in the system.')

def validate_password_strength(password):
    errors = []
    
    if len(password) < 8:
        errors.append('Password must have at least 8 characters.')
    
    if not re.search(r'[a-zA-Z]', password):
        errors.append('Password must contain at least 1 letter.')
    
    if not re.search(r'[0-9]', password):
        errors.append('Password must contain at least 1 number.')
    
    if not re.search(r'[!@#$%^&*()_+\-=\[\]{};:\'",.<>?/\\|`~]', password):
        errors.append('Password must contain at least 1 special character.')
    
    if errors:
        raise ValidationError(errors)

def validate_username(username):
    if not username or username.strip() == '':
        raise ValidationError('Username cannot be empty.')
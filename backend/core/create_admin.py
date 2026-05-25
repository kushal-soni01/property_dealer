#!/usr/bin/env python
"""
Script to create a Django superuser if one doesn't exist.
Run after migrations during deployment.

Environment variables (optional):
- ADMIN_USERNAME: Username for superuser (default: admin)
- ADMIN_PASSWORD: Password for superuser (default: admin@123)
- ADMIN_EMAIL: Email for superuser (default: admin@example.com)
"""

import os
import sys
import django

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.contrib.auth import get_user_model

User = get_user_model()

# Get credentials from environment variables or use defaults
username = os.getenv('ADMIN_USERNAME', 'admin')
password = os.getenv('ADMIN_PASSWORD', 'admin@123')
email = os.getenv('ADMIN_EMAIL', 'admin@example.com')

try:
    # Check if superuser already exists
    if User.objects.filter(username=username).exists():
        print(f"✓ Superuser '{username}' already exists.")
        sys.exit(0)
    
    # Create the superuser
    User.objects.create_superuser(username, email, password)
    print(f"✓ Superuser '{username}' created successfully!")
    print(f"  Email: {email}")
    print(f"  Access Django Admin at: /admin/")
    sys.exit(0)

except Exception as e:
    print(f"✗ Error creating superuser: {e}")
    sys.exit(1)

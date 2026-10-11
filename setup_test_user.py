#!/usr/bin/env python
"""
Quick setup script to create a test user for the Pharmacy Management System.

Run this after creating a superuser to add a regular test user.

Usage:
    python manage.py shell < setup_test_user.py

Or manually run the commands in manage.py shell.
"""

from django.contrib.auth.models import User

# Check if test user already exists
if not User.objects.filter(username='testuser').exists():
    # Create a test user
    user = User.objects.create_user(
        username='testuser',
        email='testuser@example.com',
        password='testpass123',
        first_name='Test',
        last_name='User'
    )
    print(f"✓ Test user created: {user.username}")
    print(f"  Email: {user.email}")
    print(f"  Password: testpass123")
else:
    print("✗ Test user 'testuser' already exists.")

# Show all users
print("\nExisting users:")
for user in User.objects.all():
    print(f"  - {user.username} (superuser: {user.is_superuser})")


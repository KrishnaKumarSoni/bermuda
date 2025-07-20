#!/usr/bin/env python3
"""
Create the test form with specific ID needed for test suite
"""

import sys
import os
sys.path.append('/Users/admin/Desktop/Dev/bermuda-01/api')

from firebase_integration import firebase_manager
from datetime import datetime, timezone

# Create the test form data with specific ID
test_form_data = {
    'form_id': 'test-form-123',
    'title': 'Pizza Preferences Survey',
    'questions': [
        {
            "text": "What is your favorite pizza topping?",
            "type": "text",
            "enabled": True
        },
        {
            "text": "How often do you eat pizza?",
            "type": "multiple_choice",
            "options": ["Daily", "Weekly", "Monthly", "Rarely"],
            "enabled": True
        },
        {
            "text": "Do you prefer thick or thin crust?",
            "type": "multiple_choice",
            "options": ["Thick crust", "Thin crust"],
            "enabled": True
        },
        {
            "text": "Rate your overall pizza satisfaction",
            "type": "rating",
            "options": ["1", "2", "3", "4", "5"],
            "enabled": True
        }
    ],
    'demographics': [
        {
            "name": "Age Range",
            "type": "multiple_choice",
            "options": ["18-25", "26-35", "36-45", "46-55", "55+"],
            "enabled": True
        }
    ],
    'created_at': datetime.now(timezone.utc).isoformat(),
    'updated_at': datetime.now(timezone.utc).isoformat(),
    'creator_id': 'test-user-123',
    'status': 'active'
}

def create_specific_test_form():
    """Create test form with specific ID for test suite"""
    
    print("Creating test form with ID 'test-form-123' for test suite...")
    
    # Save directly to Firebase using the manager
    success = firebase_manager.save_form('test-form-123', test_form_data)
    
    if success:
        print("✅ Test form created successfully with ID: test-form-123")
        print("📋 Share URL: https://bermuda-01.web.app/form/test-form-123")
        return 'test-form-123'
    else:
        print("❌ Failed to create test form in Firebase")
        return None

if __name__ == "__main__":
    create_specific_test_form()
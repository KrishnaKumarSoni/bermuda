#!/usr/bin/env python3
"""
Create a test form with specific ID for demo purposes
"""

import sys
import os
import json
from datetime import datetime, timezone

# Add the api directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'api'))

from firebase_integration import firebase_manager

def create_test_form():
    """Create test form with specific ID"""
    
    # The form ID from the user's URL
    form_id = "f64feb24-9054-4fe0-90f2-e9a853bb27e1"
    
    # Test form data
    form_document = {
        'form_id': form_id,
        'title': 'Coffee Experience Survey',
        'questions': [
            {
                'text': 'What is your favorite coffee drink?',
                'type': 'text',
                'enabled': True
            },
            {
                'text': 'How do you prefer your coffee?',
                'type': 'multiple_choice',
                'options': ['Black', 'With milk', 'With sugar', 'With both milk and sugar', 'Specialty drinks'],
                'enabled': True
            },
            {
                'text': 'How often do you drink coffee?',
                'type': 'multiple_choice',
                'options': ['Multiple times daily', 'Once daily', 'Few times a week', 'Occasionally', 'Rarely'],
                'enabled': True
            },
            {
                'text': 'Rate your coffee expertise from 1 to 5',
                'type': 'rating',
                'options': ['1', '2', '3', '4', '5'],
                'enabled': True
            },
            {
                'text': 'Do you prefer coffee shops or home brewing?',
                'type': 'yes_no',
                'options': ['Coffee shops', 'Home brewing'],
                'enabled': True
            }
        ],
        'demographics': [
            {
                'name': 'Age Range',
                'type': 'multiple_choice',
                'options': ['18-24', '25-34', '35-44', '45-54', '55+'],
                'enabled': True
            },
            {
                'name': 'Location',
                'type': 'text',
                'options': [],
                'enabled': True
            }
        ],
        'created_at': datetime.now(timezone.utc).isoformat(),
        'updated_at': datetime.now(timezone.utc).isoformat(),
        'creator_id': 'demo-user',
        'status': 'active'
    }
    
    try:
        # Save to Firebase
        success = firebase_manager.save_form(form_id, form_document)
        
        if success:
            print(f"✅ Test form created successfully!")
            print(f"Form ID: {form_id}")
            print(f"Title: {form_document['title']}")
            print(f"URL: https://bermuda-01.web.app/form/{form_id}")
            print(f"Questions: {len(form_document['questions'])}")
            print(f"Demographics: {len(form_document['demographics'])}")
            return True
        else:
            print("❌ Failed to save form to Firebase")
            return False
            
    except Exception as e:
        print(f"❌ Error creating test form: {e}")
        return False

if __name__ == "__main__":
    success = create_test_form()
    sys.exit(0 if success else 1)
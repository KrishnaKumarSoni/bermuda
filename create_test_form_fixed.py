#!/usr/bin/env python3
"""
Create the test form needed for the test suite
"""

import requests
import json

# Create the test form data
test_form_data = {
    "title": "Pizza Preferences Survey",
    "questions": [
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
    "demographics": [
        {
            "name": "Age Range",
            "type": "multiple_choice",
            "options": ["18-25", "26-35", "36-45", "46-55", "55+"],
            "enabled": True
        }
    ]
}

def create_test_form():
    """Create test form with specific ID"""
    
    print("Creating test form for test suite...")
    
    # Save the form using the API
    response = requests.post(
        "https://bermuda-01.web.app/api/save-form",
        json=test_form_data,
        headers={
            "Content-Type": "application/json",
            "Authorization": "Bearer test-token"
        },
        timeout=15
    )
    
    if response.status_code == 200:
        result = response.json()
        form_id = result.get('form_id')
        print(f"✅ Test form created successfully with ID: {form_id}")
        print(f"📋 Share URL: {result.get('share_url')}")
        return form_id
    else:
        print(f"❌ Failed to create test form: {response.status_code}")
        try:
            print(f"Error: {response.json()}")
        except:
            print(f"Response: {response.text}")
        return None

if __name__ == "__main__":
    create_test_form()
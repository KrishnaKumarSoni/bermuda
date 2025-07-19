#!/usr/bin/env python3
"""
Test the actual OpenAI inference functionality
"""
import requests
import json
import os
from dotenv import load_dotenv
import firebase_admin
from firebase_admin import credentials, auth

# Load environment variables
load_dotenv('../.env')

# Initialize Firebase Admin if not already initialized
if not firebase_admin._apps:
    cred = credentials.Certificate('../firebase-adminsdk.json')
    firebase_admin.initialize_app(cred)

def create_test_token():
    """Create a test token for a test user"""
    try:
        # Create a test user
        test_user = auth.create_user(
            uid='test-user-123',
            email='test@example.com',
            display_name='Test User'
        )
        
        # Create a custom token
        custom_token = auth.create_custom_token('test-user-123')
        return custom_token.decode('utf-8')
    except Exception as e:
        print(f"Error creating test token: {e}")
        # If user already exists, just create token
        try:
            custom_token = auth.create_custom_token('test-user-123')
            return custom_token.decode('utf-8')
        except Exception as e2:
            print(f"Error creating token for existing user: {e2}")
            return None

def test_inference():
    """Test the /api/infer endpoint with actual OpenAI"""
    
    # Create test token
    token = create_test_token()
    if not token:
        print("❌ Failed to create test token")
        return
    
    print("✅ Test token created")
    
    # Test data
    test_dump = """
    Customer feedback survey about our new coffee shop experience:
    
    We want to understand what customers think about our new location. 
    Questions we need answered:
    - What's your favorite type of coffee? (espresso, latte, cappuccino, americano)
    - How often do you visit coffee shops? (daily, weekly, monthly, rarely)
    - What's your preferred time to visit? (morning, afternoon, evening)
    - How would you rate our service on a scale of 1-5?
    - Do you have any dietary restrictions or allergies?
    - Would you recommend us to friends? yes/no
    - How much do you typically spend on coffee per visit?
    """
    
    print("🚀 Testing /api/infer endpoint with OpenAI...")
    print(f"📝 Test dump: {test_dump[:100]}...")
    
    try:
        response = requests.post(
            'http://localhost:5000/api/infer',
            headers={
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {token}'
            },
            json={'dump': test_dump}
        )
        
        print(f"📊 Response status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ OpenAI inference successful!")
            print(f"🎯 Generated title: {data.get('title', 'N/A')}")
            print(f"📋 Generated questions: {len(data.get('questions', []))}")
            
            # Print questions
            for i, question in enumerate(data.get('questions', []), 1):
                print(f"  {i}. {question.get('text', 'N/A')} [{question.get('type', 'N/A')}]")
                if question.get('options'):
                    print(f"     Options: {question.get('options')}")
            
            return True
        else:
            print(f"❌ Request failed: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

def test_save_form():
    """Test saving a form to Firebase"""
    
    # Create test token
    token = create_test_token()
    if not token:
        print("❌ Failed to create test token")
        return
    
    print("🚀 Testing /api/save-form endpoint...")
    
    test_form = {
        "title": "Test Coffee Survey",
        "questions": [
            {
                "text": "What's your favorite coffee type?",
                "type": "multiple_choice",
                "options": ["Espresso", "Latte", "Cappuccino", "Americano"],
                "enabled": True
            },
            {
                "text": "How often do you visit coffee shops?",
                "type": "multiple_choice", 
                "options": ["Daily", "Weekly", "Monthly", "Rarely"],
                "enabled": True
            },
            {
                "text": "Would you recommend us?",
                "type": "yes_no",
                "options": ["Yes", "No"],
                "enabled": True
            }
        ],
        "demographics": []
    }
    
    try:
        response = requests.post(
            'http://localhost:5000/api/save-form',
            headers={
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {token}'
            },
            json=test_form
        )
        
        print(f"📊 Response status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Form saved successfully!")
            print(f"🆔 Form ID: {data.get('form_id', 'N/A')}")
            return data.get('form_id')
        else:
            print(f"❌ Request failed: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return None

def main():
    print("🧪 Testing Bermuda Form Creation Backend")
    print("=" * 50)
    
    # Test 1: Inference
    print("\n1. Testing OpenAI Inference...")
    inference_success = test_inference()
    
    # Test 2: Save Form
    print("\n2. Testing Firebase Save...")
    form_id = test_save_form()
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 Test Results:")
    print(f"   OpenAI Inference: {'✅ PASS' if inference_success else '❌ FAIL'}")
    print(f"   Firebase Save: {'✅ PASS' if form_id else '❌ FAIL'}")
    
    if inference_success and form_id:
        print("\n🎉 All tests passed! The form creation system is working!")
        print("💡 You can now test the frontend at http://localhost:8000")
    else:
        print("\n⚠️  Some tests failed. Check the logs for details.")
    
    # Clean up test user
    try:
        auth.delete_user('test-user-123')
        print("🧹 Cleaned up test user")
    except:
        pass

if __name__ == "__main__":
    main()
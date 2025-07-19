#!/usr/bin/env python3
"""
Test script for Bermuda API endpoints
"""
import os
import sys
import json
import requests
from dotenv import load_dotenv
import firebase_admin
from firebase_admin import credentials, auth

# Load environment variables
load_dotenv('../.env')

# Initialize Firebase Admin
if not firebase_admin._apps:
    cred = credentials.Certificate('../firebase-adminsdk.json')
    firebase_admin.initialize_app(cred)

BASE_URL = 'http://localhost:5000'

def test_health_endpoint():
    """Test the health endpoint"""
    try:
        response = requests.get(f'{BASE_URL}/health')
        print(f"Health endpoint: {response.status_code}")
        if response.status_code == 200:
            print(f"Response: {response.json()}")
            return True
        else:
            print(f"Error: {response.text}")
            return False
    except Exception as e:
        print(f"Health endpoint error: {e}")
        return False

def test_infer_endpoint():
    """Test the infer endpoint without auth (should fail)"""
    try:
        data = {
            "dump": "This is a customer feedback survey about our coffee shop. We want to know favorite coffee types, how often they visit, and if they have any allergies."
        }
        response = requests.post(f'{BASE_URL}/api/infer', json=data)
        print(f"Infer endpoint (no auth): {response.status_code}")
        if response.status_code == 401:
            print("✓ Correctly requires authentication")
            return True
        else:
            print(f"Unexpected response: {response.text}")
            return False
    except Exception as e:
        print(f"Infer endpoint error: {e}")
        return False

def test_form_metadata_endpoint():
    """Test the form metadata endpoint (anonymous)"""
    try:
        # This should return 404 since we don't have any forms yet
        response = requests.get(f'{BASE_URL}/api/forms/test-form-id')
        print(f"Form metadata endpoint: {response.status_code}")
        if response.status_code == 404:
            print("✓ Correctly returns 404 for non-existent form")
            return True
        else:
            print(f"Unexpected response: {response.text}")
            return False
    except Exception as e:
        print(f"Form metadata endpoint error: {e}")
        return False

def test_chat_message_endpoint():
    """Test the chat message endpoint"""
    try:
        data = {
            "session_id": "test-session-123",
            "form_id": "test-form-id",
            "message": "Hello, I'd like to take the survey",
            "device_id": "test-device-123",
            "location": {"country": "US", "city": "San Francisco"}
        }
        response = requests.post(f'{BASE_URL}/api/chat-message', json=data)
        print(f"Chat message endpoint: {response.status_code}")
        if response.status_code == 404:
            print("✓ Correctly returns 404 for non-existent form")
            return True
        else:
            print(f"Response: {response.text}")
            return response.status_code in [200, 404]
    except Exception as e:
        print(f"Chat message endpoint error: {e}")
        return False

def main():
    print("Testing Bermuda API endpoints...")
    print("=" * 50)
    
    tests = [
        ("Health endpoint", test_health_endpoint),
        ("Infer endpoint (auth required)", test_infer_endpoint),
        ("Form metadata endpoint", test_form_metadata_endpoint),
        ("Chat message endpoint", test_chat_message_endpoint),
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n{test_name}:")
        try:
            result = test_func()
            results.append(result)
            print(f"Result: {'✓ PASS' if result else '✗ FAIL'}")
        except Exception as e:
            print(f"Test failed with exception: {e}")
            results.append(False)
    
    print("\n" + "=" * 50)
    print(f"Test Results: {sum(results)}/{len(results)} passed")
    
    if all(results):
        print("🎉 All tests passed!")
    else:
        print("⚠️  Some tests failed. Check the server logs.")

if __name__ == "__main__":
    main()
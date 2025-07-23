#!/usr/bin/env python3
"""
Quick test to verify API setup and OpenAI connectivity
"""

import os
import sys
import requests
import json

def test_openai_api():
    """Test OpenAI API connectivity"""
    api_key = os.getenv('OPENAI_API_KEY')
    
    if not api_key:
        print("❌ OPENAI_API_KEY not found in environment variables")
        print("Please set it with: export OPENAI_API_KEY='your-key-here'")
        return False
    
    print(f"✅ Found OpenAI API key: {api_key[:10]}...")
    
    # Test simple API call
    try:
        response = requests.post(
            'https://api.openai.com/v1/chat/completions',
            headers={
                'Authorization': f'Bearer {api_key}',
                'Content-Type': 'application/json'
            },
            json={
                'model': 'gpt-4o-mini',
                'messages': [{'role': 'user', 'content': 'Say "API test successful"'}],
                'max_tokens': 10
            },
            timeout=10
        )
        
        if response.status_code == 200:
            result = response.json()
            message = result['choices'][0]['message']['content']
            print(f"✅ OpenAI API working: {message}")
            return True
        else:
            print(f"❌ OpenAI API error: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ OpenAI API test failed: {e}")
        return False

def test_firebase_api():
    """Test Firebase Cloud Functions API"""
    api_url = 'https://us-central1-bermuda-01.cloudfunctions.net/api'
    
    try:
        # Test health endpoint
        response = requests.get(f"{api_url}/health", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Firebase API health: {data}")
            return True
        else:
            print(f"❌ Firebase API health check failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Firebase API test failed: {e}")
        return False

def test_form_access():
    """Test form access endpoint"""
    api_url = 'https://us-central1-bermuda-01.cloudfunctions.net/api'
    
    try:
        # Test coffee form access
        response = requests.get(f"{api_url}/forms/test-form-coffee", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Test form access: {data['title']}")
            return True
        else:
            print(f"❌ Test form access failed: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Form access test failed: {e}")
        return False

if __name__ == "__main__":
    print("🧪 Testing API setup and connectivity...")
    print("=" * 50)
    
    success = True
    
    if not test_openai_api():
        success = False
        
    if not test_firebase_api():
        success = False
        
    if not test_form_access():
        success = False
    
    print("=" * 50)
    if success:
        print("🎉 All API tests passed!")
    else:
        print("⚠️  Some API tests failed. Check the issues above.")
    
    sys.exit(0 if success else 1)
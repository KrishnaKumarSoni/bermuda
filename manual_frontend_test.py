#!/usr/bin/env python3
"""
Manual Frontend Test Script
Opens the production site and performs comprehensive frontend testing
"""

import webbrowser
import time
import requests
import json
from datetime import datetime

BASE_URL = "https://bermuda-01.web.app"

def log(message: str, test_type: str = "INFO"):
    timestamp = datetime.now().strftime("%H:%M:%S")
    print(f"[{timestamp}] {test_type}: {message}")

def test_frontend_manually():
    """Test frontend by opening browser and providing manual test steps"""
    
    log("🚀 Starting Manual Frontend Test - Production System")
    log(f"Target URL: {BASE_URL}")
    
    # Test 1: Open landing page
    log("Opening landing page in browser...")
    webbrowser.open(BASE_URL)
    
    print("\n" + "="*60)
    print("MANUAL FRONTEND TEST CHECKLIST")
    print("="*60)
    
    print("\n📋 LANDING PAGE TESTS:")
    print("1. ✅ Does the landing page load correctly?")
    print("2. ✅ Is the main heading 'Forms That Feel Like Conversations' visible?")
    print("3. ✅ Are the CTA buttons (orange color) present and clickable?")
    print("4. ✅ Is the demo chat interface showing on the right side?")
    print("5. ✅ Is the burnt orange (#CC5500) color scheme applied?")
    print("6. ✅ Are the custom fonts (Plus Jakarta Sans, Inter Tight) loading?")
    print("7. ✅ Is the page mobile-responsive (try resizing browser)?")
    
    input("\nPress Enter after checking Landing Page tests...")
    
    # Test 2: Navigate to app
    app_url = f"{BASE_URL}/app"
    log(f"Opening app interface: {app_url}")
    webbrowser.open(app_url)
    
    print("\n📋 APP INTERFACE TESTS:")
    print("1. ✅ Does the app interface load (may show auth or dashboard)?")
    print("2. ✅ Is there a 'Sign in with Google' button or 'Create New Form' button?")
    print("3. ✅ Can you click the auth/create button successfully?")
    print("4. ✅ Does clicking show a response (auth flow or form creation)?")
    
    input("\nPress Enter after checking App Interface tests...")
    
    # Test 3: Form creation workflow
    print("\n📋 FORM CREATION WORKFLOW TESTS:")
    print("1. ✅ If auth is bypassed, do you see a 'Create New Form' button?")
    print("2. ✅ Clicking 'Create New Form' shows text input area?")
    print("3. ✅ Try entering: 'Survey about coffee preferences: favorite type, brewing method, frequency'")
    print("4. ✅ Does character count update as you type?")
    print("5. ✅ Does 'Create Form' button become enabled with enough text?")
    print("6. ✅ Clicking 'Create Form' shows loading spinner?")
    print("7. ✅ After ~5-10 seconds, does form builder appear with generated questions?")
    print("8. ✅ Can you see a form title field and question cards?")
    print("9. ✅ Are there toggles, dropdowns, and edit options for questions?")
    print("10. ✅ Is there a demographics section with checkboxes?")
    
    input("\nPress Enter after checking Form Creation tests...")
    
    # Test 4: Chat interface
    form_url = f"{BASE_URL}/form/test-form-123"
    log(f"Opening form chat interface: {form_url}")
    webbrowser.open(form_url)
    
    print("\n📋 CHAT INTERFACE TESTS:")
    print("1. ✅ Does the form URL route correctly (may redirect to app)?")
    print("2. ✅ Is there a chat-like interface visible?")
    print("3. ✅ If it's the app page, check browser console for routing")
    print("4. ✅ Are there any visible chat elements or message inputs?")
    
    input("\nPress Enter after checking Chat Interface tests...")
    
    # Test 5: API Integration verification
    print("\n📋 API INTEGRATION VERIFICATION:")
    
    try:
        # Health check
        response = requests.get(f"{BASE_URL}/api/health", timeout=10)
        log(f"✅ API Health: {response.status_code} - {response.json()}")
        
        # Chat test
        chat_response = requests.post(f"{BASE_URL}/api/debug/test-chat", 
                                    json={"message": "Hello!"}, timeout=10)
        log(f"✅ Chat API: {chat_response.status_code}")
        if chat_response.status_code == 200:
            data = chat_response.json()
            log(f"   Bot response: {data.get('bot_response', '')[:100]}...")
        
        # Form metadata
        form_response = requests.get(f"{BASE_URL}/api/forms/test-form-123", timeout=10)
        log(f"✅ Form API: {form_response.status_code}")
        
    except Exception as e:
        log(f"❌ API test error: {e}", "ERROR")
    
    print("\n📋 CROSS-BROWSER TESTS (Optional):")
    print("1. ✅ Try opening in Safari/Firefox to test cross-browser compatibility")
    print("2. ✅ Test on mobile device or mobile browser mode")
    print("3. ✅ Check browser developer console for any JavaScript errors")
    
    print("\n" + "="*60)
    print("🏁 MANUAL FRONTEND TEST COMPLETE")
    print("="*60)
    
    # Performance check
    try:
        start_time = time.time()
        response = requests.get(BASE_URL, timeout=10)
        load_time = time.time() - start_time
        log(f"✅ Page load time: {load_time:.2f} seconds")
        log(f"✅ Page size: {len(response.content)} bytes")
    except Exception as e:
        log(f"❌ Performance test error: {e}", "ERROR")
    
    print(f"\n🌐 Production URLs:")
    print(f"   Landing Page: {BASE_URL}")
    print(f"   App Interface: {BASE_URL}/app") 
    print(f"   Dashboard: {BASE_URL}/dashboard")
    print(f"   Test Form: {BASE_URL}/form/test-form-123")
    print(f"   API Health: {BASE_URL}/api/health")
    
    print(f"\n🔧 Backend Status:")
    try:
        health = requests.get(f"{BASE_URL}/api/health").json()
        print(f"   Service: {health.get('service', 'unknown')}")
        print(f"   Status: {health.get('status', 'unknown')}")
        print(f"   OpenAI: {health.get('openai', 'unknown')}")
        print(f"   Active Sessions: {health.get('active_sessions', 0)}")
    except:
        print("   Unable to fetch backend status")

if __name__ == "__main__":
    test_frontend_manually()
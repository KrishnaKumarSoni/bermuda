#!/usr/bin/env python3
"""
Complete Frontend Testing - Production System
Combines API testing with browser verification instructions
"""

import requests
import json
import time
import webbrowser
from datetime import datetime

BASE_URL = "https://bermuda-01.web.app"

class CompleteFrontendTest:
    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.errors = []
        
    def log(self, message: str, test_type: str = "INFO"):
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"[{timestamp}] {test_type}: {message}")
        
    def assert_test(self, condition: bool, test_name: str, details: str = ""):
        if condition:
            self.passed += 1
            self.log(f"✅ PASS: {test_name}", "PASS")
        else:
            self.failed += 1
            error_msg = f"❌ FAIL: {test_name} - {details}"
            self.log(error_msg, "FAIL")
            self.errors.append(error_msg)

    def test_api_endpoints(self):
        """Test all API endpoints in production"""
        self.log("🔧 Testing Production API Endpoints")
        
        # Health check
        try:
            response = requests.get(f"{BASE_URL}/api/health", timeout=10)
            self.assert_test(
                response.status_code == 200,
                "API Health endpoint accessible",
                f"Status: {response.status_code}"
            )
            
            if response.status_code == 200:
                data = response.json()
                self.assert_test(
                    data.get("status") == "healthy",
                    "API reports healthy status",
                    f"Status: {data.get('status')}"
                )
                
                self.assert_test(
                    data.get("openai") == "configured",
                    "OpenAI integration configured",
                    f"OpenAI: {data.get('openai')}"
                )
        except Exception as e:
            self.assert_test(False, "API Health endpoint failed", str(e))
        
        # Form metadata
        try:
            response = requests.get(f"{BASE_URL}/api/forms/test-form-123", timeout=10)
            self.assert_test(
                response.status_code == 200,
                "Form metadata endpoint working",
                f"Status: {response.status_code}"
            )
        except Exception as e:
            self.assert_test(False, "Form metadata endpoint failed", str(e))
        
        # Chat functionality
        try:
            response = requests.post(f"{BASE_URL}/api/debug/test-chat", 
                json={"message": "Hello, I want to take the survey"}, timeout=15)
            self.assert_test(
                response.status_code == 200,
                "Chat endpoint functional",
                f"Status: {response.status_code}"
            )
            
            if response.status_code == 200:
                data = response.json()
                bot_response = data.get("bot_response", "")
                self.assert_test(
                    len(bot_response) > 10,
                    "Chat generates meaningful responses",
                    f"Response length: {len(bot_response)}"
                )
        except Exception as e:
            self.assert_test(False, "Chat endpoint failed", str(e))
        
        # Data extraction
        try:
            test_data = {
                "session_id": "test-session",
                "transcript": [
                    {"role": "assistant", "text": "What's your favorite coffee?"},
                    {"role": "user", "text": "I love espresso"}
                ],
                "questions_json": {
                    "questions": [{"text": "What's your favorite coffee?", "type": "text"}]
                }
            }
            response = requests.post(f"{BASE_URL}/api/extract", json=test_data, timeout=10)
            self.assert_test(
                response.status_code == 200,
                "Data extraction endpoint working",
                f"Status: {response.status_code}"
            )
        except Exception as e:
            self.assert_test(False, "Data extraction endpoint failed", str(e))

    def open_frontend_for_verification(self):
        """Open frontend in browser for manual verification"""
        self.log("🌐 Opening Frontend for Manual Verification")
        
        # Landing page
        self.log("Opening landing page...")
        webbrowser.open(BASE_URL)
        time.sleep(1)
        
        # App interface
        self.log("Opening app interface...")
        webbrowser.open(f"{BASE_URL}/app")
        time.sleep(1)
        
        # Form interface
        self.log("Opening form interface...")
        webbrowser.open(f"{BASE_URL}/form/test-form-123")
        
        print("\n" + "="*60)
        print("MANUAL FRONTEND VERIFICATION CHECKLIST")
        print("="*60)
        print("Please verify the following in your browser:")
        print()
        print("📋 LANDING PAGE (first tab):")
        print("  ✅ Page loads without errors")
        print("  ✅ Main heading 'Forms That Feel Like Conversations' is visible")
        print("  ✅ Orange CTA buttons are present and styled correctly")
        print("  ✅ Demo chat interface is showing on the right")
        print("  ✅ Burnt orange color scheme (#CC5500) is applied")
        print("  ✅ Custom fonts are loading properly")
        print()
        print("📋 APP INTERFACE (second tab):")
        print("  ✅ App page loads (may show auth or main interface)")
        print("  ✅ 'Sign in with Google' or 'Create New Form' button visible")
        print("  ✅ Interface is responsive and styled correctly")
        print("  ✅ No JavaScript errors in browser console")
        print()
        print("📋 FORM INTERFACE (third tab):")
        print("  ✅ Form URL routes correctly (may redirect to app)")
        print("  ✅ Chat-like interface elements are present")
        print("  ✅ No routing errors or 404 pages")
        print("  ✅ Firebase configuration loads properly")
        print()
        print("🔧 TECHNICAL VERIFICATION:")
        print("  ✅ Open browser console (F12) - check for errors")
        print("  ✅ Network tab shows successful resource loading")
        print("  ✅ All CSS and JS files load without 404s")
        print("  ✅ Firebase services initialize correctly")
        print("="*60)

    def test_performance(self):
        """Test performance metrics"""
        self.log("⚡ Testing Performance Metrics")
        
        try:
            start_time = time.time()
            response = requests.get(BASE_URL, timeout=30)
            load_time = time.time() - start_time
            
            self.assert_test(
                response.status_code == 200,
                "Landing page loads successfully",
                f"Status: {response.status_code}"
            )
            
            self.assert_test(
                load_time < 5.0,
                "Landing page loads in reasonable time",
                f"Load time: {load_time:.2f} seconds"
            )
            
            self.assert_test(
                len(response.content) > 1000,
                "Landing page has substantial content",
                f"Content size: {len(response.content)} bytes"
            )
            
        except Exception as e:
            self.assert_test(False, "Performance test failed", str(e))

    def run_complete_test(self):
        """Run complete frontend and backend testing"""
        self.log("🚀 Starting Complete Frontend + Backend Testing")
        self.log(f"Target URL: {BASE_URL}")
        
        start_time = time.time()
        
        # Run automated tests
        self.test_api_endpoints()
        self.test_performance()
        
        # Open browser for manual verification
        self.open_frontend_for_verification()
        
        end_time = time.time()
        total_time = end_time - start_time
        
        # Print summary
        print("\n" + "="*60)
        self.log("🏁 COMPLETE TEST SUITE SUMMARY")
        self.log(f"⏱️  Automated test time: {total_time:.2f} seconds")
        self.log(f"✅ Automated tests passed: {self.passed}")
        self.log(f"❌ Automated tests failed: {self.failed}")
        
        if self.failed == 0:
            self.log("🎉 All automated tests PASSED!")
        else:
            self.log(f"⚠️  {self.failed} automated tests failed")
            
        self.log("📊 Frontend verification requires manual review in browser")
        self.log("🌐 Three browser tabs opened for manual verification")
        
        if self.failed > 0:
            self.log("🔍 FAILED TESTS:")
            for error in self.errors:
                self.log(f"   {error}")
                
        print("="*60)
        return self.passed, self.failed

if __name__ == "__main__":
    test_suite = CompleteFrontendTest()
    passed, failed = test_suite.run_complete_test()
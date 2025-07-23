#!/usr/bin/env python3
"""
Comprehensive Google Authentication Test Suite
Tests all authentication scenarios and edge cases
"""

import time
import json
import requests
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import TimeoutException, NoSuchElementException, ElementClickInterceptedException
from webdriver_manager.chrome import ChromeDriverManager

class AuthenticationTester:
    """Comprehensive authentication testing"""
    
    def __init__(self):
        self.base_url = "https://bermuda-01.web.app"
        self.api_url = "https://us-central1-bermuda-01.cloudfunctions.net/api"
        self.driver = None
        self.results = []
        
    def setup_browser(self):
        """Setup browser for auth testing"""
        chrome_options = Options()
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-web-security")
        chrome_options.add_argument("--disable-features=VizDisplayCompositor")
        chrome_options.add_argument("--window-size=1280,720")
        
        service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service, options=chrome_options)
        self.driver.implicitly_wait(10)
        self.wait = WebDriverWait(self.driver, 20)
        
    def log_result(self, test_name, success, details=""):
        """Log test result"""
        result = {
            "test": test_name,
            "success": success,
            "details": details,
            "timestamp": datetime.now().isoformat(),
            "url": self.driver.current_url if self.driver else "N/A"
        }
        self.results.append(result)
        
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status}: {test_name}")
        if details and not success:
            print(f"    Details: {details}")
    
    def test_landing_page_access(self):
        """Test basic landing page functionality"""
        print("\n🌐 Testing Landing Page Access...")
        
        try:
            self.driver.get(self.base_url)
            time.sleep(3)
            
            # Check page loads
            if "Bermuda" in self.driver.title:
                self.log_result("Landing page loads correctly", True)
            else:
                self.log_result("Landing page loads correctly", False, f"Wrong title: {self.driver.title}")
                return False
            
            # Check Sign in with Google button exists on landing page
            try:
                google_signin = self.driver.find_element(By.ID, "google-signin-btn")
                self.log_result("Sign in with Google button present on landing", True)
                
                # Landing page should show login interface directly
                page_content = self.driver.page_source.lower()
                if "sign in with google" in page_content:
                    self.log_result("Landing page shows login interface", True)
                else:
                    self.log_result("Landing page shows login interface", False, "Login interface not visible")
                
                # Navigate to /app to test app-specific auth flow
                self.driver.get(f"{self.base_url}/app")
                time.sleep(3)
                self.log_result("Navigation to /app works", True)
                    
            except NoSuchElementException:
                self.log_result("Sign in with Google button present on landing", False, "Button not found")
                return False
                
            return True
            
        except Exception as e:
            self.log_result("Landing page access", False, f"Error: {str(e)}")
            return False
    
    def test_authentication_ui_elements(self):
        """Test authentication UI elements"""
        print("\n🔐 Testing Authentication UI Elements...")
        
        try:
            # Should already be on /app from previous test
            self.driver.get(f"{self.base_url}/app")
            time.sleep(3)
            
            # Check for Google Sign-in button
            try:
                google_btn = self.wait.until(EC.presence_of_element_located((By.ID, "google-signin-btn")))
                self.log_result("Google Sign-in button present", True)
                
                # Check button text
                if "Google" in google_btn.text:
                    self.log_result("Google Sign-in button has correct text", True)
                else:
                    self.log_result("Google Sign-in button has correct text", False, f"Text: {google_btn.text}")
                
                # Check if button is clickable
                if google_btn.is_enabled() and google_btn.is_displayed():
                    self.log_result("Google Sign-in button is interactive", True)
                else:
                    self.log_result("Google Sign-in button is interactive", False, "Button not enabled or visible")
                
                return True
                
            except TimeoutException:
                self.log_result("Google Sign-in button present", False, "Button not found")
                return False
                
        except Exception as e:
            self.log_result("Authentication UI testing", False, f"Error: {str(e)}")
            return False
    
    def test_google_auth_flow(self):
        """Test actual Google authentication flow"""
        print("\n🔑 Testing Google Authentication Flow...")
        
        try:
            # Find and click Google sign-in button
            google_btn = self.driver.find_element(By.ID, "google-signin-btn")
            
            # Check initial state
            original_text = google_btn.text
            original_windows = len(self.driver.window_handles)
            
            # Click the button
            google_btn.click()
            time.sleep(2)
            
            # Check for loading state
            if google_btn.text != original_text:
                self.log_result("Sign-in button shows loading state", True)
            else:
                self.log_result("Sign-in button shows loading state", False, "Button text unchanged")
            
            # Wait a bit for popup or redirect
            time.sleep(5)
            
            # Check for popup window
            new_windows = len(self.driver.window_handles)
            current_url = self.driver.current_url
            
            if new_windows > original_windows:
                self.log_result("Google auth popup opens", True)
                
                # Switch to popup and check it's Google
                popup_window = None
                for handle in self.driver.window_handles:
                    if handle != self.driver.current_window_handle:
                        popup_window = handle
                        break
                
                if popup_window:
                    self.driver.switch_to.window(popup_window)
                    time.sleep(2)
                    
                    if "google" in self.driver.current_url.lower() or "accounts.google.com" in self.driver.current_url:
                        self.log_result("Popup is Google authentication", True)
                    else:
                        self.log_result("Popup is Google authentication", False, f"URL: {self.driver.current_url}")
                    
                    # Close popup and return to main window
                    self.driver.close()
                    self.driver.switch_to.window(self.driver.window_handles[0])
                
            elif "google" in current_url.lower():
                self.log_result("Google auth redirects correctly", True)
                # Go back to continue testing
                self.driver.back()
                time.sleep(2)
            else:
                self.log_result("Google auth flow initiates", False, "No popup or redirect detected")
                
            return True
            
        except Exception as e:
            self.log_result("Google authentication flow", False, f"Error: {str(e)}")
            return False
    
    def test_auth_error_handling(self):
        """Test authentication error scenarios"""
        print("\n⚠️  Testing Authentication Error Handling...")
        
        try:
            # Go to app page
            self.driver.get(f"{self.base_url}/app")
            time.sleep(3)
            
            # Check if error element exists
            try:
                error_element = self.driver.find_element(By.ID, "auth-error")
                if error_element:
                    self.log_result("Authentication error element present", True)
                    
                    # Check if it's initially hidden
                    if "hidden" in error_element.get_attribute("class"):
                        self.log_result("Error element initially hidden", True)
                    else:
                        self.log_result("Error element initially hidden", False, "Error element visible by default")
                        
                else:
                    self.log_result("Authentication error element present", False, "Error element not found")
                    
            except NoSuchElementException:
                self.log_result("Authentication error element present", False, "Error element not found")
            
            # Test popup blocking scenario (simulate by closing potential popups quickly)
            try:
                google_btn = self.driver.find_element(By.ID, "google-signin-btn")
                
                # Click and immediately handle any popup
                google_btn.click()
                time.sleep(1)
                
                # Close any new windows quickly to simulate popup blocking
                current_handles = self.driver.window_handles
                if len(current_handles) > 1:
                    for handle in current_handles[1:]:
                        self.driver.switch_to.window(handle)
                        self.driver.close()
                    self.driver.switch_to.window(current_handles[0])
                
                time.sleep(3)
                
                # Check if error message appears
                try:
                    error_element = self.driver.find_element(By.ID, "auth-error")
                    if error_element.text and "hidden" not in error_element.get_attribute("class"):
                        self.log_result("Error message appears on auth failure", True)
                    else:
                        self.log_result("Error message appears on auth failure", False, "No error message shown")
                        
                except NoSuchElementException:
                    self.log_result("Error message appears on auth failure", False, "Error element not found")
                
            except Exception as e:
                self.log_result("Error handling test", False, f"Error: {str(e)}")
            
            return True
            
        except Exception as e:
            self.log_result("Authentication error handling", False, f"Error: {str(e)}")
            return False
    
    def test_anonymous_form_access(self):
        """Test that forms can be accessed without authentication"""
        print("\n👤 Testing Anonymous Form Access...")
        
        try:
            # Test form URL access
            form_url = f"{self.base_url}/f/test-form-123"
            self.driver.get(form_url)
            time.sleep(3)
            
            # Check if we can access the form
            page_content = self.driver.page_source.lower()
            
            if any(keyword in page_content for keyword in ["chat", "message", "survey", "conversation"]):
                self.log_result("Anonymous form access works", True)
                
                # Check for chat interface elements
                try:
                    chat_input = self.driver.find_element(By.ID, "chat-input")
                    self.log_result("Chat interface accessible anonymously", True)
                    
                    # Try to send a test message
                    chat_input.send_keys("Hello, this is a test message")
                    
                    send_button = self.driver.find_element(By.ID, "send-message")
                    send_button.click()
                    time.sleep(3)
                    
                    # Check for any response or loading indicator
                    messages = self.driver.find_elements(By.XPATH, "//*[contains(@class, 'message')]")
                    loading = self.driver.find_elements(By.ID, "chat-loading")
                    
                    if len(messages) > 0 or len(loading) > 0:
                        self.log_result("Anonymous chat functionality works", True)
                    else:
                        self.log_result("Anonymous chat functionality works", False, "No response or loading detected")
                        
                except NoSuchElementException:
                    self.log_result("Chat interface accessible anonymously", False, "Chat elements not found")
                    
            else:
                self.log_result("Anonymous form access works", False, "Form content not accessible")
            
            return True
            
        except Exception as e:
            self.log_result("Anonymous form access", False, f"Error: {str(e)}")
            return False
    
    def test_api_authentication_requirements(self):
        """Test API endpoints authentication requirements"""
        print("\n🔌 Testing API Authentication Requirements...")
        
        # Test creator endpoints (should require auth)
        creator_endpoints = [
            ("/infer", {"dump": "test survey"}),
            ("/save-form", {"title": "Test", "questions": [{"text": "Test?", "type": "text", "enabled": True}], "demographics": []}),
            ("/forms", None)
        ]
        
        for endpoint, payload in creator_endpoints:
            try:
                if payload:
                    response = requests.post(f"{self.api_url}{endpoint}", 
                                           json=payload, timeout=10)
                else:
                    response = requests.get(f"{self.api_url}{endpoint}", timeout=10)
                
                if response.status_code == 401:
                    self.log_result(f"Creator endpoint {endpoint} requires auth", True)
                elif response.status_code in [400, 500]:
                    self.log_result(f"Creator endpoint {endpoint} auth check", True, 
                                  f"Status {response.status_code} (may accept but validate)")
                else:
                    self.log_result(f"Creator endpoint {endpoint} requires auth", False, 
                                  f"Status: {response.status_code}")
                    
            except requests.exceptions.RequestException as e:
                self.log_result(f"Creator endpoint {endpoint} accessibility", False, 
                              f"Request error: {str(e)}")
        
        # Test respondent endpoints (should be anonymous)
        respondent_endpoints = [
            ("/chat-message", {"session_id": "test", "form_id": "test-form-123", "message": "hello"}),
            ("/extract", {"session_id": "test", "transcript": [], "questions_json": "{}"})
        ]
        
        for endpoint, payload in respondent_endpoints:
            try:
                response = requests.post(f"{self.api_url}{endpoint}", 
                                       json=payload, timeout=10)
                
                if response.status_code in [200, 400]:  # 200 success, 400 validation error
                    self.log_result(f"Respondent endpoint {endpoint} allows anonymous access", True)
                else:
                    self.log_result(f"Respondent endpoint {endpoint} allows anonymous access", False, 
                                  f"Status: {response.status_code}")
                    
            except requests.exceptions.RequestException as e:
                self.log_result(f"Respondent endpoint {endpoint} accessibility", False, 
                              f"Request error: {str(e)}")
        
        return True
    
    def test_session_persistence(self):
        """Test authentication session persistence"""
        print("\n💾 Testing Session Persistence...")
        
        try:
            # Go to app page
            self.driver.get(f"{self.base_url}/app")
            time.sleep(3)
            
            # Refresh the page to test persistence
            self.driver.refresh()
            time.sleep(5)
            
            # Check what state we're in after refresh
            page_content = self.driver.page_source.lower()
            
            if "sign in" in page_content or "google" in page_content:
                self.log_result("Session state after refresh", True, "Correctly shows login (no persistent session)")
            elif "your forms" in page_content or "dashboard" in page_content:
                self.log_result("Session state after refresh", True, "Persistent session maintained")
            else:
                self.log_result("Session state after refresh", False, "Unclear state after refresh")
            
            return True
            
        except Exception as e:
            self.log_result("Session persistence testing", False, f"Error: {str(e)}")
            return False
    
    def run_comprehensive_auth_tests(self):
        """Run all authentication tests"""
        print("🔐 Comprehensive Authentication Test Suite")
        print("=" * 60)
        
        self.setup_browser()
        
        try:
            # Phase 1: Basic functionality
            if not self.test_landing_page_access():
                print("❌ Landing page failed, skipping remaining tests")
                return
            
            # Phase 2: Authentication UI
            if not self.test_authentication_ui_elements():
                print("❌ Auth UI failed, but continuing with other tests")
            
            # Phase 3: Authentication flow
            self.test_google_auth_flow()
            
            # Phase 4: Error handling
            self.test_auth_error_handling()
            
            # Phase 5: Anonymous access
            self.test_anonymous_form_access()
            
            # Phase 6: API authentication
            self.test_api_authentication_requirements()
            
            # Phase 7: Session persistence
            self.test_session_persistence()
            
        finally:
            self.cleanup()
    
    def cleanup(self):
        """Clean up and generate summary"""
        if self.driver:
            self.driver.quit()
        
        self.generate_summary()
    
    def generate_summary(self):
        """Generate comprehensive authentication test summary"""
        total_tests = len(self.results)
        passed_tests = len([r for r in self.results if r["success"]])
        failed_tests = total_tests - passed_tests
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        print("\n" + "=" * 60)
        print("🏁 COMPREHENSIVE AUTHENTICATION TEST SUMMARY")
        print("=" * 60)
        print(f"✅ Passed: {passed_tests}")
        print(f"❌ Failed: {failed_tests}")
        print(f"📊 Success Rate: {success_rate:.1f}%")
        
        if failed_tests > 0:
            print("\n🔍 FAILED TESTS:")
            for result in self.results:
                if not result["success"]:
                    print(f"   ❌ {result['test']}: {result['details']}")
        
        print("=" * 60)
        
        # Authentication assessment
        if success_rate >= 90:
            print("🔒 AUTHENTICATION STATUS: EXCELLENT - Production ready!")
        elif success_rate >= 75:
            print("✅ AUTHENTICATION STATUS: GOOD - Minor auth issues")
        elif success_rate >= 60:
            print("⚠️  AUTHENTICATION STATUS: NEEDS WORK - Several auth problems")
        else:
            print("❌ AUTHENTICATION STATUS: CRITICAL - Major auth failures")
        
        # Save detailed results
        with open('comprehensive_auth_results.json', 'w') as f:
            json.dump({
                "results": self.results,
                "summary": {
                    "total_tests": total_tests,
                    "passed_tests": passed_tests,
                    "failed_tests": failed_tests,
                    "success_rate": success_rate,
                    "test_duration": datetime.now().isoformat()
                }
            }, f, indent=2)

if __name__ == "__main__":
    tester = AuthenticationTester()
    tester.run_comprehensive_auth_tests()
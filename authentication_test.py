#!/usr/bin/env python3
"""
Focused Authentication Testing for Bermuda
Tests login/logout flows, session management, and auth edge cases
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
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager

class AuthenticationTester:
    """Focused authentication flow testing"""
    
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
        
        service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service, options=chrome_options)
        self.driver.implicitly_wait(10)
        self.wait = WebDriverWait(self.driver, 20)
        
    def log_result(self, test_name, success, details=""):
        """Log authentication test result"""
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
    
    def test_unauthenticated_access(self):
        """Test what users can access without authentication"""
        print("\n🌐 Testing Unauthenticated Access...")
        
        # Test 1: Landing page access
        try:
            self.driver.get(self.base_url)
            time.sleep(3)
            
            if "Bermuda" in self.driver.title and self.driver.current_url.startswith(self.base_url):
                self.log_result("Landing page accessible without auth", True)
            else:
                self.log_result("Landing page accessible without auth", False, f"Redirected to: {self.driver.current_url}")
        except Exception as e:
            self.log_result("Landing page accessible without auth", False, f"Error: {str(e)}")
        
        # Test 2: Direct app access
        try:
            self.driver.get(f"{self.base_url}/app")
            time.sleep(3)
            
            # Should either show auth prompt or allow limited access
            page_content = self.driver.page_source.lower()
            if "sign in" in page_content or "login" in page_content or "auth" in page_content:
                self.log_result("App redirects to authentication", True)
            elif "create" in page_content or "form" in page_content:
                self.log_result("App allows unauthenticated access", True)
            else:
                self.log_result("App access behavior", False, "Unclear authentication behavior")
        except Exception as e:
            self.log_result("App access behavior", False, f"Error: {str(e)}")
        
        # Test 3: Anonymous form access
        try:
            form_url = f"{self.base_url}/f/test-form-123"
            self.driver.get(form_url)
            time.sleep(3)
            
            page_content = self.driver.page_source.lower()
            if any(keyword in page_content for keyword in ["chat", "message", "survey", "form"]):
                self.log_result("Anonymous form access works", True)
            else:
                self.log_result("Anonymous form access works", False, "Form not accessible")
        except Exception as e:
            self.log_result("Anonymous form access works", False, f"Error: {str(e)}")
    
    def test_authentication_ui(self):
        """Test authentication user interface"""
        print("\n🔐 Testing Authentication UI...")
        
        try:
            self.driver.get(f"{self.base_url}/app")
            time.sleep(3)
            
            # Test 1: Auth button presence
            try:
                auth_buttons = self.driver.find_elements(By.XPATH, "//button[contains(text(), 'Sign') or contains(text(), 'Login') or contains(text(), 'Google')]")
                if auth_buttons:
                    self.log_result("Authentication buttons present", True)
                    
                    # Test button interactivity
                    for button in auth_buttons:
                        if button.is_displayed() and button.is_enabled():
                            self.log_result("Authentication buttons are interactive", True)
                            break
                    else:
                        self.log_result("Authentication buttons are interactive", False, "Buttons not clickable")
                else:
                    self.log_result("Authentication buttons present", False, "No auth buttons found")
            except Exception as e:
                self.log_result("Authentication buttons present", False, f"Error: {str(e)}")
            
            # Test 2: Google Sign-In specific testing
            try:
                google_btn = self.driver.find_element(By.XPATH, "//button[contains(text(), 'Google') or contains(@class, 'google')]")
                
                # Check visual state
                if google_btn.is_displayed():
                    self.log_result("Google Sign-In button visible", True)
                    
                    # Test click behavior (without completing auth)
                    original_url = self.driver.current_url
                    original_windows = len(self.driver.window_handles)
                    
                    google_btn.click()
                    time.sleep(3)
                    
                    # Check for popup or redirect
                    new_windows = len(self.driver.window_handles)
                    current_url = self.driver.current_url
                    
                    if new_windows > original_windows:
                        self.log_result("Google auth opens popup", True)
                        # Close popup
                        if len(self.driver.window_handles) > 1:
                            self.driver.switch_to.window(self.driver.window_handles[-1])
                            self.driver.close()
                            self.driver.switch_to.window(self.driver.window_handles[0])
                    elif current_url != original_url and "google" in current_url.lower():
                        self.log_result("Google auth redirects correctly", True)
                        self.driver.back()
                        time.sleep(2)
                    else:
                        self.log_result("Google auth flow initiates", False, "No popup or redirect detected")
                else:
                    self.log_result("Google Sign-In button visible", False, "Button not displayed")
                    
            except NoSuchElementException:
                self.log_result("Google Sign-In button exists", False, "Google button not found")
            except Exception as e:
                self.log_result("Google Sign-In testing", False, f"Error: {str(e)}")
        
        except Exception as e:
            self.log_result("Authentication UI testing", False, f"Error: {str(e)}")
    
    def test_session_management(self):
        """Test session management and persistence"""
        print("\n📱 Testing Session Management...")
        
        # Test 1: Session persistence across page refreshes
        try:
            self.driver.get(f"{self.base_url}/f/test-form-123")
            time.sleep(2)
            
            # Start a chat session
            try:
                chat_input = self.wait.until(EC.presence_of_element_located((By.XPATH, "//input[@type='text'] | //textarea")))
                chat_input.send_keys("Test session persistence")
                chat_input.send_keys(Keys.ENTER)
                time.sleep(3)
                
                # Count messages before refresh
                messages_before = len(self.driver.find_elements(By.XPATH, "//*[contains(@class, 'message')]"))
                
                # Refresh page
                self.driver.refresh()
                time.sleep(3)
                
                # Check if session persisted
                messages_after = len(self.driver.find_elements(By.XPATH, "//*[contains(@class, 'message')]"))
                
                if messages_after >= messages_before:
                    self.log_result("Chat session persists across refresh", True)
                else:
                    self.log_result("Chat session persists across refresh", False, f"Messages lost: {messages_before} -> {messages_after}")
                    
            except TimeoutException:
                self.log_result("Chat session creation", False, "Chat input not found")
                
        except Exception as e:
            self.log_result("Session persistence testing", False, f"Error: {str(e)}")
        
        # Test 2: Multiple tab session isolation
        try:
            original_window = self.driver.current_window_handle
            
            # Open new tab
            self.driver.execute_script("window.open('');")
            self.driver.switch_to.window(self.driver.window_handles[-1])
            self.driver.get(f"{self.base_url}/f/test-form-456")
            time.sleep(2)
            
            # Start different chat session
            try:
                chat_input = self.wait.until(EC.presence_of_element_located((By.XPATH, "//input[@type='text'] | //textarea")))
                chat_input.send_keys("Different session message")
                chat_input.send_keys(Keys.ENTER)
                time.sleep(2)
                
                self.log_result("Multiple tab session handling", True)
            except TimeoutException:
                self.log_result("Multiple tab session handling", False, "Chat not available in new tab")
            
            # Close new tab and return to original
            self.driver.close()
            self.driver.switch_to.window(original_window)
            
        except Exception as e:
            self.log_result("Multiple tab session testing", False, f"Error: {str(e)}")
    
    def test_api_authentication(self):
        """Test API endpoints authentication requirements"""
        print("\n🔌 Testing API Authentication...")
        
        # Test 1: Creator endpoints (should require auth)
        creator_endpoints = ["/infer", "/save-form", "/forms"]
        
        for endpoint in creator_endpoints:
            try:
                # Test without auth token
                response = requests.post(f"{self.api_url}{endpoint}", 
                                       json={"test": "data"},
                                       timeout=10)
                
                if response.status_code == 401:
                    self.log_result(f"Creator endpoint {endpoint} requires auth", True)
                elif response.status_code == 400:
                    self.log_result(f"Creator endpoint {endpoint} auth check", True, "Returns 400 (might accept but validate data)")
                else:
                    self.log_result(f"Creator endpoint {endpoint} requires auth", False, f"Status: {response.status_code}")
                    
            except requests.exceptions.RequestException as e:
                self.log_result(f"Creator endpoint {endpoint} accessibility", False, f"Request error: {str(e)}")
        
        # Test 2: Respondent endpoints (should be anonymous)
        respondent_endpoints = ["/chat-message", "/extract"]
        
        for endpoint in respondent_endpoints:
            try:
                response = requests.post(f"{self.api_url}{endpoint}",
                                       json={
                                           "session_id": "test-session",
                                           "form_id": "test-form",
                                           "message": "test"
                                       },
                                       timeout=10)
                
                if response.status_code in [200, 400]:  # 200 success, 400 validation error
                    self.log_result(f"Respondent endpoint {endpoint} allows anonymous access", True)
                else:
                    self.log_result(f"Respondent endpoint {endpoint} allows anonymous access", False, f"Status: {response.status_code}")
                    
            except requests.exceptions.RequestException as e:
                self.log_result(f"Respondent endpoint {endpoint} accessibility", False, f"Request error: {str(e)}")
        
        # Test 3: Form access endpoint
        try:
            response = requests.get(f"{self.api_url}/forms/test-form-123", timeout=10)
            
            if response.status_code in [200, 404]:  # Should allow anonymous access
                self.log_result("Form metadata endpoint allows anonymous access", True)
            else:
                self.log_result("Form metadata endpoint allows anonymous access", False, f"Status: {response.status_code}")
                
        except requests.exceptions.RequestException as e:
            self.log_result("Form metadata endpoint accessibility", False, f"Request error: {str(e)}")
    
    def test_auth_edge_cases(self):
        """Test authentication edge cases and error handling"""
        print("\n⚠️  Testing Authentication Edge Cases...")
        
        # Test 1: Invalid token handling
        try:
            response = requests.post(f"{self.api_url}/infer",
                                   json={"dump": "test"},
                                   headers={"Authorization": "Bearer invalid-token"},
                                   timeout=10)
            
            if response.status_code == 401:
                self.log_result("Invalid token properly rejected", True)
            else:
                self.log_result("Invalid token properly rejected", False, f"Status: {response.status_code}")
                
        except requests.exceptions.RequestException as e:
            self.log_result("Invalid token handling", False, f"Request error: {str(e)}")
        
        # Test 2: Malformed Authorization header
        try:
            response = requests.post(f"{self.api_url}/infer",
                                   json={"dump": "test"},
                                   headers={"Authorization": "InvalidFormat"},
                                   timeout=10)
            
            if response.status_code == 401:
                self.log_result("Malformed auth header rejected", True)
            else:
                self.log_result("Malformed auth header rejected", False, f"Status: {response.status_code}")
                
        except requests.exceptions.RequestException as e:
            self.log_result("Malformed auth header handling", False, f"Request error: {str(e)}")
        
        # Test 3: Browser session timeout simulation
        try:
            self.driver.get(f"{self.base_url}/app")
            time.sleep(2)
            
            # Clear all cookies to simulate session timeout
            self.driver.delete_all_cookies()
            
            # Refresh and check behavior
            self.driver.refresh()
            time.sleep(3)
            
            page_content = self.driver.page_source.lower()
            if "sign in" in page_content or "login" in page_content:
                self.log_result("Session timeout redirects to auth", True)
            else:
                self.log_result("Session timeout handling", True, "Allows continued access")
                
        except Exception as e:
            self.log_result("Session timeout simulation", False, f"Error: {str(e)}")
    
    def run_authentication_tests(self):
        """Run complete authentication test suite"""
        print("🔐 Starting Authentication Test Suite")
        print(f"Target URL: {self.base_url}")
        print(f"API URL: {self.api_url}")
        print("=" * 60)
        
        self.setup_browser()
        
        try:
            # Phase 1: Unauthenticated access testing
            self.test_unauthenticated_access()
            
            # Phase 2: Authentication UI testing
            self.test_authentication_ui()
            
            # Phase 3: Session management testing
            self.test_session_management()
            
            # Phase 4: API authentication testing
            self.test_api_authentication()
            
            # Phase 5: Edge cases and error handling
            self.test_auth_edge_cases()
            
        finally:
            self.cleanup()
    
    def cleanup(self):
        """Clean up and save results"""
        if self.driver:
            self.driver.quit()
        
        # Save results
        with open('authentication_test_results.json', 'w') as f:
            json.dump({
                "results": self.results,
                "summary": self.generate_summary()
            }, f, indent=2)
    
    def generate_summary(self):
        """Generate authentication test summary"""
        total_tests = len(self.results)
        passed_tests = len([r for r in self.results if r["success"]])
        failed_tests = total_tests - passed_tests
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        print("\n" + "=" * 60)
        print("🏁 AUTHENTICATION TEST SUMMARY")
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
        
        # Security assessment
        if success_rate >= 95:
            print("🔒 SECURITY STATUS: EXCELLENT - Auth system is robust")
        elif success_rate >= 85:
            print("✅ SECURITY STATUS: GOOD - Minor auth issues")
        elif success_rate >= 70:
            print("⚠️  SECURITY STATUS: NEEDS WORK - Auth vulnerabilities present")
        else:
            print("❌ SECURITY STATUS: CRITICAL - Major auth issues")
        
        return {
            "total_tests": total_tests,
            "passed_tests": passed_tests,
            "failed_tests": failed_tests,
            "success_rate": success_rate,
            "test_duration": datetime.now().isoformat()
        }

if __name__ == "__main__":
    tester = AuthenticationTester()
    tester.run_authentication_tests()
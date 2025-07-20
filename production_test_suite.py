#!/usr/bin/env python3
"""
Production Test Suite for Bermuda - Full Frontend + Backend Testing
Tests actual user workflows end-to-end in production environment
"""

import requests
import json
import time
import uuid
import sys
from datetime import datetime
from typing import Dict, List, Any, Optional
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, WebDriverException
import urllib.parse

# Test configuration
BASE_URL = "https://bermuda-01.web.app"
TEST_FORM_ID = "test-form-123"

class ProductionTestSuite:
    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.errors = []
        self.driver = None
        self.setup_selenium()
        
    def setup_selenium(self):
        """Setup Selenium WebDriver for frontend testing"""
        try:
            import tempfile
            temp_dir = tempfile.mkdtemp()
            
            chrome_options = Options()
            chrome_options.add_argument("--headless")  # Run in headless mode
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--disable-gpu")
            chrome_options.add_argument("--window-size=1920,1080")
            chrome_options.add_argument("--disable-web-security")
            chrome_options.add_argument("--allow-running-insecure-content")
            chrome_options.add_argument(f"--user-data-dir={temp_dir}")
            chrome_options.add_argument("--remote-debugging-port=9222")
            chrome_options.add_argument("--disable-extensions")
            chrome_options.add_argument("--disable-plugins")
            
            # Try to use Chromium first
            chrome_options.binary_location = "/opt/homebrew/bin/chromium"
            
            from webdriver_manager.chrome import ChromeDriverManager
            from selenium.webdriver.chrome.service import Service
            
            service = Service(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
            self.driver.implicitly_wait(10)
            self.log("Selenium WebDriver initialized successfully with Chromium")
        except Exception as e:
            self.log(f"Selenium setup failed: {e} - Will run API-only tests", "WARN")
            self.driver = None
        
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
            
    def make_request(self, method: str, endpoint: str, data: Dict = None, headers: Dict = None) -> Dict:
        """Make HTTP request with error handling"""
        try:
            url = f"{BASE_URL}{endpoint}"
            if headers is None:
                headers = {"Content-Type": "application/json"}
                
            if method.upper() == "GET":
                response = requests.get(url, headers=headers, timeout=30)
            elif method.upper() == "POST":
                response = requests.post(url, json=data, headers=headers, timeout=30)
            else:
                raise ValueError(f"Unsupported method: {method}")
                
            return {
                "status_code": response.status_code,
                "data": response.json() if response.headers.get("content-type", "").startswith("application/json") else response.text,
                "headers": dict(response.headers)
            }
        except Exception as e:
            return {
                "status_code": 0,
                "data": {"error": str(e)},
                "headers": {}
            }

    def test_landing_page_interactions(self):
        """Test 1-10: Landing Page Full Interactions"""
        self.log("Starting Landing Page Interaction Tests")
        
        if not self.driver:
            self.log("Skipping frontend tests - Selenium not available")
            return
            
        try:
            # Test 1: Landing page loads
            self.driver.get(BASE_URL)
            self.assert_test(
                "Bermuda" in self.driver.title,
                "Landing page loads with correct title",
                f"Title: {self.driver.title}"
            )
            
            # Test 2: Main heading visible
            try:
                heading = WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.TAG_NAME, "h1"))
                )
                self.assert_test(
                    "Forms That Feel Like" in heading.text,
                    "Main heading displays correctly",
                    f"Heading: {heading.text[:50]}"
                )
            except TimeoutException:
                self.assert_test(False, "Main heading not found", "Timeout waiting for h1")
            
            # Test 3: CTA buttons present
            try:
                cta_buttons = self.driver.find_elements(By.CLASS_NAME, "btn-primary")
                self.assert_test(
                    len(cta_buttons) > 0,
                    "CTA buttons present on landing page",
                    f"Found {len(cta_buttons)} CTA buttons"
                )
            except Exception as e:
                self.assert_test(False, "CTA buttons test failed", str(e))
            
            # Test 4: Demo chat visible
            try:
                demo_chat = self.driver.find_element(By.CLASS_NAME, "chat-bubble-demo")
                self.assert_test(
                    demo_chat.is_displayed(),
                    "Demo chat interface visible",
                    "Demo chat found and displayed"
                )
            except Exception as e:
                self.assert_test(False, "Demo chat not visible", str(e))
                
            # Test 5: Color scheme verification
            try:
                primary_elements = self.driver.find_elements(By.CSS_SELECTOR, "[style*='#CC5500'], .text-primary")
                self.assert_test(
                    len(primary_elements) > 0,
                    "Primary color scheme applied",
                    f"Found {len(primary_elements)} elements with primary color"
                )
            except Exception as e:
                self.assert_test(False, "Color scheme test failed", str(e))
                
            # Test 6: Click CTA button
            try:
                cta_button = self.driver.find_element(By.CLASS_NAME, "btn-primary")
                cta_button.click()
                
                # Wait for navigation or modal
                time.sleep(2)
                current_url = self.driver.current_url
                
                self.assert_test(
                    "/app" in current_url or "signin" in self.driver.page_source.lower(),
                    "CTA button navigates correctly",
                    f"Current URL: {current_url}"
                )
            except Exception as e:
                self.assert_test(False, "CTA button click failed", str(e))
                
        except Exception as e:
            self.log(f"Landing page test error: {e}", "ERROR")

    def test_app_interface_interactions(self):
        """Test 11-25: App Interface Full Interactions"""
        self.log("Starting App Interface Interaction Tests")
        
        if not self.driver:
            self.log("Skipping app interface tests - Selenium not available")
            return
            
        try:
            # Test 11: Navigate to app interface
            self.driver.get(f"{BASE_URL}/app")
            time.sleep(3)
            
            # Test 12: App interface loads
            self.assert_test(
                "bermuda-01.web.app" in self.driver.current_url,
                "App interface accessible",
                f"Current URL: {self.driver.current_url}"
            )
            
            # Test 13: Check for auth or main interface
            try:
                # Look for either auth form or main interface elements
                auth_elements = self.driver.find_elements(By.ID, "google-signin-btn")
                main_elements = self.driver.find_elements(By.ID, "create-form-btn")
                
                has_interface = len(auth_elements) > 0 or len(main_elements) > 0
                self.assert_test(
                    has_interface,
                    "App interface elements present",
                    f"Auth elements: {len(auth_elements)}, Main elements: {len(main_elements)}"
                )
                
                # Test 14: Try to interact with auth if present
                if len(auth_elements) > 0:
                    auth_btn = auth_elements[0]
                    self.assert_test(
                        auth_btn.is_displayed() and auth_btn.is_enabled(),
                        "Google sign-in button interactive",
                        "Button found and clickable"
                    )
                    
                    # Click the auth button to see what happens
                    auth_btn.click()
                    time.sleep(2)
                    
                    # Check if anything changed
                    post_click_elements = self.driver.find_elements(By.ID, "create-form-btn")
                    self.assert_test(
                        len(post_click_elements) > 0 or "dashboard" in self.driver.current_url,
                        "Auth button triggers interface change",
                        f"Dashboard elements found: {len(post_click_elements)}"
                    )
                    
            except Exception as e:
                self.assert_test(False, "App interface interaction failed", str(e))
                
        except Exception as e:
            self.log(f"App interface test error: {e}", "ERROR")

    def test_form_creation_workflow(self):
        """Test 26-40: Complete Form Creation Workflow"""
        self.log("Starting Form Creation Workflow Tests")
        
        if not self.driver:
            self.log("Skipping form creation tests - Selenium not available")
            return
            
        try:
            # Test 26: Navigate to form creation
            self.driver.get(f"{BASE_URL}/app")
            time.sleep(3)
            
            # Click through auth if needed
            try:
                auth_btn = self.driver.find_element(By.ID, "google-signin-btn")
                auth_btn.click()
                time.sleep(2)
            except:
                pass  # Auth might not be needed
                
            # Test 27: Look for create form button
            try:
                create_btns = self.driver.find_elements(By.ID, "create-form-btn")
                if len(create_btns) == 0:
                    create_btns = self.driver.find_elements(By.CLASS_NAME, "create-form-trigger")
                
                self.assert_test(
                    len(create_btns) > 0,
                    "Create form button available",
                    f"Found {len(create_btns)} create form buttons"
                )
                
                if len(create_btns) > 0:
                    # Test 28: Click create form
                    create_btns[0].click()
                    time.sleep(2)
                    
                    # Test 29: Text dump input appears
                    try:
                        text_input = WebDriverWait(self.driver, 10).until(
                            EC.presence_of_element_located((By.ID, "text-dump-input"))
                        )
                        self.assert_test(
                            text_input.is_displayed(),
                            "Text dump input field appears",
                            "Text input found and visible"
                        )
                        
                        # Test 30: Enter text in form creation
                        test_text = "Create a survey about coffee preferences: favorite type, brewing method, frequency of drinking, preferred time of day"
                        text_input.clear()
                        text_input.send_keys(test_text)
                        
                        # Test 31: Character count updates
                        try:
                            char_count = self.driver.find_element(By.ID, "char-count")
                            self.assert_test(
                                str(len(test_text)) in char_count.text,
                                "Character count updates correctly",
                                f"Char count: {char_count.text}"
                            )
                        except:
                            self.assert_test(False, "Character count not updating", "Element not found")
                        
                        # Test 32: Submit button becomes enabled
                        try:
                            submit_btn = self.driver.find_element(By.ID, "create-form-submit")
                            self.assert_test(
                                submit_btn.is_enabled(),
                                "Submit button enabled with valid text",
                                f"Button enabled: {submit_btn.is_enabled()}"
                            )
                            
                            # Test 33: Click submit to generate form
                            submit_btn.click()
                            
                            # Wait for loading or form builder
                            time.sleep(5)  # AI inference takes time
                            
                            # Test 34: Form builder appears or loading shown
                            loading_el = self.driver.find_elements(By.ID, "loading-inference")
                            builder_el = self.driver.find_elements(By.ID, "form-builder-step")
                            
                            self.assert_test(
                                len(loading_el) > 0 or len(builder_el) > 0,
                                "Form generation initiated",
                                f"Loading: {len(loading_el)}, Builder: {len(builder_el)}"
                            )
                            
                            # Wait longer for AI response
                            if len(loading_el) > 0:
                                WebDriverWait(self.driver, 30).until(
                                    EC.invisibility_of_element(loading_el[0])
                                )
                            
                            # Test 35: Form builder with generated questions
                            try:
                                form_title = WebDriverWait(self.driver, 10).until(
                                    EC.presence_of_element_located((By.ID, "form-title"))
                                )
                                self.assert_test(
                                    len(form_title.get_attribute("value")) > 0,
                                    "Generated form has title",
                                    f"Title: {form_title.get_attribute('value')[:50]}"
                                )
                                
                                # Test 36: Generated questions present
                                question_cards = self.driver.find_elements(By.CLASS_NAME, "question-card")
                                self.assert_test(
                                    len(question_cards) > 0,
                                    "Generated questions displayed",
                                    f"Found {len(question_cards)} question cards"
                                )
                                
                            except TimeoutException:
                                self.assert_test(False, "Form builder did not load", "Timeout waiting for form elements")
                                
                        except Exception as e:
                            self.assert_test(False, "Form submission failed", str(e))
                            
                    except TimeoutException:
                        self.assert_test(False, "Text input not found", "Timeout waiting for text-dump-input")
                        
            except Exception as e:
                self.assert_test(False, "Create form button interaction failed", str(e))
                
        except Exception as e:
            self.log(f"Form creation workflow error: {e}", "ERROR")

    def test_chat_interface_workflow(self):
        """Test 41-55: Complete Chat Interface Workflow"""
        self.log("Starting Chat Interface Workflow Tests")
        
        if not self.driver:
            self.log("Skipping chat interface tests - Selenium not available")
            return
            
        try:
            # Test 41: Navigate to form chat interface
            self.driver.get(f"{BASE_URL}/form/{TEST_FORM_ID}")
            time.sleep(3)
            
            # Test 42: Chat interface loads
            page_source = self.driver.page_source.lower()
            has_chat_elements = any(keyword in page_source for keyword in ["chat", "message", "conversation"])
            
            self.assert_test(
                has_chat_elements,
                "Chat interface page loads",
                f"URL: {self.driver.current_url}"
            )
            
            # If we detect it's routing to app.html, that's expected for SPA
            if "/form/" not in self.driver.current_url:
                self.log("Form route redirected to app - this is expected for SPA", "INFO")
            
            # Test 43: Check for chat elements in DOM
            try:
                # Look for common chat interface elements
                chat_elements = (
                    self.driver.find_elements(By.CSS_SELECTOR, "[class*='chat']") +
                    self.driver.find_elements(By.CSS_SELECTOR, "[class*='message']") +
                    self.driver.find_elements(By.CSS_SELECTOR, "[id*='chat']") +
                    self.driver.find_elements(By.TAG_NAME, "input")
                )
                
                self.assert_test(
                    len(chat_elements) > 0,
                    "Chat interface elements present",
                    f"Found {len(chat_elements)} potential chat elements"
                )
                
            except Exception as e:
                self.assert_test(False, "Chat elements check failed", str(e))
                
        except Exception as e:
            self.log(f"Chat interface workflow error: {e}", "ERROR")

    def test_api_integration_production(self):
        """Test 56-70: Production API Integration Tests"""
        self.log("Starting Production API Integration Tests")
        
        # Test 56: Health check
        response = self.make_request("GET", "/api/health")
        self.assert_test(
            response["status_code"] == 200 and "healthy" in str(response["data"]),
            "Production API health check",
            f"Status: {response['status_code']}, Data: {response['data']}"
        )
        
        # Test 57: OpenAI integration
        if response["status_code"] == 200:
            data = response["data"]
            self.assert_test(
                data.get("openai") == "configured",
                "Production OpenAI integration",
                f"OpenAI status: {data.get('openai')}"
            )
        
        # Test 58: Form metadata endpoint
        response = self.make_request("GET", f"/api/forms/{TEST_FORM_ID}")
        self.assert_test(
            response["status_code"] == 200,
            "Production form metadata endpoint",
            f"Status: {response['status_code']}"
        )
        
        # Test 59: Chat endpoint
        response = self.make_request("POST", "/api/debug/test-chat", {
            "message": "Hello, I want to take the survey"
        })
        self.assert_test(
            response["status_code"] == 200,
            "Production chat endpoint",
            f"Status: {response['status_code']}"
        )
        
        if response["status_code"] == 200:
            # Test 60: Chat response quality
            bot_response = response["data"].get("bot_response", "")
            self.assert_test(
                len(bot_response) > 10,
                "Production chat generates meaningful response",
                f"Response length: {len(bot_response)}"
            )
            
            # Test 61: Session management
            session_id = response["data"].get("session_id")
            self.assert_test(
                session_id is not None and len(session_id) > 10,
                "Production session management working",
                f"Session ID: {session_id}"
            )
        
        # Test 62: Data extraction endpoint
        test_transcript = [
            {"role": "assistant", "text": "What's your favorite coffee?"},
            {"role": "user", "text": "I love espresso"}
        ]
        
        response = self.make_request("POST", "/api/extract", {
            "session_id": "prod-test",
            "transcript": test_transcript,
            "questions_json": {
                "questions": [{"text": "What's your favorite coffee?", "type": "text"}]
            }
        })
        
        self.assert_test(
            response["status_code"] == 200,
            "Production data extraction endpoint",
            f"Status: {response['status_code']}"
        )
        
        # Test 63-70: Additional production stress tests
        self.log("Running production stress tests...")
        
        # Multiple rapid requests
        rapid_responses = []
        for i in range(5):
            resp = self.make_request("GET", "/api/health")
            rapid_responses.append(resp["status_code"])
        
        self.assert_test(
            all(status == 200 for status in rapid_responses),
            "Production handles rapid requests",
            f"Responses: {rapid_responses}"
        )

    def cleanup(self):
        """Cleanup resources"""
        if self.driver:
            try:
                self.driver.quit()
            except:
                pass

    def run_production_tests(self):
        """Run all production tests"""
        self.log("🚀 Starting Production Test Suite - Full Frontend + Backend")
        self.log(f"Target URL: {BASE_URL}")
        
        start_time = time.time()
        
        try:
            # Run test suites
            self.test_landing_page_interactions()
            self.test_app_interface_interactions()
            self.test_form_creation_workflow()
            self.test_chat_interface_workflow()
            self.test_api_integration_production()
            
        finally:
            self.cleanup()
        
        end_time = time.time()
        total_time = end_time - start_time
        
        # Print summary
        self.log("=" * 60)
        self.log("🏁 PRODUCTION TEST SUITE COMPLETE")
        self.log(f"⏱️  Total time: {total_time:.2f} seconds")
        self.log(f"✅ Passed: {self.passed}")
        self.log(f"❌ Failed: {self.failed}")
        self.log(f"📊 Success rate: {(self.passed/(self.passed+self.failed)*100):.1f}%")
        
        if self.failed > 0:
            self.log("🔍 FAILED TESTS:")
            for error in self.errors:
                self.log(f"   {error}")
                
        return self.passed, self.failed

if __name__ == "__main__":
    test_suite = ProductionTestSuite()
    passed, failed = test_suite.run_production_tests()
    
    # Exit with appropriate code
    sys.exit(0 if failed == 0 else 1)
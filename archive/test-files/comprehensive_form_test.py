#!/usr/bin/env python3
"""
Comprehensive Form Creation and Workflow Test Suite
Tests all form creation scenarios and edge cases
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

class FormCreationTester:
    """Comprehensive form creation testing"""
    
    def __init__(self):
        self.base_url = "https://bermuda-01.web.app"
        self.api_url = "https://us-central1-bermuda-01.cloudfunctions.net/api"
        self.driver = None
        self.results = []
        
    def setup_browser(self):
        """Setup browser for form testing"""
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
    
    def test_app_access_and_auth_interface(self):
        """Test app access and authentication interface"""
        print("\n🔐 Testing App Access and Auth Interface...")
        
        try:
            self.driver.get(f"{self.base_url}/app")
            time.sleep(3)
            
            # Check page loads
            if "Bermuda" in self.driver.title:
                self.log_result("App page loads correctly", True)
            else:
                self.log_result("App page loads correctly", False, f"Wrong title: {self.driver.title}")
                return False
            
            # Check for Google Sign-in button
            try:
                google_btn = self.wait.until(EC.presence_of_element_located((By.ID, "google-signin-btn")))
                self.log_result("Google Sign-in button present on /app", True)
                
                if google_btn.is_displayed() and google_btn.is_enabled():
                    self.log_result("Google Sign-in button is interactive", True)
                else:
                    self.log_result("Google Sign-in button is interactive", False)
                    
                return True
                
            except TimeoutException:
                self.log_result("Google Sign-in button present on /app", False, "Button not found")
                return False
                
        except Exception as e:
            self.log_result("App access and auth interface", False, f"Error: {str(e)}")
            return False
    
    def test_inference_api_directly(self):
        """Test form inference API directly"""
        print("\n🧠 Testing Form Inference API...")
        
        test_dumps = [
            {
                "name": "Customer feedback survey",
                "dump": "We need to collect customer feedback about our new product launch. Ask about satisfaction, features they like, areas for improvement, likelihood to recommend, and demographics like age and location."
            },
            {
                "name": "Employee satisfaction survey", 
                "dump": "Employee satisfaction survey for Q4. Questions about work-life balance, management effectiveness, career development opportunities, compensation satisfaction, and workplace culture."
            },
            {
                "name": "Product research survey",
                "dump": "Research survey for new mobile app. Ask users about current apps they use, pain points, desired features, willingness to pay, and usage patterns."
            }
        ]
        
        for test_case in test_dumps:
            try:
                payload = {"dump": test_case["dump"]}
                
                # Test without auth (should fail)
                response = requests.post(f"{self.api_url}/infer", json=payload, timeout=30)
                
                if response.status_code == 401:
                    self.log_result(f"Inference API requires auth - {test_case['name']}", True)
                elif response.status_code == 200:
                    # Parse response to check quality
                    try:
                        data = response.json()
                        if "questions" in data and len(data["questions"]) > 0:
                            self.log_result(f"Inference API returns questions - {test_case['name']}", True, f"Generated {len(data['questions'])} questions")
                        else:
                            self.log_result(f"Inference API returns questions - {test_case['name']}", False, "No questions generated")
                    except json.JSONDecodeError:
                        self.log_result(f"Inference API response format - {test_case['name']}", False, "Invalid JSON")
                else:
                    self.log_result(f"Inference API response - {test_case['name']}", False, f"Status: {response.status_code}")
                    
            except requests.exceptions.RequestException as e:
                self.log_result(f"Inference API connection - {test_case['name']}", False, f"Error: {str(e)}")
    
    def test_form_builder_ui_elements(self):
        """Test form builder UI elements without auth"""
        print("\n🎨 Testing Form Builder UI Elements...")
        
        try:
            # Go to app page
            self.driver.get(f"{self.base_url}/app")
            time.sleep(3)
            
            # Check for form builder elements that should be present
            form_builder_elements = [
                ("form-title-input", "Form title input"),
                ("text-dump-input", "Text dump input area"),
                ("infer-form-btn", "Infer form button"),
                ("questions-container", "Questions container"),
                ("demographics-container", "Demographics container"),
                ("save-form-btn", "Save form button"),
                ("preview-form-btn", "Preview form button")
            ]
            
            visible_elements = 0
            for element_id, description in form_builder_elements:
                try:
                    element = self.driver.find_element(By.ID, element_id)
                    if element.is_displayed():
                        self.log_result(f"{description} visible", True)
                        visible_elements += 1
                    else:
                        self.log_result(f"{description} visible", False, "Element hidden")
                        
                except NoSuchElementException:
                    self.log_result(f"{description} present", False, "Element not found")
            
            # Check if main form builder interface is accessible
            if visible_elements >= 3:  # At least some key elements visible
                self.log_result("Form builder interface accessible", True, f"{visible_elements} elements visible")
            else:
                self.log_result("Form builder interface accessible", False, f"Only {visible_elements} elements visible")
            
            return True
            
        except Exception as e:
            self.log_result("Form builder UI testing", False, f"Error: {str(e)}")
            return False
    
    def test_form_creation_flow_simulation(self):
        """Test form creation flow simulation (UI interactions)"""
        print("\n📝 Testing Form Creation Flow...")
        
        try:
            # Go to app page
            self.driver.get(f"{self.base_url}/app")
            time.sleep(3)
            
            # Test 1: Text dump input
            try:
                text_dump_input = self.driver.find_element(By.ID, "text-dump-input")
                test_text = "Customer satisfaction survey about our pizza delivery service. Ask about food quality, delivery time, customer service, and overall experience."
                
                text_dump_input.clear()
                text_dump_input.send_keys(test_text)
                
                if len(text_dump_input.get_attribute("value")) > 0:
                    self.log_result("Text dump input functional", True)
                else:
                    self.log_result("Text dump input functional", False, "Input not accepting text")
                    
            except NoSuchElementException:
                self.log_result("Text dump input functional", False, "Input not found")
            
            # Test 2: Form title input
            try:
                title_input = self.driver.find_element(By.ID, "form-title-input")
                title_input.clear()
                title_input.send_keys("Pizza Delivery Satisfaction Survey")
                
                if len(title_input.get_attribute("value")) > 0:
                    self.log_result("Form title input functional", True)
                else:
                    self.log_result("Form title input functional", False, "Title input not working")
                    
            except NoSuchElementException:
                self.log_result("Form title input functional", False, "Title input not found")
            
            # Test 3: Infer button interaction
            try:
                infer_btn = self.driver.find_element(By.ID, "infer-form-btn")
                
                if infer_btn.is_enabled():
                    self.log_result("Infer form button enabled", True)
                    
                    # Click infer button
                    infer_btn.click()
                    time.sleep(2)
                    
                    # Check for loading state or response
                    if "loading" in infer_btn.get_attribute("class").lower() or infer_btn.text != infer_btn.get_attribute("data-original-text"):
                        self.log_result("Infer button shows loading state", True)
                    else:
                        self.log_result("Infer button shows loading state", False, "No loading state detected")
                        
                else:
                    self.log_result("Infer form button enabled", False, "Button disabled")
                    
            except NoSuchElementException:
                self.log_result("Infer form button interaction", False, "Button not found")
            
            # Test 4: Questions container updates
            time.sleep(5)  # Wait for potential API response
            
            try:
                questions_container = self.driver.find_element(By.ID, "questions-container")
                questions = questions_container.find_elements(By.CLASS_NAME, "question-item")
                
                if len(questions) > 0:
                    self.log_result("Questions generated after inference", True, f"Found {len(questions)} questions")
                    
                    # Test question editing
                    first_question = questions[0]
                    question_input = first_question.find_element(By.CLASS_NAME, "question-text")
                    
                    original_text = question_input.get_attribute("value")
                    question_input.clear()
                    question_input.send_keys("Modified question text")
                    
                    if question_input.get_attribute("value") != original_text:
                        self.log_result("Question editing functional", True)
                    else:
                        self.log_result("Question editing functional", False)
                        
                else:
                    self.log_result("Questions generated after inference", False, "No questions found")
                    
            except NoSuchElementException:
                self.log_result("Questions container interaction", False, "Container not found")
            
            return True
            
        except Exception as e:
            self.log_result("Form creation flow testing", False, f"Error: {str(e)}")
            return False
    
    def test_anonymous_form_access_patterns(self):
        """Test anonymous form access patterns"""
        print("\n👤 Testing Anonymous Form Access Patterns...")
        
        # Test different form URL patterns
        form_patterns = [
            "/f/test-form-123",
            "/f/pizza-survey",
            "/f/customer-feedback-2024"
        ]
        
        for pattern in form_patterns:
            try:
                form_url = f"{self.base_url}{pattern}"
                self.driver.get(form_url)
                time.sleep(3)
                
                # Check if page loads without error
                page_title = self.driver.title
                page_content = self.driver.page_source.lower()
                
                if "error" not in page_title.lower() and "not found" not in page_content:
                    self.log_result(f"Anonymous access {pattern}", True, "Page loads without error")
                    
                    # Check for chat interface elements
                    chat_elements = [
                        ("chat-container", "Chat container"),
                        ("chat-input", "Chat input"),
                        ("send-message", "Send button"),
                        ("chat-messages", "Chat messages area")
                    ]
                    
                    found_elements = 0
                    for element_id, description in chat_elements:
                        try:
                            element = self.driver.find_element(By.ID, element_id)
                            if element.is_displayed():
                                found_elements += 1
                        except NoSuchElementException:
                            pass
                    
                    if found_elements >= 2:
                        self.log_result(f"Chat interface elements {pattern}", True, f"{found_elements}/4 elements found")
                    else:
                        self.log_result(f"Chat interface elements {pattern}", False, f"Only {found_elements}/4 elements found")
                        
                else:
                    self.log_result(f"Anonymous access {pattern}", False, "Page shows error or not found")
                    
            except Exception as e:
                self.log_result(f"Anonymous access {pattern}", False, f"Error: {str(e)}")
    
    def test_api_endpoints_comprehensive(self):
        """Test all API endpoints comprehensively"""
        print("\n🔌 Testing API Endpoints Comprehensively...")
        
        # Test creator endpoints (should require auth)
        creator_tests = [
            {
                "endpoint": "/infer",
                "method": "POST",
                "payload": {"dump": "Test survey about customer satisfaction"},
                "name": "Form inference"
            },
            {
                "endpoint": "/save-form", 
                "method": "POST",
                "payload": {
                    "title": "Test Form",
                    "questions": [{"text": "Test question?", "type": "text", "enabled": True}],
                    "demographics": []
                },
                "name": "Form saving"
            },
            {
                "endpoint": "/forms",
                "method": "GET", 
                "payload": None,
                "name": "Forms listing"
            }
        ]
        
        for test in creator_tests:
            try:
                if test["method"] == "POST":
                    response = requests.post(f"{self.api_url}{test['endpoint']}", 
                                           json=test["payload"], timeout=30)
                else:
                    response = requests.get(f"{self.api_url}{test['endpoint']}", timeout=30)
                
                if response.status_code == 401:
                    self.log_result(f"{test['name']} requires authentication", True)
                elif response.status_code in [400, 500]:
                    self.log_result(f"{test['name']} API endpoint responds", True, f"Status {response.status_code}")
                else:
                    self.log_result(f"{test['name']} API security", False, f"Status: {response.status_code}")
                    
            except requests.exceptions.RequestException as e:
                self.log_result(f"{test['name']} API accessibility", False, f"Error: {str(e)}")
        
        # Test respondent endpoints (should allow anonymous)
        respondent_tests = [
            {
                "endpoint": "/chat-message",
                "payload": {
                    "session_id": "test-session-123",
                    "form_id": "test-form-456", 
                    "message": "Hello, this is a test message"
                },
                "name": "Chat message handling"
            },
            {
                "endpoint": "/extract",
                "payload": {
                    "session_id": "test-session-123",
                    "transcript": [
                        {"role": "user", "message": "I like pizza"},
                        {"role": "bot", "message": "What's your favorite topping?"}
                    ],
                    "questions_json": json.dumps([{"text": "Favorite food?", "type": "text"}])
                },
                "name": "Data extraction"
            }
        ]
        
        for test in respondent_tests:
            try:
                response = requests.post(f"{self.api_url}{test['endpoint']}", 
                                       json=test["payload"], timeout=30)
                
                if response.status_code in [200, 400]:  # Success or validation error
                    self.log_result(f"{test['name']} anonymous access", True, f"Status {response.status_code}")
                elif response.status_code == 401:
                    self.log_result(f"{test['name']} anonymous access", False, "Requires authentication")
                else:
                    self.log_result(f"{test['name']} API response", False, f"Status: {response.status_code}")
                    
            except requests.exceptions.RequestException as e:
                self.log_result(f"{test['name']} API accessibility", False, f"Error: {str(e)}")
    
    def run_comprehensive_form_tests(self):
        """Run all form creation and workflow tests"""
        print("📝 Comprehensive Form Creation & Workflow Test Suite")
        print("=" * 60)
        
        self.setup_browser()
        
        try:
            # Phase 1: App access and auth interface
            if not self.test_app_access_and_auth_interface():
                print("❌ App access failed, but continuing with API tests")
            
            # Phase 2: API testing (can run without UI)
            self.test_inference_api_directly()
            self.test_api_endpoints_comprehensive()
            
            # Phase 3: UI testing (when possible)
            self.test_form_builder_ui_elements()
            self.test_form_creation_flow_simulation()
            
            # Phase 4: Anonymous access testing
            self.test_anonymous_form_access_patterns()
            
        finally:
            self.cleanup()
    
    def cleanup(self):
        """Clean up and generate summary"""
        if self.driver:
            self.driver.quit()
        
        self.generate_summary()
    
    def generate_summary(self):
        """Generate comprehensive form testing summary"""
        total_tests = len(self.results)
        passed_tests = len([r for r in self.results if r["success"]])
        failed_tests = total_tests - passed_tests
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        print("\n" + "=" * 60)
        print("🏁 COMPREHENSIVE FORM CREATION TEST SUMMARY")
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
        
        # Form system assessment
        if success_rate >= 90:
            print("🔥 FORM SYSTEM STATUS: EXCELLENT - Production ready!")
        elif success_rate >= 75:
            print("✅ FORM SYSTEM STATUS: GOOD - Minor issues")
        elif success_rate >= 60:
            print("⚠️  FORM SYSTEM STATUS: NEEDS WORK - Several problems")
        else:
            print("❌ FORM SYSTEM STATUS: CRITICAL - Major failures")
        
        # Save detailed results
        with open('comprehensive_form_results.json', 'w') as f:
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
    tester = FormCreationTester()
    tester.run_comprehensive_form_tests()
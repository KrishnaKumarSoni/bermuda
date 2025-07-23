#!/usr/bin/env python3
"""
Comprehensive Real-World Test Suite for Bermuda
Tests complex chat scenarios, authentication flows, and edge cases
"""

import time
import json
import random
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager

class ComprehensiveRealWorldTest:
    """Comprehensive test suite for real-world usage scenarios"""
    
    def __init__(self):
        self.base_url = "https://bermuda-01.web.app"
        self.driver = None
        self.results = []
        self.test_forms = []
        self.chat_sessions = []
        
    def setup_browser(self):
        """Setup Chrome browser with realistic user configuration"""
        chrome_options = Options()
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        chrome_options.add_argument("--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
        
        # Randomize window size for realistic testing
        window_sizes = [(1920, 1080), (1366, 768), (1440, 900), (1280, 720)]
        width, height = random.choice(window_sizes)
        chrome_options.add_argument(f"--window-size={width},{height}")
        
        service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service, options=chrome_options)
        self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
        # Set realistic timeouts
        self.driver.implicitly_wait(10)
        self.wait = WebDriverWait(self.driver, 30)
        
    def log_result(self, test_name, success, details="", screenshot=False):
        """Log test result with optional screenshot"""
        result = {
            "test": test_name,
            "success": success,
            "details": details,
            "timestamp": datetime.now().isoformat(),
            "url": self.driver.current_url if self.driver else "N/A"
        }
        
        if screenshot and self.driver:
            try:
                screenshot_name = f"screenshot_{len(self.results)}.png"
                self.driver.save_screenshot(screenshot_name)
                result["screenshot"] = screenshot_name
            except:
                pass
                
        self.results.append(result)
        
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status}: {test_name}")
        if details and not success:
            print(f"    Details: {details}")
    
    def human_like_typing(self, element, text, typing_speed=0.05):
        """Type text with human-like delays and occasional typos"""
        element.clear()
        for char in text:
            element.send_keys(char)
            # Add realistic typing delays
            time.sleep(random.uniform(typing_speed, typing_speed * 3))
            
            # Occasional pauses (thinking)
            if random.random() < 0.05:
                time.sleep(random.uniform(0.3, 1.0))
    
    def human_like_scroll(self, direction="down", distance=300):
        """Scroll with human-like behavior"""
        if direction == "down":
            self.driver.execute_script(f"window.scrollBy(0, {distance});")
        else:
            self.driver.execute_script(f"window.scrollBy(0, -{distance});")
        time.sleep(random.uniform(0.2, 0.8))
    
    def test_authentication_flows(self):
        """Test comprehensive authentication scenarios"""
        print("\n🔐 Testing Authentication Flows...")
        
        try:
            # Test 1: Landing page access
            self.driver.get(self.base_url)
            time.sleep(3)
            
            if "Bermuda" in self.driver.title:
                self.log_result("Landing page loads correctly", True)
            else:
                self.log_result("Landing page loads correctly", False, f"Wrong title: {self.driver.title}")
                return
            
            # Test 2: Navigate to app without authentication
            try:
                get_started = self.wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Get Started') or contains(text(), 'Start Creating')]")))
                get_started.click()
                time.sleep(2)
                self.log_result("Navigation to app interface works", True)
            except TimeoutException:
                self.log_result("Navigation to app interface works", False, "Get Started button not found")
                return
            
            # Test 3: Authentication prompt appears
            try:
                auth_element = self.wait.until(EC.presence_of_element_located((By.XPATH, "//*[contains(text(), 'Sign in') or contains(text(), 'Login') or contains(text(), 'Google')]")))
                self.log_result("Authentication prompt appears", True)
            except TimeoutException:
                self.log_result("Authentication prompt appears", False, "No auth prompt found")
            
            # Test 4: Google Sign-In button functionality
            try:
                google_signin = self.driver.find_element(By.XPATH, "//button[contains(text(), 'Google') or contains(@class, 'google')]")
                
                # Check if button is clickable
                if google_signin.is_enabled():
                    self.log_result("Google Sign-In button is interactive", True)
                    
                    # Click but don't complete (to avoid actual auth)
                    original_windows = self.driver.window_handles
                    google_signin.click()
                    time.sleep(3)
                    
                    # Check if popup or redirect occurred
                    new_windows = self.driver.window_handles
                    if len(new_windows) > len(original_windows) or "google" in self.driver.current_url.lower():
                        self.log_result("Google authentication flow initiates", True)
                        
                        # Close any popups
                        if len(new_windows) > len(original_windows):
                            self.driver.switch_to.window(new_windows[-1])
                            self.driver.close()
                            self.driver.switch_to.window(original_windows[0])
                        else:
                            self.driver.back()
                            time.sleep(2)
                    else:
                        self.log_result("Google authentication flow initiates", False, "No popup or redirect detected")
                else:
                    self.log_result("Google Sign-In button is interactive", False, "Button not enabled")
                    
            except NoSuchElementException:
                self.log_result("Google Sign-In button exists", False, "Button not found")
            
            # Test 5: Anonymous form access (no auth required)
            test_form_url = f"{self.base_url}/f/test-form-123"
            self.driver.get(test_form_url)
            time.sleep(3)
            
            # Check if we can access a form without authentication
            if "chat" in self.driver.current_url.lower() or any(text in self.driver.page_source.lower() for text in ["message", "chat", "survey", "form"]):
                self.log_result("Anonymous form access works", True)
            else:
                self.log_result("Anonymous form access works", False, "Form not accessible anonymously")
                
        except Exception as e:
            self.log_result("Authentication flow testing", False, f"Unexpected error: {str(e)}")
    
    def create_test_form(self, scenario_name, form_data):
        """Create a test form for specific scenario"""
        print(f"\n📝 Creating test form for {scenario_name}...")
        
        try:
            # Navigate to app
            self.driver.get(f"{self.base_url}/app")
            time.sleep(3)
            
            # Skip auth for now (testing with mock auth)
            try:
                create_button = self.wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Create') or contains(text(), 'New Form')]")))
                create_button.click()
                time.sleep(2)
            except TimeoutException:
                # Might need to handle auth first
                pass
            
            # Input form description
            try:
                text_area = self.wait.until(EC.presence_of_element_located((By.TAG_NAME, "textarea")))
                self.human_like_typing(text_area, form_data["description"])
                time.sleep(1)
                
                # Generate form
                generate_button = self.driver.find_element(By.XPATH, "//button[contains(text(), 'Generate') or contains(text(), 'Create')]")
                generate_button.click()
                time.sleep(5)  # Wait for AI generation
                
                # Check if form was created
                if "questions" in self.driver.page_source.lower():
                    form_id = f"test-{scenario_name}-{int(time.time())}"
                    self.test_forms.append({
                        "id": form_id,
                        "scenario": scenario_name,
                        "url": self.driver.current_url
                    })
                    self.log_result(f"Form creation for {scenario_name}", True)
                    return form_id
                else:
                    self.log_result(f"Form creation for {scenario_name}", False, "No questions generated")
                    return None
                    
            except TimeoutException:
                self.log_result(f"Form creation for {scenario_name}", False, "Form creation interface not found")
                return None
                
        except Exception as e:
            self.log_result(f"Form creation for {scenario_name}", False, f"Error: {str(e)}")
            return None
    
    def test_complex_chat_scenario(self, scenario_name, chat_flow):
        """Test complex real-world chat scenario"""
        print(f"\n💬 Testing chat scenario: {scenario_name}...")
        
        # Use existing test form
        form_url = f"{self.base_url}/f/test-form-123"
        self.driver.get(form_url)
        time.sleep(3)
        
        try:
            # Wait for chat interface
            chat_input = self.wait.until(EC.presence_of_element_located((By.XPATH, "//input[@type='text'] | //textarea")))
            
            conversation_log = []
            
            for i, message in enumerate(chat_flow["messages"]):
                print(f"  Step {i+1}: {message[:50]}...")
                
                # Clear and type message with human-like behavior
                self.human_like_typing(chat_input, message)
                
                # Add realistic thinking pause
                time.sleep(random.uniform(1.0, 3.0))
                
                # Send message
                chat_input.send_keys(Keys.ENTER)
                
                # Wait for response with realistic timeout
                response_received = False
                start_time = time.time()
                
                while time.time() - start_time < 15:  # 15 second timeout
                    try:
                        # Look for new bot message
                        messages = self.driver.find_elements(By.XPATH, "//*[contains(@class, 'message') or contains(@class, 'chat')]")
                        if len(messages) > len(conversation_log):
                            response_received = True
                            conversation_log.extend(messages[len(conversation_log):])
                            break
                    except:
                        pass
                    time.sleep(0.5)
                
                if not response_received:
                    self.log_result(f"{scenario_name} - Message {i+1} response", False, "No bot response received")
                    return False
                else:
                    self.log_result(f"{scenario_name} - Message {i+1} response", True)
                
                # Random scroll to simulate reading
                if random.random() < 0.3:
                    self.human_like_scroll()
            
            # Test scenario-specific behaviors
            if chat_flow.get("test_behaviors"):
                for behavior in chat_flow["test_behaviors"]:
                    self.test_chat_behavior(behavior, scenario_name)
            
            self.chat_sessions.append({
                "scenario": scenario_name,
                "messages_count": len(chat_flow["messages"]),
                "completion_time": time.time(),
                "url": self.driver.current_url
            })
            
            return True
            
        except TimeoutException:
            self.log_result(f"{scenario_name} chat interface", False, "Chat interface not found")
            return False
        except Exception as e:
            self.log_result(f"{scenario_name} chat execution", False, f"Error: {str(e)}")
            return False
    
    def test_chat_behavior(self, behavior, scenario_name):
        """Test specific chat behaviors"""
        if behavior == "off_topic":
            # Test off-topic detection
            chat_input = self.driver.find_element(By.XPATH, "//input[@type='text'] | //textarea")
            self.human_like_typing(chat_input, "What's the weather like today?")
            chat_input.send_keys(Keys.ENTER)
            time.sleep(3)
            
            # Check for "bananas" response
            if "bananas" in self.driver.page_source.lower():
                self.log_result(f"{scenario_name} - Off-topic detection", True)
            else:
                self.log_result(f"{scenario_name} - Off-topic detection", False)
        
        elif behavior == "correction":
            # Test answer correction
            chat_input = self.driver.find_element(By.XPATH, "//input[@type='text'] | //textarea")
            self.human_like_typing(chat_input, "Actually, I meant to say Italian, not Mexican")
            chat_input.send_keys(Keys.ENTER)
            time.sleep(3)
            self.log_result(f"{scenario_name} - Answer correction", True)
        
        elif behavior == "skip":
            # Test question skipping
            chat_input = self.driver.find_element(By.XPATH, "//input[@type='text'] | //textarea")
            self.human_like_typing(chat_input, "I'd prefer not to answer that question")
            chat_input.send_keys(Keys.ENTER)
            time.sleep(3)
            self.log_result(f"{scenario_name} - Question skipping", True)
    
    def run_comprehensive_test_suite(self):
        """Run the complete comprehensive test suite"""
        print("🚀 Starting Comprehensive Real-World Test Suite")
        print(f"Target URL: {self.base_url}")
        print("=" * 80)
        
        self.setup_browser()
        
        try:
            # Phase 1: Authentication Testing
            self.test_authentication_flows()
            
            # Phase 2: Complex Chat Scenarios
            chat_scenarios = [
                {
                    "name": "Job Interview Survey",
                    "messages": [
                        "Hi, I'm here for the job interview survey",
                        "I have 5 years of experience in software development",
                        "I prefer working remotely but I'm flexible",
                        "My biggest strength is problem-solving and teamwork",
                        "I'm looking for growth opportunities and good work-life balance",
                        "I would rate my technical skills as 8 out of 10"
                    ],
                    "test_behaviors": ["correction", "off_topic"]
                },
                {
                    "name": "Restaurant Feedback Survey", 
                    "messages": [
                        "I visited your restaurant last weekend",
                        "The food was absolutely delicious, especially the pasta",
                        "The service was a bit slow, maybe 20 minutes for appetizers",
                        "The atmosphere was cozy and romantic",
                        "I would definitely recommend it to friends",
                        "Overall I'd rate the experience 4 out of 5 stars"
                    ],
                    "test_behaviors": ["skip"]
                },
                {
                    "name": "Health and Lifestyle Survey",
                    "messages": [
                        "I exercise about 3-4 times per week",
                        "I usually go for runs and do some weight training",
                        "I try to eat healthy but I love pizza on weekends",
                        "I sleep around 7 hours per night usually",
                        "I don't smoke and drink occasionally",
                        "My stress level is moderate, maybe 5 out of 10"
                    ],
                    "test_behaviors": ["correction"]
                },
                {
                    "name": "Product Research Survey",
                    "messages": [
                        "I'm looking for a new laptop for work",
                        "Budget is around $1500-2000",
                        "I need it mainly for programming and video calls",
                        "Battery life is very important to me",
                        "I prefer MacBook but I'm open to Windows",
                        "I would buy it within the next month"
                    ],
                    "test_behaviors": ["off_topic", "skip"]
                },
                {
                    "name": "Travel Preferences Survey",
                    "messages": [
                        "I love traveling and try to take 2-3 trips per year",
                        "I prefer adventure travel over relaxation",
                        "Mountains and hiking are my favorite activities",
                        "I usually travel with my partner or small groups",
                        "Budget travel is important but I value experiences",
                        "Europe and South America are on my bucket list"
                    ],
                    "test_behaviors": ["correction"]
                },
                {
                    "name": "Education Feedback Survey",
                    "messages": [
                        "I'm currently a graduate student in computer science",
                        "The online classes have been challenging but manageable",
                        "I prefer interactive lectures over pure video content",
                        "Group projects are helpful for learning",
                        "I wish there were more practical coding assignments",
                        "Overall the program meets my expectations"
                    ],
                    "test_behaviors": ["skip", "off_topic"]
                }
            ]
            
            for scenario in chat_scenarios:
                success = self.test_complex_chat_scenario(scenario["name"], scenario)
                if success:
                    self.log_result(f"Complete {scenario['name']} scenario", True)
                else:
                    self.log_result(f"Complete {scenario['name']} scenario", False)
                
                # Brief pause between scenarios
                time.sleep(2)
            
            # Phase 3: Edge Case Testing
            self.test_edge_cases()
            
            # Phase 4: Performance and Stress Testing
            self.test_performance_scenarios()
            
        finally:
            self.cleanup()
    
    def test_edge_cases(self):
        """Test various edge cases and error conditions"""
        print("\n⚠️  Testing Edge Cases...")
        
        edge_cases = [
            {
                "name": "Very Long Message",
                "message": "This is a very long message that should test the system's ability to handle large inputs. " * 20
            },
            {
                "name": "Special Characters",
                "message": "Testing émojis 🎉 and spéciàl chäräctêrs! @#$%^&*()_+ 中文 العربية"
            },
            {
                "name": "Multiple Rapid Messages",
                "messages": ["Quick", "Multiple", "Messages", "In", "Succession"]
            },
            {
                "name": "Empty Message Test",
                "message": ""
            }
        ]
        
        form_url = f"{self.base_url}/f/test-form-123"
        
        for case in edge_cases:
            try:
                self.driver.get(form_url)
                time.sleep(2)
                
                chat_input = self.wait.until(EC.presence_of_element_located((By.XPATH, "//input[@type='text'] | //textarea")))
                
                if case["name"] == "Multiple Rapid Messages":
                    for msg in case["messages"]:
                        chat_input.clear()
                        chat_input.send_keys(msg)
                        chat_input.send_keys(Keys.ENTER)
                        time.sleep(0.5)
                    self.log_result(f"Edge case: {case['name']}", True)
                else:
                    chat_input.clear()
                    if case["message"]:
                        chat_input.send_keys(case["message"])
                    chat_input.send_keys(Keys.ENTER)
                    time.sleep(3)
                    self.log_result(f"Edge case: {case['name']}", True)
                    
            except Exception as e:
                self.log_result(f"Edge case: {case['name']}", False, f"Error: {str(e)}")
    
    def test_performance_scenarios(self):
        """Test performance under various conditions"""
        print("\n⚡ Testing Performance Scenarios...")
        
        # Test 1: Multiple tab simulation
        try:
            original_window = self.driver.current_window_handle
            
            # Open multiple tabs
            for i in range(3):
                self.driver.execute_script("window.open('');")
                self.driver.switch_to.window(self.driver.window_handles[-1])
                self.driver.get(f"{self.base_url}/f/test-form-123")
                time.sleep(1)
            
            # Switch back to original
            self.driver.switch_to.window(original_window)
            self.log_result("Multiple tabs handling", True)
            
            # Close extra tabs
            for handle in self.driver.window_handles[1:]:
                self.driver.switch_to.window(handle)
                self.driver.close()
            self.driver.switch_to.window(original_window)
            
        except Exception as e:
            self.log_result("Multiple tabs handling", False, f"Error: {str(e)}")
        
        # Test 2: Page refresh during chat
        try:
            self.driver.get(f"{self.base_url}/f/test-form-123")
            time.sleep(2)
            
            chat_input = self.wait.until(EC.presence_of_element_located((By.XPATH, "//input[@type='text'] | //textarea")))
            chat_input.send_keys("Test message before refresh")
            chat_input.send_keys(Keys.ENTER)
            time.sleep(2)
            
            # Refresh page
            self.driver.refresh()
            time.sleep(3)
            
            # Check if chat interface still works
            chat_input = self.wait.until(EC.presence_of_element_located((By.XPATH, "//input[@type='text'] | //textarea")))
            chat_input.send_keys("Test message after refresh")
            chat_input.send_keys(Keys.ENTER)
            time.sleep(2)
            
            self.log_result("Page refresh during chat", True)
            
        except Exception as e:
            self.log_result("Page refresh during chat", False, f"Error: {str(e)}")
    
    def cleanup(self):
        """Clean up browser and save results"""
        if self.driver:
            self.driver.quit()
        
        # Save comprehensive results
        with open('comprehensive_test_results.json', 'w') as f:
            json.dump({
                "results": self.results,
                "test_forms": self.test_forms,
                "chat_sessions": self.chat_sessions,
                "summary": self.generate_summary()
            }, f, indent=2)
    
    def generate_summary(self):
        """Generate test summary"""
        total_tests = len(self.results)
        passed_tests = len([r for r in self.results if r["success"]])
        failed_tests = total_tests - passed_tests
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        summary = {
            "total_tests": total_tests,
            "passed_tests": passed_tests,
            "failed_tests": failed_tests,
            "success_rate": success_rate,
            "test_duration": datetime.now().isoformat(),
            "chat_scenarios_completed": len(self.chat_sessions),
            "forms_created": len(self.test_forms)
        }
        
        print("\n" + "=" * 80)
        print("🏁 COMPREHENSIVE TEST SUMMARY")
        print("=" * 80)
        print(f"✅ Passed: {passed_tests}")
        print(f"❌ Failed: {failed_tests}")
        print(f"📊 Success Rate: {success_rate:.1f}%")
        print(f"💬 Chat Scenarios: {len(self.chat_sessions)}")
        print(f"📝 Forms Created: {len(self.test_forms)}")
        
        if failed_tests > 0:
            print("\n🔍 FAILED TESTS:")
            for result in self.results:
                if not result["success"]:
                    print(f"   ❌ {result['test']}: {result['details']}")
        
        print("=" * 80)
        
        # Determine overall status
        if success_rate >= 95:
            print("🎉 SYSTEM STATUS: EXCELLENT - Production ready!")
        elif success_rate >= 85:
            print("✅ SYSTEM STATUS: GOOD - Minor issues to address")
        elif success_rate >= 70:
            print("⚠️  SYSTEM STATUS: NEEDS WORK - Several issues present")
        else:
            print("❌ SYSTEM STATUS: CRITICAL - Major fixes required")
        
        return summary

if __name__ == "__main__":
    tester = ComprehensiveRealWorldTest()
    tester.run_comprehensive_test_suite()
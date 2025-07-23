#!/usr/bin/env python3
"""
Complex Conversation Test - Real-world chat scenarios and edge cases
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
from selenium.common.exceptions import TimeoutException
from webdriver_manager.chrome import ChromeDriverManager

class ComplexConversationTester:
    """Test complex real-world conversation scenarios"""
    
    def __init__(self):
        self.base_url = "https://bermuda-01.web.app"
        self.form_url = f"{self.base_url}/f/test-form-123"
        self.driver = None
        self.results = []
        
    def setup_browser(self):
        """Setup browser for conversation testing"""
        chrome_options = Options()
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
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
            "timestamp": datetime.now().isoformat()
        }
        self.results.append(result)
        
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status}: {test_name}")
        if details and not success:
            print(f"    Details: {details}")
    
    def start_chat_session(self):
        """Start a new chat session"""
        try:
            self.driver.get(self.form_url)
            time.sleep(3)
            
            # Wait for chat interface to load
            chat_input = self.wait.until(EC.presence_of_element_located((By.ID, "chat-input")))
            return True
        except TimeoutException:
            self.log_result("Chat session initialization", False, "Chat interface not found")
            return False
    
    def send_message(self, message, expect_response=True):
        """Send a message and optionally wait for response"""
        try:
            chat_input = self.driver.find_element(By.ID, "chat-input")
            send_button = self.driver.find_element(By.ID, "send-message")
            
            # Clear and type message
            chat_input.clear()
            chat_input.send_keys(message)
            
            # Count messages before sending
            messages_before = len(self.driver.find_elements(By.XPATH, "//*[contains(@class, 'message') or contains(@class, 'chat')]"))
            
            # Send message
            send_button.click()
            
            if expect_response:
                # Wait for response (max 15 seconds)
                start_time = time.time()
                while time.time() - start_time < 15:
                    messages_after = len(self.driver.find_elements(By.XPATH, "//*[contains(@class, 'message') or contains(@class, 'chat')]"))
                    if messages_after > messages_before:
                        return True
                    time.sleep(0.5)
                return False
            return True
            
        except Exception as e:
            print(f"Error sending message: {str(e)}")
            return False
    
    def get_last_bot_response(self):
        """Get the last bot response text"""
        try:
            # Look for bot messages (assistant messages)
            bot_messages = self.driver.find_elements(By.XPATH, "//*[contains(@class, 'justify-start')]//p")
            if bot_messages:
                return bot_messages[-1].text
            return ""
        except:
            return ""
    
    def test_natural_conversation_flow(self):
        """Test natural conversation progression"""
        print("\n💬 Testing Natural Conversation Flow...")
        
        if not self.start_chat_session():
            return
        
        conversation_scenarios = [
            {
                "name": "Restaurant Experience Survey",
                "messages": [
                    "Hi, I'm here to share my restaurant experience",
                    "We went to Mario's Italian Restaurant last Friday night",
                    "The food was really good, especially the seafood pasta",
                    "The service was a bit slow though, took about 25 minutes for appetizers",
                    "The atmosphere was nice and cozy, perfect for a date",
                    "Overall I'd give it 4 out of 5 stars"
                ]
            }
        ]
        
        for scenario in conversation_scenarios:
            print(f"\n  Testing: {scenario['name']}")
            success_count = 0
            
            for i, message in enumerate(scenario["messages"]):
                print(f"    Message {i+1}: {message[:30]}...")
                
                if self.send_message(message):
                    success_count += 1
                    time.sleep(2)  # Natural pause between messages
                else:
                    print(f"    Failed to get response for message {i+1}")
            
            success_rate = (success_count / len(scenario["messages"])) * 100
            self.log_result(f"{scenario['name']} conversation flow", 
                          success_rate >= 80, 
                          f"Success rate: {success_rate:.1f}%")
    
    def test_conversation_edge_cases(self):
        """Test edge cases and difficult scenarios"""
        print("\n⚠️  Testing Conversation Edge Cases...")
        
        edge_cases = [
            {
                "name": "Off-topic Detection",
                "message": "What's the weather like today?",
                "expected_response": "bananas"
            },
            {
                "name": "Very Long Response",
                "message": "Well, let me tell you about my experience in great detail. " * 20,
                "expected_response": ""  # Should handle gracefully
            },
            {
                "name": "Special Characters and Emojis",
                "message": "I love pizza 🍕 and café ☕ with special chars: @#$%^&*()",
                "expected_response": ""
            },
            {
                "name": "Multiple Questions in One Message",
                "message": "I like Italian food. How often do I eat out? Maybe twice a week. What about my cooking skills? I'd say I'm intermediate.",
                "expected_response": ""
            },
            {
                "name": "Correction and Clarification",
                "message": "Actually, I meant to say Thai food, not Italian. Sorry for the confusion.",
                "expected_response": ""
            },
            {
                "name": "Refusal to Answer",
                "message": "I don't want to answer that question. Can we skip it?",
                "expected_response": ""
            },
            {
                "name": "Gibberish Input",
                "message": "asdjfklasdjf aslkdfj alskdfj",
                "expected_response": "bananas"
            }
        ]
        
        for case in edge_cases:
            # Start fresh session for each edge case
            if not self.start_chat_session():
                continue
                
            print(f"  Testing: {case['name']}")
            
            if self.send_message(case["message"]):
                time.sleep(3)  # Wait for processing
                
                response = self.get_last_bot_response().lower()
                
                if case["expected_response"] == "bananas":
                    success = "bananas" in response
                    self.log_result(f"Edge case: {case['name']}", success, 
                                  f"Response: {response[:50]}...")
                else:
                    # For other cases, just check that we got a response
                    success = len(response) > 0
                    self.log_result(f"Edge case: {case['name']}", success,
                                  f"Got response: {'Yes' if success else 'No'}")
            else:
                self.log_result(f"Edge case: {case['name']}", False, "Failed to send message")
    
    def test_conversation_memory_and_context(self):
        """Test conversation memory and context awareness"""
        print("\n🧠 Testing Conversation Memory and Context...")
        
        if not self.start_chat_session():
            return
        
        memory_tests = [
            {
                "setup_message": "My name is John and I'm 25 years old",
                "followup_message": "What did I say my name was?",
                "test_name": "Basic Information Recall"
            },
            {
                "setup_message": "I prefer Italian cuisine over Mexican food",
                "followup_message": "Wait, actually I like Mexican food better",
                "test_name": "Preference Correction"
            },
            {
                "setup_message": "I eat out about 3 times per week usually",
                "followup_message": "How often did I say I eat out?",
                "test_name": "Frequency Information Recall"
            }
        ]
        
        for test in memory_tests:
            print(f"  Testing: {test['test_name']}")
            
            # Send setup message
            if self.send_message(test["setup_message"]):
                time.sleep(2)
                
                # Send followup message
                if self.send_message(test["followup_message"]):
                    time.sleep(3)
                    response = self.get_last_bot_response()
                    
                    # Check if response shows awareness of previous context
                    success = len(response) > 10  # Basic check for meaningful response
                    self.log_result(f"Memory test: {test['test_name']}", success,
                                  f"Response length: {len(response)}")
                else:
                    self.log_result(f"Memory test: {test['test_name']}", False, "Followup message failed")
            else:
                self.log_result(f"Memory test: {test['test_name']}", False, "Setup message failed")
    
    def test_rapid_interaction_patterns(self):
        """Test rapid interactions and stress scenarios"""
        print("\n⚡ Testing Rapid Interaction Patterns...")
        
        if not self.start_chat_session():
            return
        
        # Test 1: Rapid successive messages
        rapid_messages = ["Hi", "Hello", "How are you?", "Let's start", "I'm ready"]
        
        print("  Testing: Rapid Successive Messages")
        success_count = 0
        
        for i, msg in enumerate(rapid_messages):
            if self.send_message(msg, expect_response=False):
                success_count += 1
            time.sleep(0.5)  # Very short delay
        
        # Wait for final response
        time.sleep(5)
        final_response = self.get_last_bot_response()
        
        self.log_result("Rapid successive messages", 
                      success_count >= 3 and len(final_response) > 0,
                      f"Sent: {success_count}/{len(rapid_messages)}")
        
        # Test 2: Long conversation simulation
        if not self.start_chat_session():
            return
            
        print("  Testing: Extended Conversation")
        
        extended_messages = [
            "I want to share my travel experience",
            "I went to Japan last month",
            "Tokyo was absolutely amazing",
            "The food was incredible",
            "Sushi, ramen, everything was perfect",
            "The people were so friendly and helpful",
            "I visited temples and modern districts",
            "Shopping in Shibuya was fun",
            "I'd definitely go back again",
            "Overall rating would be 10/10"
        ]
        
        extended_success = 0
        for i, msg in enumerate(extended_messages):
            print(f"    Extended message {i+1}/10")
            if self.send_message(msg):
                extended_success += 1
                time.sleep(1)  # Normal conversation pace
        
        success_rate = (extended_success / len(extended_messages)) * 100
        self.log_result("Extended conversation", 
                      success_rate >= 70,
                      f"Success rate: {success_rate:.1f}%")
    
    def run_complex_conversation_tests(self):
        """Run all complex conversation tests"""
        print("🚀 Complex Conversation Test Suite")
        print("=" * 60)
        
        self.setup_browser()
        
        try:
            # Phase 1: Natural conversation flow
            self.test_natural_conversation_flow()
            
            # Phase 2: Edge cases and error handling
            self.test_conversation_edge_cases()
            
            # Phase 3: Memory and context awareness
            self.test_conversation_memory_and_context()
            
            # Phase 4: Rapid interactions and stress testing
            self.test_rapid_interaction_patterns()
            
        finally:
            self.cleanup()
    
    def cleanup(self):
        """Clean up and generate summary"""
        if self.driver:
            self.driver.quit()
        
        self.generate_summary()
    
    def generate_summary(self):
        """Generate test summary"""
        total_tests = len(self.results)
        passed_tests = len([r for r in self.results if r["success"]])
        failed_tests = total_tests - passed_tests
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        print("\n" + "=" * 60)
        print("🏁 COMPLEX CONVERSATION TEST SUMMARY")
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
        
        # Conversation quality assessment
        if success_rate >= 90:
            print("🎉 CONVERSATION QUALITY: EXCELLENT - Human-like interactions!")
        elif success_rate >= 75:
            print("✅ CONVERSATION QUALITY: GOOD - Minor conversation issues")
        elif success_rate >= 60:
            print("⚠️  CONVERSATION QUALITY: NEEDS WORK - Several chat problems")
        else:
            print("❌ CONVERSATION QUALITY: CRITICAL - Major conversation failures")
        
        # Save detailed results
        with open('complex_conversation_results.json', 'w') as f:
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
    tester = ComplexConversationTester()
    tester.run_complex_conversation_tests()
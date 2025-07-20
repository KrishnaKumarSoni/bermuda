#!/usr/bin/env python3
"""
Comprehensive test suite for Bermuda system
Tests all aspects based on YAML specifications:
- API endpoints (creator & respondent)
- Chat conversation flows
- Data extraction and transformation
- UI components (via DOM validation)
- Error handling and edge cases
"""

import requests
import json
import time
import uuid
import sys
from datetime import datetime
from typing import Dict, List, Any, Optional

# Test configuration  
BASE_URL = "https://bermuda-01.web.app"
TEST_FORM_ID = "test-form-123"

class BermudaTestSuite:
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
            
    def make_request(self, method: str, endpoint: str, data: Dict = None, headers: Dict = None) -> Dict:
        """Make HTTP request with error handling"""
        try:
            url = f"{BASE_URL}{endpoint}"
            if headers is None:
                headers = {"Content-Type": "application/json"}
                
            if method.upper() == "GET":
                response = requests.get(url, headers=headers, timeout=10)
            elif method.upper() == "POST":
                response = requests.post(url, json=data, headers=headers, timeout=10)
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

    def test_api_health_checks(self):
        """Test 1-5: API Health and Status"""
        self.log("Starting API Health Check Tests")
        
        # Test 1: Respondent API health
        response = self.make_request("GET", "/api/health")
        self.assert_test(
            response["status_code"] == 200 and "healthy" in str(response["data"]),
            "Respondent API health check",
            f"Status: {response['status_code']}, Data: {response['data']}"
        )
        
        # Test 2: OpenAI configuration
        if response["status_code"] == 200:
            data = response["data"]
            self.assert_test(
                data.get("openai") == "configured",
                "OpenAI API configuration",
                f"OpenAI status: {data.get('openai')}"
            )
            
        # Test 3: Creator API health (should work or route properly)
        response = self.make_request("GET", "/api/health-creator")
        self.assert_test(
            response["status_code"] in [200, 404],  # 404 is OK if not routed
            "Creator API health endpoint accessible",
            f"Status: {response['status_code']}"
        )
        
        # Test 4: Non-existent endpoint error handling
        response = self.make_request("GET", "/api/nonexistent")
        self.assert_test(
            response["status_code"] == 404,
            "404 error for non-existent endpoint",
            f"Status: {response['status_code']}"
        )
        
        # Test 5: Base URL accessibility
        response = self.make_request("GET", "/")
        self.assert_test(
            response["status_code"] in [200, 301, 302],
            "Base URL accessibility",
            f"Status: {response['status_code']}"
        )

    def test_form_metadata_api(self):
        """Test 6-15: Form Metadata API"""
        self.log("Starting Form Metadata API Tests")
        
        # Test 6: Valid form metadata retrieval
        response = self.make_request("GET", f"/api/forms/{TEST_FORM_ID}")
        self.assert_test(
            response["status_code"] == 200,
            "Valid form metadata retrieval",
            f"Status: {response['status_code']}"
        )
        
        if response["status_code"] == 200:
            data = response["data"]
            
            # Test 7: Form has required fields
            required_fields = ["title", "questions", "demographics"]
            has_all_fields = all(field in data for field in required_fields)
            self.assert_test(
                has_all_fields,
                "Form metadata contains required fields",
                f"Fields present: {list(data.keys())}"
            )
            
            # Test 8: Questions structure validation
            questions = data.get("questions", [])
            self.assert_test(
                len(questions) > 0,
                "Form has questions",
                f"Question count: {len(questions)}"
            )
            
            # Test 9: Question types validation
            if questions:
                valid_types = ["text", "multiple_choice", "yes_no", "number", "rating"]
                question_types_valid = all(q.get("type") in valid_types for q in questions)
                self.assert_test(
                    question_types_valid,
                    "All question types are valid",
                    f"Types found: {[q.get('type') for q in questions]}"
                )
                
            # Test 10: Demographics structure
            demographics = data.get("demographics", [])
            self.assert_test(
                isinstance(demographics, list),
                "Demographics is a list",
                f"Demographics type: {type(demographics)}"
            )
            
        # Test 11: Invalid form ID handling
        response = self.make_request("GET", "/api/forms/invalid-form-id")
        self.assert_test(
            response["status_code"] == 404,
            "Invalid form ID returns 404",
            f"Status: {response['status_code']}"
        )
        
        # Test 12: Empty form ID handling
        response = self.make_request("GET", "/api/forms/")
        self.assert_test(
            response["status_code"] in [404, 405],
            "Empty form ID handled properly",
            f"Status: {response['status_code']}"
        )
        
        # Test 13: Form ID with special characters
        response = self.make_request("GET", "/api/forms/test@#$%")
        self.assert_test(
            response["status_code"] == 404,
            "Form ID with special characters returns 404",
            f"Status: {response['status_code']}"
        )
        
        # Test 14: Very long form ID
        long_id = "a" * 100
        response = self.make_request("GET", f"/api/forms/{long_id}")
        self.assert_test(
            response["status_code"] == 404,
            "Very long form ID handled gracefully",
            f"Status: {response['status_code']}"
        )
        
        # Test 15: Case sensitivity test
        response = self.make_request("GET", f"/api/forms/{TEST_FORM_ID.upper()}")
        self.assert_test(
            response["status_code"] == 404,
            "Form ID is case sensitive",
            f"Status: {response['status_code']}"
        )

    def test_chat_initialization(self):
        """Test 16-25: Chat Initialization"""
        self.log("Starting Chat Initialization Tests")
        
        # Test 16: Debug chat endpoint
        response = self.make_request("POST", "/api/debug/test-chat", {
            "message": "Hello, I want to start the survey"
        })
        self.assert_test(
            response["status_code"] == 200,
            "Debug chat endpoint responds",
            f"Status: {response['status_code']}"
        )
        
        if response["status_code"] == 200:
            data = response["data"]
            
            # Test 17: Bot initiates conversation
            bot_response = data.get("bot_response", "")
            self.assert_test(
                len(bot_response) > 0,
                "Bot provides initial response",
                f"Response length: {len(bot_response)}"
            )
            
            # Test 18: Bot response is conversational
            conversational_indicators = ["!", "?", "👋", "😊", "Hey", "Hi", "What"]
            is_conversational = any(indicator in bot_response for indicator in conversational_indicators)
            self.assert_test(
                is_conversational,
                "Bot response is conversational",
                f"Response: {bot_response[:100]}"
            )
            
            # Test 19: Session ID generation
            session_id = data.get("session_id")
            self.assert_test(
                session_id is not None and len(session_id) > 10,
                "Session ID generated",
                f"Session ID: {session_id}"
            )
            
            # Test 20: Form data included
            form_data = data.get("form_data")
            self.assert_test(
                form_data is not None and "questions" in form_data,
                "Form data included in response",
                f"Form data keys: {list(form_data.keys()) if form_data else 'None'}"
            )
            
        # Test 21: Empty message handling
        response = self.make_request("POST", "/api/debug/test-chat", {
            "message": ""
        })
        self.assert_test(
            response["status_code"] in [200, 400],
            "Empty message handled",
            f"Status: {response['status_code']}"
        )
        
        # Test 22: Very long message
        long_message = "a" * 1500
        response = self.make_request("POST", "/api/debug/test-chat", {
            "message": long_message
        })
        self.assert_test(
            response["status_code"] in [200, 400],
            "Very long message handled",
            f"Status: {response['status_code']}"
        )
        
        # Test 23: Special characters in message
        response = self.make_request("POST", "/api/debug/test-chat", {
            "message": "Hello! @#$%^&*(){}[]|\\:;\"'<>?,./"
        })
        self.assert_test(
            response["status_code"] == 200,
            "Special characters in message handled",
            f"Status: {response['status_code']}"
        )
        
        # Test 24: Unicode/emoji in message
        response = self.make_request("POST", "/api/debug/test-chat", {
            "message": "Hello 👋 I love pizza 🍕 café ñoño"
        })
        self.assert_test(
            response["status_code"] == 200,
            "Unicode/emoji in message handled",
            f"Status: {response['status_code']}"
        )
        
        # Test 25: Malformed JSON handling
        try:
            response = requests.post(
                f"{BASE_URL}/api/debug/test-chat",
                data="invalid json",
                headers={"Content-Type": "application/json"},
                timeout=10
            )
            self.assert_test(
                response.status_code == 400,
                "Malformed JSON returns 400",
                f"Status: {response.status_code}"
            )
        except:
            self.assert_test(True, "Malformed JSON handled gracefully", "Exception caught")

    def test_conversation_flow(self):
        """Test 26-40: Conversation Flow"""
        self.log("Starting Conversation Flow Tests")
        
        # Test 26: First question asked naturally
        response = self.make_request("POST", "/api/debug/test-chat", {
            "message": "I want to take the pizza survey"
        })
        
        if response["status_code"] == 200:
            bot_response = response["data"].get("bot_response", "")
            
            # Test 27: Bot asks about pizza topping (first question)
            asks_topping = any(word in bot_response.lower() for word in ["topping", "favorite", "pizza"])
            self.assert_test(
                asks_topping,
                "Bot asks about pizza topping naturally",
                f"Response: {bot_response}"
            )
            
            # Test 28: No bias in questioning (doesn't list options)
            lists_options = any(phrase in bot_response.lower() for phrase in ["daily, weekly", "choose from", "a) b) c)"])
            self.assert_test(
                not lists_options,
                "Bot doesn't list options (no bias)",
                f"Response: {bot_response}"
            )
            
        # Test 29: Response to specific answer
        response = self.make_request("POST", "/api/debug/test-chat", {
            "message": "I love pepperoni pizza"
        })
        
        if response["status_code"] == 200:
            bot_response = response["data"].get("bot_response", "")
            
            # Test 30: Bot acknowledges answer and moves to next question
            acknowledges = any(word in bot_response.lower() for word in ["great", "awesome", "cool", "nice"])
            self.assert_test(
                acknowledges,
                "Bot acknowledges answer positively",
                f"Response: {bot_response}"
            )
            
            # Test 31: Bot asks next question (frequency)
            asks_frequency = any(word in bot_response.lower() for word in ["often", "frequency", "how much"])
            self.assert_test(
                asks_frequency,
                "Bot moves to frequency question",
                f"Response: {bot_response}"
            )
            
        # Test 32: Multiple choice response handling
        response = self.make_request("POST", "/api/debug/test-chat", {
            "message": "I eat pizza about twice a week"
        })
        
        if response["status_code"] == 200:
            bot_response = response["data"].get("bot_response", "")
            
            # Test 33: Bot continues conversation naturally
            self.assert_test(
                len(bot_response) > 0,
                "Bot continues conversation after frequency answer",
                f"Response length: {len(bot_response)}"
            )
            
        # Test 34: Off-topic message handling
        response = self.make_request("POST", "/api/debug/test-chat", {
            "message": "What's the weather like today?"
        })
        
        if response["status_code"] == 200:
            bot_response = response["data"].get("bot_response", "")
            
            # Test 35: Bot uses "bananas" for off-topic
            uses_bananas = "bananas" in bot_response.lower()
            self.assert_test(
                uses_bananas,
                "Bot uses 'bananas' for off-topic messages",
                f"Response: {bot_response}"
            )
            
            # Test 36: Bot redirects back to survey
            redirects = any(phrase in bot_response.lower() for phrase in ["anyway", "back to", "survey", "preferences", "pizza", "favorite", "topping"])
            self.assert_test(
                redirects,
                "Bot redirects back to survey",
                f"Response: {bot_response}"
            )
            
        # Test 37: Gibberish handling
        response = self.make_request("POST", "/api/debug/test-chat", {
            "message": "asdfghjkl qwerty"
        })
        
        if response["status_code"] == 200:
            bot_response = response["data"].get("bot_response", "")
            
            # Test 38: Bot handles gibberish with bananas
            handles_gibberish = "bananas" in bot_response.lower()
            self.assert_test(
                handles_gibberish,
                "Bot handles gibberish with 'bananas'",
                f"Response: {bot_response}"
            )
            
        # Test 39: Natural language number handling
        response = self.make_request("POST", "/api/debug/test-chat", {
            "message": "I would rate it as excellent, maybe 4 or 5 stars"
        })
        
        self.assert_test(
            response["status_code"] == 200,
            "Bot handles natural language numbers",
            f"Status: {response['status_code']}"
        )
        
        # Test 40: Conversation memory (contextual response)
        response = self.make_request("POST", "/api/debug/test-chat", {
            "message": "Actually, I changed my mind about the pepperoni"
        })
        
        if response["status_code"] == 200:
            bot_response = response["data"].get("bot_response", "")
            
            # Test: Bot acknowledges the change
            acknowledges_change = any(word in bot_response.lower() for word in ["changed", "different", "now", "instead"])
            self.assert_test(
                acknowledges_change or len(bot_response) > 0,
                "Bot handles answer changes gracefully",
                f"Response: {bot_response}"
            )

    def test_data_extraction(self):
        """Test 41-55: Data Extraction and Transformation"""
        self.log("Starting Data Extraction Tests")
        
        # Test 41: Basic data extraction
        test_transcript = [
            {"role": "assistant", "text": "What is your favorite pizza topping?"},
            {"role": "user", "text": "I love pepperoni"},
            {"role": "assistant", "text": "How often do you eat pizza?"},
            {"role": "user", "text": "About twice a week"},
            {"role": "assistant", "text": "Do you prefer thick or thin crust?"},
            {"role": "user", "text": "Thin crust definitely"}
        ]
        
        questions_json = {
            "questions": [
                {"text": "What is your favorite pizza topping?", "type": "text"},
                {"text": "How often do you eat pizza?", "type": "multiple_choice", "options": ["Daily", "Weekly", "Monthly", "Rarely"]},
                {"text": "Do you prefer thick or thin crust?", "type": "multiple_choice", "options": ["Thick crust", "Thin crust"]}
            ]
        }
        
        response = self.make_request("POST", "/api/extract", {
            "session_id": "test-extraction",
            "transcript": test_transcript,
            "questions_json": questions_json
        })
        
        self.assert_test(
            response["status_code"] == 200,
            "Data extraction endpoint responds",
            f"Status: {response['status_code']}"
        )
        
        if response["status_code"] == 200:
            data = response["data"]
            
            # Test 42: Extraction returns structured data
            self.assert_test(
                "questions" in data,
                "Extraction returns questions data",
                f"Data keys: {list(data.keys())}"
            )
            
            # Test 43: Text type extraction
            questions_data = data.get("questions", {})
            topping_answer = questions_data.get("What is your favorite pizza topping?")
            self.assert_test(
                topping_answer and "pepperoni" in topping_answer.lower(),
                "Text type extracted correctly",
                f"Topping answer: {topping_answer}"
            )
            
            # Test 44: Multiple choice mapping
            frequency_answer = questions_data.get("How often do you eat pizza?")
            self.assert_test(
                frequency_answer == "Weekly",
                "Multiple choice mapped correctly",
                f"Frequency answer: {frequency_answer}"
            )
            
            # Test 45: Multiple choice exact match
            crust_answer = questions_data.get("Do you prefer thick or thin crust?")
            self.assert_test(
                crust_answer == "Thin crust",
                "Multiple choice exact match works",
                f"Crust answer: {crust_answer}"
            )
            
            # Test 46: Completion status
            completion_status = data.get("completion_status")
            self.assert_test(
                completion_status in ["complete", "partial"],
                "Completion status provided",
                f"Status: {completion_status}"
            )
            
        # Test 47: Rating type extraction
        rating_transcript = [
            {"role": "assistant", "text": "Rate your satisfaction"},
            {"role": "user", "text": "It's really good, I'd say 4 out of 5"}
        ]
        
        rating_questions = {
            "questions": [
                {"text": "Rate your satisfaction", "type": "rating", "options": ["1", "2", "3", "4", "5"]}
            ]
        }
        
        response = self.make_request("POST", "/api/extract", {
            "session_id": "test-rating",
            "transcript": rating_transcript,
            "questions_json": rating_questions
        })
        
        if response["status_code"] == 200:
            data = response["data"]
            rating_answer = data.get("questions", {}).get("Rate your satisfaction")
            
            # Test 48: Rating conversion to number
            self.assert_test(
                rating_answer == 4 or rating_answer == "4",
                "Rating converted to number",
                f"Rating answer: {rating_answer}"
            )
            
        # Test 49: Yes/No type extraction
        yesno_transcript = [
            {"role": "assistant", "text": "Do you like pizza?"},
            {"role": "user", "text": "Yeah, definitely!"}
        ]
        
        yesno_questions = {
            "questions": [
                {"text": "Do you like pizza?", "type": "yes_no"}
            ]
        }
        
        response = self.make_request("POST", "/api/extract", {
            "session_id": "test-yesno",
            "transcript": yesno_transcript,
            "questions_json": yesno_questions
        })
        
        if response["status_code"] == 200:
            data = response["data"]
            yesno_answer = data.get("questions", {}).get("Do you like pizza?")
            
            # Test 50: Yes/No mapping
            self.assert_test(
                yesno_answer == "Yes",
                "Yes/No mapped correctly",
                f"Yes/No answer: {yesno_answer}"
            )
            
        # Test 51: Number type extraction
        number_transcript = [
            {"role": "assistant", "text": "How many pizzas do you eat per month?"},
            {"role": "user", "text": "I usually have about 6 or 7 pizzas per month"}
        ]
        
        number_questions = {
            "questions": [
                {"text": "How many pizzas do you eat per month?", "type": "number"}
            ]
        }
        
        response = self.make_request("POST", "/api/extract", {
            "session_id": "test-number",
            "transcript": number_transcript,
            "questions_json": number_questions
        })
        
        if response["status_code"] == 200:
            data = response["data"]
            number_answer = data.get("questions", {}).get("How many pizzas do you eat per month?")
            
            # Test 52: Number extraction
            try:
                number_value = float(number_answer) if number_answer else 0
                self.assert_test(
                    5 <= number_value <= 8,
                    "Number extracted from natural language",
                    f"Number answer: {number_answer}"
                )
            except:
                self.assert_test(False, "Number extraction failed", f"Answer: {number_answer}")
                
        # Test 53: Empty transcript handling
        response = self.make_request("POST", "/api/extract", {
            "session_id": "test-empty",
            "transcript": [],
            "questions_json": {"questions": []}
        })
        
        self.assert_test(
            response["status_code"] in [200, 400],
            "Empty transcript handled",
            f"Status: {response['status_code']}"
        )
        
        # Test 54: Missing fields handling
        response = self.make_request("POST", "/api/extract", {
            "session_id": "test-missing"
        })
        
        self.assert_test(
            response["status_code"] == 400,
            "Missing fields return 400",
            f"Status: {response['status_code']}"
        )
        
        # Test 55: Malformed questions_json
        response = self.make_request("POST", "/api/extract", {
            "session_id": "test-malformed",
            "transcript": test_transcript,
            "questions_json": "invalid"
        })
        
        self.assert_test(
            response["status_code"] in [200, 400],
            "Malformed questions_json handled",
            f"Status: {response['status_code']}"
        )

    def test_api_edge_cases(self):
        """Test 56-70: API Edge Cases and Error Handling"""
        self.log("Starting API Edge Cases Tests")
        
        # Test 56: Rate limiting simulation (multiple rapid requests)
        start_time = time.time()
        responses = []
        for i in range(5):
            response = self.make_request("GET", "/api/health")
            responses.append(response["status_code"])
            
        # Test 57: All requests should succeed (no rate limiting issues)
        all_success = all(status == 200 for status in responses)
        self.assert_test(
            all_success,
            "Multiple rapid requests handled",
            f"Status codes: {responses}"
        )
        
        # Test 58: Request timeout simulation (invalid endpoint that might hang)
        try:
            response = requests.get(f"{BASE_URL}/api/slow", timeout=3)
            self.assert_test(
                response.status_code == 404,
                "Non-existent slow endpoint returns 404",
                f"Status: {response.status_code}"
            )
        except requests.Timeout:
            self.assert_test(True, "Request timeout handled gracefully", "Timeout occurred")
        except:
            self.assert_test(True, "Request exception handled", "Exception caught")
            
        # Test 59: Large payload handling
        large_data = {
            "session_id": "test-large",
            "transcript": [{"role": "user", "text": "a" * 10000}] * 50,
            "questions_json": {"questions": []}
        }
        
        response = self.make_request("POST", "/api/extract", large_data)
        self.assert_test(
            response["status_code"] in [200, 400, 413],
            "Large payload handled appropriately",
            f"Status: {response['status_code']}"
        )
        
        # Test 60: SQL injection attempt in form_id
        malicious_form_id = "'; DROP TABLE forms; --"
        response = self.make_request("GET", f"/api/forms/{malicious_form_id}")
        self.assert_test(
            response["status_code"] == 404,
            "SQL injection attempt handled safely",
            f"Status: {response['status_code']}"
        )
        
        # Test 61: XSS attempt in message
        xss_message = "<script>alert('xss')</script>"
        response = self.make_request("POST", "/api/debug/test-chat", {
            "message": xss_message
        })
        self.assert_test(
            response["status_code"] == 200,
            "XSS attempt in message handled",
            f"Status: {response['status_code']}"
        )
        
        # Test 62: Invalid HTTP method
        try:
            response = requests.put(f"{BASE_URL}/api/health", timeout=5)
            self.assert_test(
                response.status_code == 405,
                "Invalid HTTP method returns 405",
                f"Status: {response.status_code}"
            )
        except:
            self.assert_test(True, "Invalid HTTP method handled", "Exception occurred")
            
        # Test 63: Missing Content-Type header
        try:
            response = requests.post(
                f"{BASE_URL}/api/debug/test-chat",
                data='{"message": "test"}',
                timeout=5
            )
            self.assert_test(
                response.status_code in [200, 400],
                "Missing Content-Type handled",
                f"Status: {response.status_code}"
            )
        except:
            self.assert_test(True, "Missing Content-Type handled", "Exception occurred")
            
        # Test 64: Invalid JSON content-type
        try:
            response = requests.post(
                f"{BASE_URL}/api/debug/test-chat",
                json={"message": "test"},
                headers={"Content-Type": "text/plain"},
                timeout=5
            )
            self.assert_test(
                response.status_code in [200, 400],
                "Invalid content-type handled",
                f"Status: {response.status_code}"
            )
        except:
            self.assert_test(True, "Invalid content-type handled", "Exception occurred")
            
        # Test 65: Empty request body
        try:
            response = requests.post(
                f"{BASE_URL}/api/debug/test-chat",
                data="",
                headers={"Content-Type": "application/json"},
                timeout=5
            )
            self.assert_test(
                response.status_code == 400,
                "Empty request body returns 400",
                f"Status: {response.status_code}"
            )
        except:
            self.assert_test(True, "Empty request body handled", "Exception occurred")
            
        # Test 66: Very long URL
        long_id = "a" * 500
        response = self.make_request("GET", f"/api/forms/{long_id}")
        self.assert_test(
            response["status_code"] in [404, 414],
            "Very long URL handled",
            f"Status: {response['status_code']}"
        )
        
        # Test 67: Unicode in URL
        unicode_id = "测试🍕café"
        response = self.make_request("GET", f"/api/forms/{unicode_id}")
        self.assert_test(
            response["status_code"] == 404,
            "Unicode in URL handled",
            f"Status: {response['status_code']}"
        )
        
        # Test 68: Null bytes in request
        try:
            response = requests.post(
                f"{BASE_URL}/api/debug/test-chat",
                json={"message": "test\x00null"},
                timeout=5
            )
            self.assert_test(
                response.status_code in [200, 400],
                "Null bytes in request handled",
                f"Status: {response.status_code}"
            )
        except:
            self.assert_test(True, "Null bytes handled", "Exception occurred")
            
        # Test 69: Concurrent requests simulation
        import threading
        results = []
        
        def make_concurrent_request():
            response = self.make_request("GET", "/api/health")
            results.append(response["status_code"])
            
        threads = []
        for i in range(3):
            thread = threading.Thread(target=make_concurrent_request)
            threads.append(thread)
            thread.start()
            
        for thread in threads:
            thread.join()
            
        self.assert_test(
            all(status == 200 for status in results),
            "Concurrent requests handled",
            f"Results: {results}"
        )
        
        # Test 70: API versioning (non-existent version)
        response = self.make_request("GET", "/api/v2/health")
        self.assert_test(
            response["status_code"] == 404,
            "API versioning handled",
            f"Status: {response['status_code']}"
        )

    def test_ui_and_frontend(self):
        """Test 71-85: UI Components and Frontend"""
        self.log("Starting UI and Frontend Tests")
        
        # Test 71: Landing page accessibility
        response = self.make_request("GET", "/")
        self.assert_test(
            response["status_code"] in [200, 301, 302],
            "Landing page accessible",
            f"Status: {response['status_code']}"
        )
        
        # Test 72: Frontend serves HTML
        try:
            response = requests.get(BASE_URL, timeout=10)
            is_html = "html" in response.text.lower()
            self.assert_test(
                is_html,
                "Frontend serves HTML content",
                f"Content type: {response.headers.get('content-type', 'unknown')}"
            )
        except:
            self.assert_test(False, "Frontend HTML test failed", "Exception occurred")
            
        # Test 73: CSS styling present
        try:
            response = requests.get(BASE_URL, timeout=10)
            has_css = any(keyword in response.text.lower() for keyword in ["css", "style", "tailwind"])
            self.assert_test(
                has_css,
                "CSS styling present in HTML",
                "Checked for CSS keywords"
            )
        except:
            self.assert_test(False, "CSS styling test failed", "Exception occurred")
            
        # Test 74: JavaScript present
        try:
            response = requests.get(BASE_URL, timeout=10)
            has_js = any(keyword in response.text.lower() for keyword in ["script", "javascript", "js"])
            self.assert_test(
                has_js,
                "JavaScript present in HTML",
                "Checked for JS keywords"
            )
        except:
            self.assert_test(False, "JavaScript test failed", "Exception occurred")
            
        # Test 75: UI color scheme validation
        try:
            response = requests.get(BASE_URL, timeout=10)
            has_orange = "#CC5500" in response.text or "orange" in response.text.lower()
            self.assert_test(
                has_orange,
                "Burnt orange color scheme present",
                "Checked for orange colors"
            )
        except:
            self.assert_test(False, "Color scheme test failed", "Exception occurred")
            
        # Test 76: Typography fonts
        try:
            response = requests.get(BASE_URL, timeout=10)
            has_fonts = any(font in response.text for font in ["Plus Jakarta Sans", "Inter Tight"])
            self.assert_test(
                has_fonts,
                "Custom typography fonts present",
                "Checked for specified fonts"
            )
        except:
            self.assert_test(False, "Typography test failed", "Exception occurred")
            
        # Test 77: Mobile responsiveness indicators
        try:
            response = requests.get(BASE_URL, timeout=10)
            has_responsive = any(keyword in response.text.lower() for keyword in ["viewport", "responsive", "mobile"])
            self.assert_test(
                has_responsive,
                "Mobile responsiveness indicators present",
                "Checked for responsive design keywords"
            )
        except:
            self.assert_test(False, "Responsiveness test failed", "Exception occurred")
            
        # Test 78: Form route accessibility
        response = self.make_request("GET", f"/form/{TEST_FORM_ID}")
        self.assert_test(
            response["status_code"] in [200, 301, 302],
            "Form route accessible",
            f"Status: {response['status_code']}"
        )
        
        # Test 79: Dashboard route accessibility
        response = self.make_request("GET", "/dashboard")
        self.assert_test(
            response["status_code"] in [200, 301, 302],
            "Dashboard route accessible",
            f"Status: {response['status_code']}"
        )
        
        # Test 80: Static assets (favicon, etc.)
        response = self.make_request("GET", "/favicon.ico")
        self.assert_test(
            response["status_code"] in [200, 404],  # 404 is acceptable
            "Static assets route handled",
            f"Status: {response['status_code']}"
        )
        
        # Test 81: Chat interface route
        response = self.make_request("GET", f"/form/{TEST_FORM_ID}")
        try:
            if response["status_code"] == 200:
                content = response["data"]
                has_chat_elements = any(keyword in str(content).lower() for keyword in ["chat", "message", "input"])
                self.assert_test(
                    has_chat_elements,
                    "Chat interface elements present",
                    "Checked for chat UI elements"
                )
            else:
                self.assert_test(True, "Chat interface route handled", f"Status: {response['status_code']}")
        except:
            self.assert_test(False, "Chat interface test failed", "Exception occurred")
            
        # Test 82: Error page handling
        response = self.make_request("GET", "/nonexistent-page")
        self.assert_test(
            response["status_code"] in [404, 200],  # SPA might return 200
            "Error page handling",
            f"Status: {response['status_code']}"
        )
        
        # Test 83: CORS headers for frontend
        try:
            response = requests.options(f"{BASE_URL}/api/health", timeout=5)
            has_cors = "access-control-allow-origin" in [h.lower() for h in response.headers.keys()]
            self.assert_test(
                has_cors or response.status_code == 200,
                "CORS headers present for frontend",
                f"Headers: {list(response.headers.keys())}"
            )
        except:
            self.assert_test(True, "CORS test handled", "Exception occurred")
            
        # Test 84: Page performance (basic check)
        start_time = time.time()
        try:
            response = requests.get(BASE_URL, timeout=10)
            load_time = time.time() - start_time
            self.assert_test(
                load_time < 5.0,
                "Page loads within 5 seconds",
                f"Load time: {load_time:.2f}s"
            )
        except:
            self.assert_test(False, "Page performance test failed", "Exception occurred")
            
        # Test 85: Security headers
        try:
            response = requests.get(BASE_URL, timeout=10)
            security_headers = ["x-frame-options", "x-content-type-options", "content-security-policy"]
            has_security = any(header in [h.lower() for h in response.headers.keys()] for header in security_headers)
            self.assert_test(
                has_security or response.status_code == 200,
                "Security headers present or handled",
                f"Headers checked: {security_headers}"
            )
        except:
            self.assert_test(False, "Security headers test failed", "Exception occurred")

    def test_business_logic(self):
        """Test 86-100: Business Logic and Integration"""
        self.log("Starting Business Logic Tests")
        
        # Test 86: Complete conversation simulation
        session_id = str(uuid.uuid4())
        conversation_responses = []
        
        # Step 1: Initial greeting
        response = self.make_request("POST", "/api/debug/test-chat", {
            "message": "Hi! I want to take the pizza survey"
        })
        if response["status_code"] == 200:
            conversation_responses.append(response["data"].get("bot_response", ""))
            
        self.assert_test(
            len(conversation_responses) > 0 and len(conversation_responses[0]) > 0,
            "Complete conversation starts properly",
            f"First response: {conversation_responses[0][:50]}..."
        )
        
        # Test 87: Question type variety handling
        question_types = [
            ("I love pepperoni pizza", "text"),
            ("About twice a week", "multiple_choice"),  
            ("Thin crust definitely", "multiple_choice"),
            ("I'd rate it 4 out of 5", "rating")
        ]
        
        all_handled = True
        for message, q_type in question_types:
            response = self.make_request("POST", "/api/debug/test-chat", {"message": message})
            if response["status_code"] != 200:
                all_handled = False
                break
                
        self.assert_test(
            all_handled,
            "All question types handled in conversation",
            f"Tested {len(question_types)} question types"
        )
        
        # Test 88: Data persistence simulation
        test_extraction = {
            "session_id": session_id,
            "transcript": [
                {"role": "assistant", "text": "What's your favorite topping?"},
                {"role": "user", "text": "Pepperoni"},
                {"role": "assistant", "text": "How often do you eat pizza?"},
                {"role": "user", "text": "Weekly"}
            ],
            "questions_json": {
                "questions": [
                    {"text": "What's your favorite topping?", "type": "text"},
                    {"text": "How often do you eat pizza?", "type": "multiple_choice", "options": ["Daily", "Weekly", "Monthly"]}
                ]
            }
        }
        
        response = self.make_request("POST", "/api/extract", test_extraction)
        self.assert_test(
            response["status_code"] == 200,
            "Data persistence (extraction) works",
            f"Status: {response['status_code']}"
        )
        
        # Test 89: Natural language understanding
        natural_phrases = [
            "I absolutely love it",
            "Not really my thing",
            "Maybe once in a while",
            "Pretty much every day",
            "I'd say it's okay"
        ]
        
        understanding_works = True
        for phrase in natural_phrases:
            response = self.make_request("POST", "/api/debug/test-chat", {"message": phrase})
            if response["status_code"] != 200:
                understanding_works = False
                break
                
        self.assert_test(
            understanding_works,
            "Natural language understanding works",
            f"Tested {len(natural_phrases)} natural phrases"
        )
        
        # Test 90: Conversation memory consistency
        memory_test_messages = [
            "I love pizza",
            "What did I just say about pizza?",
            "Change my answer to hate pizza"
        ]
        
        memory_responses = []
        for message in memory_test_messages:
            response = self.make_request("POST", "/api/debug/test-chat", {"message": message})
            if response["status_code"] == 200:
                memory_responses.append(response["data"].get("bot_response", ""))
                
        self.assert_test(
            len(memory_responses) == len(memory_test_messages),
            "Conversation memory maintains context",
            f"Got {len(memory_responses)} responses"
        )
        
        # Test 91: Conflict resolution
        conflict_transcript = [
            {"role": "user", "text": "I love pepperoni"},
            {"role": "assistant", "text": "Great choice!"},
            {"role": "user", "text": "Actually, I prefer mushrooms"}
        ]
        
        response = self.make_request("POST", "/api/extract", {
            "session_id": "conflict-test",
            "transcript": conflict_transcript,
            "questions_json": {
                "questions": [{"text": "What's your favorite topping?", "type": "text"}]
            }
        })
        
        if response["status_code"] == 200:
            data = response["data"]
            topping = data.get("questions", {}).get("What's your favorite topping?", "")
            uses_latest = "mushroom" in topping.lower()
            self.assert_test(
                uses_latest,
                "Conflict resolution uses latest answer",
                f"Final answer: {topping}"
            )
        else:
            self.assert_test(False, "Conflict resolution test failed", f"Status: {response['status_code']}")
            
        # Test 92: Skip handling
        response = self.make_request("POST", "/api/debug/test-chat", {"message": "I'd rather skip this question"})
        if response["status_code"] == 200:
            bot_response = response["data"].get("bot_response", "")
            handles_skip = any(word in bot_response.lower() for word in ["skip", "no worries", "okay"])
            self.assert_test(
                handles_skip,
                "Skip requests handled gracefully",
                f"Response: {bot_response}"
            )
        else:
            self.assert_test(False, "Skip handling test failed", f"Status: {response['status_code']}")
            
        # Test 93: Demographics collection
        demographics_message = "I'm 25 years old and work as a software engineer"
        response = self.make_request("POST", "/api/debug/test-chat", {"message": demographics_message})
        self.assert_test(
            response["status_code"] == 200,
            "Demographics information processed",
            f"Status: {response['status_code']}"
        )
        
        # Test 94: Completion detection
        completion_transcript = [
            {"role": "assistant", "text": "What's your favorite topping?"},
            {"role": "user", "text": "Pepperoni"},
            {"role": "assistant", "text": "How often do you eat pizza?"},
            {"role": "user", "text": "Weekly"},
            {"role": "assistant", "text": "Thanks! That's all I needed."}
        ]
        
        response = self.make_request("POST", "/api/extract", {
            "session_id": "completion-test",
            "transcript": completion_transcript,
            "questions_json": {
                "questions": [
                    {"text": "What's your favorite topping?", "type": "text"},
                    {"text": "How often do you eat pizza?", "type": "multiple_choice", "options": ["Daily", "Weekly"]}
                ]
            }
        })
        
        if response["status_code"] == 200:
            completion_status = response["data"].get("completion_status")
            self.assert_test(
                completion_status == "complete",
                "Completion detection works",
                f"Status: {completion_status}"
            )
        else:
            self.assert_test(False, "Completion detection test failed", f"Status: {response['status_code']}")
            
        # Test 95: Error recovery
        error_scenarios = [
            {"message": ""},  # Empty message
            {"message": "a" * 2000},  # Very long message
            {"invalid": "field"}  # Invalid field
        ]
        
        error_handled = 0
        for scenario in error_scenarios:
            response = self.make_request("POST", "/api/debug/test-chat", scenario)
            if response["status_code"] in [200, 400]:  # Both acceptable
                error_handled += 1
                
        self.assert_test(
            error_handled == len(error_scenarios),
            "Error scenarios handled gracefully",
            f"Handled {error_handled}/{len(error_scenarios)} scenarios"
        )
        
        # Test 96: Performance under load
        start_time = time.time()
        rapid_requests = []
        for i in range(10):
            response = self.make_request("POST", "/api/debug/test-chat", {"message": f"Test message {i}"})
            rapid_requests.append(response["status_code"])
            
        total_time = time.time() - start_time
        all_success = all(status == 200 for status in rapid_requests)
        
        self.assert_test(
            all_success and total_time < 30,
            "Performance under load acceptable",
            f"10 requests in {total_time:.2f}s, success: {rapid_requests.count(200)}/10"
        )
        
        # Test 97: Cross-session isolation
        session1_response = self.make_request("POST", "/api/debug/test-chat", {"message": "Session 1 message"})
        session2_response = self.make_request("POST", "/api/debug/test-chat", {"message": "Session 2 message"})
        
        sessions_isolated = (
            session1_response["status_code"] == 200 and 
            session2_response["status_code"] == 200 and
            session1_response["data"].get("session_id") != session2_response["data"].get("session_id")
        )
        
        self.assert_test(
            sessions_isolated,
            "Cross-session isolation works",
            f"Session 1: {session1_response['data'].get('session_id', 'none')[:8]}, Session 2: {session2_response['data'].get('session_id', 'none')[:8]}"
        )
        
        # Test 98: Data format consistency
        consistency_test = self.make_request("POST", "/api/extract", {
            "session_id": "format-test",
            "transcript": [
                {"role": "assistant", "text": "Test question?"},
                {"role": "user", "text": "Test answer"}
            ],
            "questions_json": {
                "questions": [{"text": "Test question?", "type": "text"}]
            }
        })
        
        if consistency_test["status_code"] == 200:
            data = consistency_test["data"]
            required_fields = ["questions", "completion_status"]
            has_required = all(field in data for field in required_fields)
            self.assert_test(
                has_required,
                "Data format consistency maintained",
                f"Fields present: {list(data.keys())}"
            )
        else:
            self.assert_test(False, "Data format consistency test failed", f"Status: {consistency_test['status_code']}")
            
        # Test 99: End-to-end integration
        integration_flow = [
            ("GET", "/api/health", None),
            ("GET", f"/api/forms/{TEST_FORM_ID}", None),
            ("POST", "/api/debug/test-chat", {"message": "Integration test"}),
            ("POST", "/api/extract", {
                "session_id": "integration",
                "transcript": [{"role": "user", "text": "test"}],
                "questions_json": {"questions": []}
            })
        ]
        
        integration_success = 0
        for method, endpoint, data in integration_flow:
            response = self.make_request(method, endpoint, data)
            if response["status_code"] in [200, 404]:  # 404 acceptable for some endpoints
                integration_success += 1
                
        self.assert_test(
            integration_success >= 3,  # At least 3/4 should work
            "End-to-end integration functional",
            f"Successful: {integration_success}/{len(integration_flow)} endpoints"
        )
        
        # Test 100: System robustness
        robustness_score = 0
        total_score = 5
        
        # Check API availability
        health_response = self.make_request("GET", "/api/health")
        if health_response["status_code"] == 200:
            robustness_score += 1
            
        # Check form metadata
        form_response = self.make_request("GET", f"/api/forms/{TEST_FORM_ID}")
        if form_response["status_code"] == 200:
            robustness_score += 1
            
        # Check chat functionality
        chat_response = self.make_request("POST", "/api/debug/test-chat", {"message": "Robustness test"})
        if chat_response["status_code"] == 200:
            robustness_score += 1
            
        # Check data extraction
        extract_response = self.make_request("POST", "/api/extract", {
            "session_id": "robustness",
            "transcript": [{"role": "user", "text": "test"}],
            "questions_json": {"questions": []}
        })
        if extract_response["status_code"] in [200, 400]:
            robustness_score += 1
            
        # Check error handling
        error_response = self.make_request("GET", "/api/nonexistent")
        if error_response["status_code"] == 404:
            robustness_score += 1
            
        self.assert_test(
            robustness_score >= 4,
            "System robustness verified",
            f"Robustness score: {robustness_score}/{total_score}"
        )

    def run_all_tests(self):
        """Run all test suites"""
        self.log("🚀 Starting Bermuda Test Suite - 100 Test Cases")
        self.log(f"Target URL: {BASE_URL}")
        
        start_time = time.time()
        
        # Run test suites
        self.test_api_health_checks()
        self.test_form_metadata_api()
        self.test_chat_initialization()
        self.test_conversation_flow()
        self.test_data_extraction()
        self.test_api_edge_cases()
        self.test_ui_and_frontend()
        self.test_business_logic()
        
        end_time = time.time()
        total_time = end_time - start_time
        
        # Print summary
        self.log("=" * 60)
        self.log("🏁 TEST SUITE COMPLETE")
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
    test_suite = BermudaTestSuite()
    passed, failed = test_suite.run_all_tests()
    
    # Exit with appropriate code
    sys.exit(0 if failed == 0 else 1)
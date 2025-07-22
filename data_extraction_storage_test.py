#!/usr/bin/env python3
"""
Data Extraction and Storage Workflows Test Suite
Tests data extraction from conversations and storage functionality
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
import uuid

class DataExtractionStorageTester:
    """Test data extraction and storage workflows"""
    
    def __init__(self):
        self.base_url = "https://bermuda-01.web.app"
        self.api_url = "https://us-central1-bermuda-01.cloudfunctions.net/api"
        self.driver = None
        self.results = []
        self.test_session_id = f"test-session-{uuid.uuid4().hex[:8]}"
        
    def setup_browser(self):
        """Setup browser for testing"""
        chrome_options = Options()
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-web-security")
        chrome_options.add_argument("--window-size=1280,720")
        
        service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service, options=chrome_options)
        self.driver.implicitly_wait(10)
        self.wait = WebDriverWait(self.driver, 30)
        
    def log_result(self, test_name, success, details=""):
        """Log test result"""
        result = {
            "test": test_name,
            "success": success,
            "details": details,
            "timestamp": datetime.now().isoformat(),
            "session_id": self.test_session_id
        }
        self.results.append(result)
        
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status}: {test_name}")
        if details and not success:
            print(f"    Details: {details}")
    
    def test_extract_api_with_correct_format(self):
        """Test extract API with correct JSON object format"""
        print("\n📊 Testing Extract API with Correct Format...")
        
        # Test scenarios with different question types and conversation patterns
        test_scenarios = [
            {
                "name": "Simple text questions",
                "transcript": [
                    {"role": "bot", "message": "What's your favorite food?"},
                    {"role": "user", "message": "I love pizza, especially pepperoni!"},
                    {"role": "bot", "message": "How often do you eat it?"},
                    {"role": "user", "message": "About twice a week"}
                ],
                "questions": [
                    {"text": "What's your favorite food?", "type": "text", "enabled": True},
                    {"text": "How often do you eat it?", "type": "text", "enabled": True}
                ],
                "expected_responses": 2
            },
            {
                "name": "Multiple choice extraction",
                "transcript": [
                    {"role": "bot", "message": "Do you prefer delivery or pickup?"},
                    {"role": "user", "message": "I prefer delivery"},
                    {"role": "bot", "message": "What size pizza do you usually order?"},
                    {"role": "user", "message": "Large size for the family"}
                ],
                "questions": [
                    {"text": "Do you prefer delivery or pickup?", "type": "multiple_choice", "enabled": True,
                     "options": ["Delivery", "Pickup", "Dine-in"]},
                    {"text": "What size pizza do you usually order?", "type": "multiple_choice", "enabled": True,
                     "options": ["Small", "Medium", "Large", "Extra Large"]}
                ],
                "expected_responses": 2
            },
            {
                "name": "Rating and number extraction",
                "transcript": [
                    {"role": "bot", "message": "How would you rate our service from 1 to 10?"},
                    {"role": "user", "message": "I'd give it a 9 out of 10, very satisfied"},
                    {"role": "bot", "message": "How old are you?"},
                    {"role": "user", "message": "I'm 28 years old"}
                ],
                "questions": [
                    {"text": "How would you rate our service?", "type": "rating", "enabled": True},
                    {"text": "How old are you?", "type": "number", "enabled": True}
                ],
                "expected_responses": 2
            },
            {
                "name": "Yes/No extraction",
                "transcript": [
                    {"role": "bot", "message": "Would you recommend us to friends?"},
                    {"role": "user", "message": "Absolutely! Yes, I would definitely recommend you"},
                    {"role": "bot", "message": "Are you a student?"},
                    {"role": "user", "message": "No, I work full-time"}
                ],
                "questions": [
                    {"text": "Would you recommend us to friends?", "type": "yes_no", "enabled": True},
                    {"text": "Are you a student?", "type": "yes_no", "enabled": True}
                ],
                "expected_responses": 2
            },
            {
                "name": "Complex conversation with context",
                "transcript": [
                    {"role": "bot", "message": "Let's talk about your coffee preferences. What's your favorite type?"},
                    {"role": "user", "message": "I really enjoy cappuccinos and lattes"},
                    {"role": "bot", "message": "How many cups do you drink per day?"},
                    {"role": "user", "message": "Usually 2-3 cups, sometimes more on busy days"},
                    {"role": "bot", "message": "Do you add sugar?"},
                    {"role": "user", "message": "No, I prefer it without sugar"},
                    {"role": "bot", "message": "Any favorite coffee shops?"},
                    {"role": "user", "message": "Starbucks and local cafes near my office"}
                ],
                "questions": [
                    {"text": "What's your favorite type of coffee?", "type": "text", "enabled": True},
                    {"text": "How many cups do you drink per day?", "type": "number", "enabled": True},
                    {"text": "Do you add sugar?", "type": "yes_no", "enabled": True},
                    {"text": "Any favorite coffee shops?", "type": "text", "enabled": True}
                ],
                "expected_responses": 4
            }
        ]
        
        for scenario in test_scenarios:
            try:
                # Use correct format - questions_json as object with questions key
                payload = {
                    "session_id": f"{self.test_session_id}-{scenario['name'].replace(' ', '-')}",
                    "transcript": scenario["transcript"],
                    "questions_json": {
                        "questions": scenario["questions"],
                        "demographics": []
                    }
                }
                
                response = requests.post(f"{self.api_url}/extract", 
                                       json=payload, timeout=30)
                
                if response.status_code == 200:
                    try:
                        data = response.json()
                        
                        if "questions" in data:
                            questions_dict = data["questions"]
                            completion_status = data.get("completion_status", "unknown")
                            extraction_notes = data.get("extraction_notes", [])
                            
                            self.log_result(f"Extract {scenario['name']} - API success", True,
                                          f"Extracted {len(questions_dict)} questions, status: {completion_status}")
                            
                            # Check response count
                            if len(questions_dict) >= scenario["expected_responses"]:
                                self.log_result(f"Extract {scenario['name']} - response count", True,
                                              f"Got {len(questions_dict)}/{scenario['expected_responses']} responses")
                            else:
                                self.log_result(f"Extract {scenario['name']} - response count", False,
                                              f"Got only {len(questions_dict)}/{scenario['expected_responses']} responses")
                            
                            # Check response structure (questions dict format)
                            if questions_dict:
                                structure_valid = isinstance(questions_dict, dict) and len(questions_dict) > 0
                                
                                if structure_valid:
                                    self.log_result(f"Extract {scenario['name']} - structure", True,
                                                  "Questions returned in correct dict format")
                                else:
                                    self.log_result(f"Extract {scenario['name']} - structure", False,
                                                  "Questions not in expected dict format")
                                
                                # Check data quality - answers should contain key content from user messages
                                user_messages = [msg["message"].lower() for msg in scenario["transcript"] 
                                               if msg["role"] == "user"]
                                extracted_answers = [str(answer).lower() for answer in questions_dict.values()]
                                
                                # Look for key words from user messages in extracted answers
                                key_words = []
                                for msg in user_messages:
                                    words = [word for word in msg.split() if len(word) > 3]
                                    key_words.extend(words[:2])  # Take first 2 meaningful words from each message
                                
                                found_keywords = []
                                for answer in extracted_answers:
                                    for keyword in key_words:
                                        if keyword in answer:
                                            found_keywords.append(keyword)
                                
                                if found_keywords:
                                    self.log_result(f"Extract {scenario['name']} - content quality", True,
                                                  f"Found keywords: {', '.join(set(found_keywords))}")
                                else:
                                    self.log_result(f"Extract {scenario['name']} - content quality", False,
                                                  "Extracted content doesn't match conversation")
                                
                                # Check type-specific extraction for multiple choice and ratings
                                if scenario["name"] == "Multiple choice extraction":
                                    all_answers = " ".join(extracted_answers)
                                    delivery_found = "delivery" in all_answers
                                    large_found = "large" in all_answers
                                    
                                    if delivery_found and large_found:
                                        self.log_result(f"Extract {scenario['name']} - specific extraction", True,
                                                      "Correctly extracted delivery and large")
                                    else:
                                        self.log_result(f"Extract {scenario['name']} - specific extraction", False,
                                                      f"Missing specific terms: delivery={delivery_found}, large={large_found}")
                                
                                elif scenario["name"] == "Rating and number extraction":
                                    all_answers = " ".join(extracted_answers)
                                    rating_found = "9" in all_answers
                                    age_found = "28" in all_answers
                                    
                                    if rating_found or age_found:
                                        self.log_result(f"Extract {scenario['name']} - number extraction", True,
                                                      f"Found numbers: rating={rating_found}, age={age_found}")
                                    else:
                                        self.log_result(f"Extract {scenario['name']} - number extraction", False,
                                                      "Numbers not properly extracted")
                                
                                elif scenario["name"] == "Yes/No extraction":
                                    all_answers = " ".join(extracted_answers)
                                    yes_found = "yes" in all_answers
                                    no_found = "no" in all_answers
                                    
                                    if yes_found or no_found:
                                        self.log_result(f"Extract {scenario['name']} - yes/no extraction", True,
                                                      f"Found answers: yes={yes_found}, no={no_found}")
                                    else:
                                        self.log_result(f"Extract {scenario['name']} - yes/no extraction", False,
                                                      "Yes/No responses not properly extracted")
                            
                        else:
                            self.log_result(f"Extract {scenario['name']} - response format", False,
                                          "Missing 'questions' field in API response")
                            
                    except json.JSONDecodeError:
                        self.log_result(f"Extract {scenario['name']} - JSON parsing", False,
                                      "Invalid JSON response from API")
                        
                else:
                    self.log_result(f"Extract {scenario['name']} - API response", False,
                                  f"Status: {response.status_code}")
                    
                    # If it's a 400 error, try to get the error message
                    if response.status_code == 400:
                        try:
                            error_data = response.json()
                            self.log_result(f"Extract {scenario['name']} - error details", False,
                                          f"Error: {error_data.get('error', 'Unknown error')}")
                        except:
                            pass
                    
            except requests.exceptions.RequestException as e:
                self.log_result(f"Extract {scenario['name']} - connection", False,
                              f"Request error: {str(e)}")
    
    def test_data_bucketizing_and_transformation(self):
        """Test data bucketizing and transformation features"""
        print("\n🔄 Testing Data Bucketizing and Transformation...")
        
        # Test scenarios that require data transformation
        transformation_scenarios = [
            {
                "name": "Multiple choice bucketizing",
                "transcript": [
                    {"role": "bot", "message": "What's your income level?"},
                    {"role": "user", "message": "I make around $75,000 per year"},
                    {"role": "bot", "message": "What's your education level?"},
                    {"role": "user", "message": "I have a bachelor's degree in engineering"}
                ],
                "questions": [
                    {"text": "What's your income level?", "type": "multiple_choice", "enabled": True,
                     "options": ["Under $30k", "$30k-$50k", "$50k-$75k", "$75k-$100k", "Over $100k"]},
                    {"text": "What's your education level?", "type": "multiple_choice", "enabled": True,
                     "options": ["High School", "Bachelor's", "Master's", "PhD", "Other"]}
                ],
                "expected_buckets": ["$75k-$100k", "Bachelor's"]
            },
            {
                "name": "Age range bucketizing",
                "transcript": [
                    {"role": "bot", "message": "What's your age?"},
                    {"role": "user", "message": "I'm 32 years old"},
                    {"role": "bot", "message": "How many hours do you work per week?"},
                    {"role": "user", "message": "Usually around 45 hours"}
                ],
                "questions": [
                    {"text": "What's your age?", "type": "multiple_choice", "enabled": True,
                     "options": ["18-25", "26-35", "36-45", "46-55", "Over 55"]},
                    {"text": "How many hours do you work per week?", "type": "number", "enabled": True}
                ],
                "expected_transformations": {"age": "26-35", "hours": "45"}
            },
            {
                "name": "Sentiment and satisfaction bucketizing",
                "transcript": [
                    {"role": "bot", "message": "How satisfied are you with our service?"},
                    {"role": "user", "message": "Very satisfied! It's excellent, I'd rate it 9/10"},
                    {"role": "bot", "message": "Any complaints or issues?"},
                    {"role": "user", "message": "No complaints at all, everything was perfect"}
                ],
                "questions": [
                    {"text": "How satisfied are you?", "type": "multiple_choice", "enabled": True,
                     "options": ["Very Dissatisfied", "Dissatisfied", "Neutral", "Satisfied", "Very Satisfied"]},
                    {"text": "Any complaints?", "type": "yes_no", "enabled": True}
                ],
                "expected_sentiment": ["Very Satisfied", "No"]
            }
        ]
        
        for scenario in transformation_scenarios:
            try:
                payload = {
                    "session_id": f"{self.test_session_id}-transform-{scenario['name'].replace(' ', '-')}",
                    "transcript": scenario["transcript"],
                    "questions_json": {
                        "questions": scenario["questions"],
                        "demographics": []
                    }
                }
                
                response = requests.post(f"{self.api_url}/extract", 
                                       json=payload, timeout=30)
                
                if response.status_code == 200:
                    try:
                        data = response.json()
                        questions_dict = data.get("questions", {})
                        
                        if questions_dict:
                            self.log_result(f"Transform {scenario['name']} - extraction success", True,
                                          f"Extracted {len(questions_dict)} questions")
                            
                            # Check for intelligent bucketizing in multiple choice
                            if "bucketizing" in scenario["name"]:
                                answer_texts = [str(answer).lower() for answer in questions_dict.values()]
                                
                                # For income bucketizing
                                if "income" in scenario["name"]:
                                    income_bucketed = any("75k" in answer or "75,000" in answer or "$75" in answer 
                                                        for answer in answer_texts)
                                    education_bucketed = any("bachelor" in answer or "degree" in answer 
                                                           for answer in answer_texts)
                                    
                                    if income_bucketed:
                                        self.log_result(f"Transform {scenario['name']} - income bucketizing", True,
                                                      "Income properly categorized")
                                    else:
                                        self.log_result(f"Transform {scenario['name']} - income bucketizing", False,
                                                      "Income not properly bucketized")
                                    
                                    if education_bucketed:
                                        self.log_result(f"Transform {scenario['name']} - education bucketizing", True,
                                                      "Education properly categorized")
                                    else:
                                        self.log_result(f"Transform {scenario['name']} - education bucketizing", False,
                                                      "Education not properly bucketized")
                                
                                # For age range bucketizing
                                elif "age range" in scenario["name"]:
                                    age_bucketed = any("32" in answer or "26-35" in answer 
                                                     for answer in answer_texts)
                                    hours_extracted = any("45" in answer 
                                                        for answer in answer_texts)
                                    
                                    if age_bucketed:
                                        self.log_result(f"Transform {scenario['name']} - age bucketizing", True,
                                                      "Age properly categorized")
                                    else:
                                        self.log_result(f"Transform {scenario['name']} - age bucketizing", False,
                                                      "Age not properly bucketized")
                                    
                                    if hours_extracted:
                                        self.log_result(f"Transform {scenario['name']} - number extraction", True,
                                                      "Work hours properly extracted")
                                    else:
                                        self.log_result(f"Transform {scenario['name']} - number extraction", False,
                                                      "Work hours not properly extracted")
                                
                                # For sentiment bucketizing
                                elif "sentiment" in scenario["name"]:
                                    positive_sentiment = any("satisfied" in answer or "excellent" in answer or "9" in answer
                                                           for answer in answer_texts)
                                    no_complaints = any("no" in answer or "perfect" in answer 
                                                      for answer in answer_texts)
                                    
                                    if positive_sentiment:
                                        self.log_result(f"Transform {scenario['name']} - satisfaction detection", True,
                                                      "Positive sentiment detected")
                                    else:
                                        self.log_result(f"Transform {scenario['name']} - satisfaction detection", False,
                                                      "Sentiment not properly detected")
                                    
                                    if no_complaints:
                                        self.log_result(f"Transform {scenario['name']} - complaint detection", True,
                                                      "No complaints properly detected")
                                    else:
                                        self.log_result(f"Transform {scenario['name']} - complaint detection", False,
                                                      "Complaint response not properly detected")
                        else:
                            self.log_result(f"Transform {scenario['name']} - no questions", False,
                                          "No questions extracted")
                            
                    except json.JSONDecodeError:
                        self.log_result(f"Transform {scenario['name']} - JSON error", False,
                                      "Invalid JSON response")
                        
                else:
                    self.log_result(f"Transform {scenario['name']} - API error", False,
                                  f"Status: {response.status_code}")
                    
            except requests.exceptions.RequestException as e:
                self.log_result(f"Transform {scenario['name']} - connection error", False,
                              f"Error: {str(e)}")
    
    def test_edge_cases_and_error_handling(self):
        """Test edge cases in data extraction"""
        print("\n⚠️  Testing Edge Cases and Error Handling...")
        
        edge_cases = [
            {
                "name": "Empty transcript",
                "payload": {
                    "session_id": f"{self.test_session_id}-empty",
                    "transcript": [],
                    "questions_json": {
                        "questions": [{"text": "Test question", "type": "text", "enabled": True}],
                        "demographics": []
                    }
                },
                "expected_behavior": "Should handle empty transcript gracefully"
            },
            {
                "name": "Mismatched questions and transcript",
                "payload": {
                    "session_id": f"{self.test_session_id}-mismatch",
                    "transcript": [
                        {"role": "bot", "message": "What's your favorite color?"},
                        {"role": "user", "message": "Blue"}
                    ],
                    "questions_json": {
                        "questions": [
                            {"text": "What's your favorite food?", "type": "text", "enabled": True},
                            {"text": "How old are you?", "type": "number", "enabled": True}
                        ],
                        "demographics": []
                    }
                },
                "expected_behavior": "Should handle mismatched content"
            },
            {
                "name": "Very long conversation",
                "payload": {
                    "session_id": f"{self.test_session_id}-long",
                    "transcript": [
                        msg for i in range(20) 
                        for msg in [
                            {"role": "bot", "message": f"Question {i}?"},
                            {"role": "user", "message": f"Answer {i} with some detailed response"}
                        ]
                    ],
                    "questions_json": {
                        "questions": [
                            {"text": f"Question {i}?", "type": "text", "enabled": True}
                            for i in range(20)
                        ],
                        "demographics": []
                    }
                },
                "expected_behavior": "Should handle long conversations"
            },
            {
                "name": "Invalid question types",
                "payload": {
                    "session_id": f"{self.test_session_id}-invalid",
                    "transcript": [
                        {"role": "bot", "message": "Test question?"},
                        {"role": "user", "message": "Test answer"}
                    ],
                    "questions_json": {
                        "questions": [
                            {"text": "Test question", "type": "invalid_type", "enabled": True}
                        ],
                        "demographics": []
                    }
                },
                "expected_behavior": "Should handle invalid question types"
            }
        ]
        
        # Flatten the long conversation payload
        long_case = edge_cases[2]
        flattened_transcript = []
        for pair in long_case["payload"]["transcript"]:
            flattened_transcript.extend(pair)
        long_case["payload"]["transcript"] = flattened_transcript
        
        for case in edge_cases:
            try:
                response = requests.post(f"{self.api_url}/extract", 
                                       json=case["payload"], timeout=45)
                
                # For edge cases, we mainly care that the API doesn't crash
                if response.status_code in [200, 400]:
                    try:
                        data = response.json()
                        self.log_result(f"Edge case - {case['name']}", True,
                                      f"Status: {response.status_code}, handled gracefully")
                        
                        # For successful responses, check if we got reasonable data
                        if response.status_code == 200 and "questions" in data:
                            questions_dict = data["questions"]
                            self.log_result(f"Edge case - {case['name']} data", True,
                                          f"Returned {len(questions_dict)} questions")
                            
                    except json.JSONDecodeError:
                        self.log_result(f"Edge case - {case['name']}", False,
                                      "Invalid JSON response")
                        
                elif response.status_code == 500:
                    self.log_result(f"Edge case - {case['name']}", False,
                                  "Server error - API crashed")
                else:
                    self.log_result(f"Edge case - {case['name']}", True,
                                  f"Status: {response.status_code} (handled)")
                    
            except requests.exceptions.RequestException as e:
                self.log_result(f"Edge case - {case['name']}", False,
                              f"Request error: {str(e)}")
    
    def run_data_extraction_storage_tests(self):
        """Run all data extraction and storage tests"""
        print("📊 Data Extraction and Storage Test Suite")
        print("=" * 60)
        
        # Don't need browser for API-only testing
        # self.setup_browser()
        
        try:
            # Phase 1: Extract API with correct format
            self.test_extract_api_with_correct_format()
            
            # Phase 2: Data bucketizing and transformation
            self.test_data_bucketizing_and_transformation()
            
            # Phase 3: Edge cases and error handling
            self.test_edge_cases_and_error_handling()
            
        finally:
            self.cleanup()
    
    def cleanup(self):
        """Clean up and generate summary"""
        if self.driver:
            self.driver.quit()
        
        self.generate_summary()
    
    def generate_summary(self):
        """Generate data extraction and storage summary"""
        total_tests = len(self.results)
        passed_tests = len([r for r in self.results if r["success"]])
        failed_tests = total_tests - passed_tests
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        print("\n" + "=" * 60)
        print("🏁 DATA EXTRACTION AND STORAGE TEST SUMMARY")
        print("=" * 60)
        print(f"✅ Passed: {passed_tests}")
        print(f"❌ Failed: {failed_tests}")
        print(f"📊 Success Rate: {success_rate:.1f}%")
        print(f"🔗 Test Session ID: {self.test_session_id}")
        
        if failed_tests > 0:
            print("\n🔍 FAILED TESTS:")
            for result in self.results:
                if not result["success"]:
                    print(f"   ❌ {result['test']}: {result['details']}")
        
        print("=" * 60)
        
        # Data extraction assessment
        if success_rate >= 90:
            print("🔥 DATA EXTRACTION STATUS: EXCELLENT - Production ready!")
        elif success_rate >= 75:
            print("✅ DATA EXTRACTION STATUS: GOOD - Minor issues")
        elif success_rate >= 60:
            print("⚠️  DATA EXTRACTION STATUS: NEEDS WORK - Several problems")
        else:
            print("❌ DATA EXTRACTION STATUS: CRITICAL - Major failures")
        
        # Save detailed results
        with open('data_extraction_storage_results.json', 'w') as f:
            json.dump({
                "results": self.results,
                "summary": {
                    "total_tests": total_tests,
                    "passed_tests": passed_tests,
                    "failed_tests": failed_tests,
                    "success_rate": success_rate,
                    "session_id": self.test_session_id,
                    "test_duration": datetime.now().isoformat()
                }
            }, f, indent=2)

if __name__ == "__main__":
    tester = DataExtractionStorageTester()
    tester.run_data_extraction_storage_tests()